from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import Inventory, PurchaseOrder, PurchaseOrderItem, StockMovement


@transaction.atomic
def record_movement(*, item, movement_type, quantity, created_by='', notes='', reference_type='', reference_number='', purchase_cost_amount=0, sale_value=0, movement_at=None, vendor=None, purchase_order=None):
    quantity = Decimal(str(quantity))
    if quantity <= 0:
        raise ValidationError('Movement quantity must be greater than zero.')
    item = Inventory.objects.select_for_update().get(pk=item.pk)
    if movement_type == StockMovement.RETURN_VENDOR:
        if not vendor:
            raise ValidationError('Select the vendor receiving this return.')
        purchase_cost_amount = Decimal(str(purchase_cost_amount or 0))
        if purchase_cost_amount <= 0:
            raise ValidationError('Enter the return value so the vendor ledger can be credited.')
        if purchase_order:
            if purchase_order.vendor_id != vendor.pk:
                raise ValidationError('The selected purchase order belongs to a different vendor.')
            if not purchase_order.items.filter(inventory_item=item).exists():
                raise ValidationError('This stock item is not part of the selected purchase order.')
    incoming = movement_type in (StockMovement.PURCHASE_RECEIVED, StockMovement.OPENING_STOCK)
    if movement_type == StockMovement.ADJUSTMENT:
        raise ValidationError('Use adjust_stock for stock adjustments.')
    new_balance = item.quantity + quantity if incoming else item.quantity - quantity
    if new_balance < 0:
        raise ValidationError(f'Insufficient stock. Available: {item.quantity} {item.unit}.')
    item.quantity = new_balance
    item.save(update_fields=['quantity', 'last_updated'])
    return StockMovement.objects.create(
        inventory_item=item, movement_at=movement_at or timezone.now(), movement_type=movement_type,
        quantity_in=quantity if incoming else 0, quantity_out=0 if incoming else quantity,
        unit=item.unit, reference_type=reference_type, reference_number=reference_number,
        purchase_cost_amount=purchase_cost_amount or 0, sale_value=sale_value or 0,
        vendor=vendor, purchase_order=purchase_order,
        created_by=created_by, notes=notes, balance_after=new_balance,
    )


@transaction.atomic
def adjust_stock(*, item, new_quantity, created_by='', notes=''):
    item = Inventory.objects.select_for_update().get(pk=item.pk)
    new_quantity = Decimal(str(new_quantity))
    if new_quantity < 0:
        raise ValidationError('Stock quantity cannot be negative.')
    difference = new_quantity - item.quantity
    if difference == 0:
        return None
    item.quantity = new_quantity
    item.save(update_fields=['quantity', 'last_updated'])
    return StockMovement.objects.create(
        inventory_item=item, movement_type=StockMovement.ADJUSTMENT,
        quantity_in=max(difference, 0), quantity_out=max(-difference, 0), unit=item.unit,
        reference_type='manual_adjustment', created_by=created_by, notes=notes,
        balance_after=new_quantity,
    )


@transaction.atomic
def receive_purchase_order(purchase_order, created_by=''):
    po = PurchaseOrder.objects.select_for_update().get(pk=purchase_order.pk)
    if po.status == 'cancelled':
        raise ValidationError('A cancelled purchase order cannot be received.')
    received_any = False
    for line in PurchaseOrderItem.objects.select_for_update().filter(purchase_order=po).select_related('inventory_item'):
        delta = line.quantity_received - line.quantity_posted
        if delta < 0:
            raise ValidationError('Received quantity cannot be lower than quantity already posted.')
        if delta:
            record_movement(
                item=line.inventory_item, movement_type=StockMovement.PURCHASE_RECEIVED, quantity=delta,
                created_by=created_by, reference_type='purchase_order', reference_number=po.number,
                purchase_cost_amount=delta * line.unit_cost,
            )
            line.quantity_posted = line.quantity_received
            line.save(update_fields=['quantity_posted'])
            received_any = True
    if not po.items.exists():
        raise ValidationError('Add at least one item before receiving this purchase order.')
    if all(line.quantity_posted >= line.quantity_ordered for line in po.items.all()):
        po.status = 'received'
    elif received_any and po.status == 'draft':
        po.status = 'ordered'
    po.save(update_fields=['status', 'updated_at'])
    return received_any
