from datetime import datetime
from decimal import Decimal

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import DecimalField, F, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from app2.inventory_forms import InventoryForm, MovementForm, PurchaseOrderForm, PurchaseOrderItemForm, VendorForm
from app2.inventory_services import adjust_stock, receive_purchase_order, record_movement
from app2.models import Inventory, Orders, Payments, PurchaseOrder, PurchaseOrderItem, StockMovement, Vendor
from .views import get_logged_in_user


def _access(request, read_only=False):
    user, user_type = get_logged_in_user(request)
    if not user:
        return None, None
    allowed = user_type == 'admin' or (user_type == 'staff' and user.role.lower() == 'inventory')
    if read_only and user_type == 'staff' and user.role.lower() == 'receptionist':
        allowed = True
    return (user, user_type) if allowed else (None, 'forbidden')


def _guard(request, read_only=False):
    user, kind = _access(request, read_only)
    if not user:
        messages.error(request, 'You do not have permission to access inventory.')
        return None, redirect('signin' if kind is None else 'staff_dashboard')
    return (user, kind), None


def _context(user, kind, **kwargs):
    return {'data': user, 'user_type': kind, 'base_template': 'Rest-Admin/base.html' if kind == 'admin' else 'Staff/base.html', **kwargs}


def inventory_dashboard(request):
    auth, response = _guard(request, read_only=True)
    if response: return response
    user, kind = auth
    stock = Inventory.objects.all()
    return render(request, 'Inventory/dashboard.html', _context(user, kind,
        item_count=stock.count(), low_stock_count=stock.filter(quantity__lte=F('min_quantity')).count(),
        active_vendor_count=Vendor.objects.filter(is_active=True).count(), open_po_count=PurchaseOrder.objects.exclude(status__in=['received', 'cancelled']).count(),
        recent_movements=StockMovement.objects.select_related('inventory_item')[:8]))


def inventory_list(request):
    auth, response = _guard(request, read_only=True)
    if response: return response
    user, kind = auth
    items = Inventory.objects.all()
    low_only = request.GET.get('low') == '1'
    if low_only: items = items.filter(quantity__lte=F('min_quantity'))
    return render(request, 'Inventory/inventory_list.html', _context(user, kind, items=items, low_only=low_only, can_edit=kind == 'admin' or user.role.lower() == 'inventory'))


def inventory_edit(request, pk=None):
    auth, response = _guard(request)
    if response: return response
    user, kind = auth
    item = get_object_or_404(Inventory, pk=pk) if pk else Inventory()
    old_quantity = item.quantity if item.pk else Decimal('0')
    form = InventoryForm(request.POST or None, instance=item)
    if request.method == 'POST' and form.is_valid():
        desired_quantity = form.cleaned_data['quantity']
        saved = form.save(commit=False)
        saved.quantity = old_quantity
        saved.save()
        if pk:
            adjust_stock(item=saved, new_quantity=desired_quantity, created_by=user.username, notes='Quantity changed from inventory edit screen')
        elif desired_quantity:
            record_movement(item=saved, movement_type=StockMovement.OPENING_STOCK, quantity=desired_quantity, created_by=user.username, reference_type='inventory_creation')
        messages.success(request, 'Stock item saved successfully.')
        return redirect('inventory_list')
    return render(request, 'Inventory/form.html', _context(user, kind, form=form, title='Edit stock item' if pk else 'Add stock item', back_url='inventory_list'))


def inventory_delete(request, pk):
    auth, response = _guard(request)
    if response: return response
    item = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        if item.movements.exists() or item.purchase_items.exists():
            messages.error(request, 'This item has stock history and cannot be deleted.')
        else:
            item.delete(); messages.success(request, 'Stock item deleted.')
        return redirect('inventory_list')
    user, kind = auth
    return render(request, 'Inventory/confirm_delete.html', _context(user, kind, object=item, back_url='inventory_list'))


def vendor_list(request):
    auth, response = _guard(request)
    if response: return response
    user, kind = auth
    return render(request, 'Inventory/vendor_list.html', _context(user, kind, vendors=Vendor.objects.all()))


def vendor_edit(request, pk=None):
    auth, response = _guard(request)
    if response: return response
    user, kind = auth; vendor = get_object_or_404(Vendor, pk=pk) if pk else None
    form = VendorForm(request.POST or None, instance=vendor)
    if request.method == 'POST' and form.is_valid():
        form.save(); messages.success(request, 'Vendor saved successfully.'); return redirect('vendor_list')
    return render(request, 'Inventory/form.html', _context(user, kind, form=form, title='Edit vendor' if pk else 'Add vendor', back_url='vendor_list'))


def vendor_delete(request, pk):
    auth, response = _guard(request)
    if response: return response
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        if vendor.purchase_orders.exists():
            vendor.is_active = False; vendor.save(update_fields=['is_active']); messages.info(request, 'Vendor has purchase history and was deactivated.')
        else: vendor.delete(); messages.success(request, 'Vendor deleted.')
        return redirect('vendor_list')
    user, kind = auth
    return render(request, 'Inventory/confirm_delete.html', _context(user, kind, object=vendor, back_url='vendor_list'))


def purchase_order_list(request):
    auth, response = _guard(request)
    if response: return response
    user, kind = auth
    return render(request, 'Inventory/po_list.html', _context(user, kind, purchase_orders=PurchaseOrder.objects.select_related('vendor').prefetch_related('items')))


def purchase_order_edit(request, pk=None):
    auth, response = _guard(request)
    if response: return response
    user, kind = auth; po = get_object_or_404(PurchaseOrder, pk=pk) if pk else None
    form = PurchaseOrderForm(request.POST or None, instance=po, initial={'number': f"PO-{timezone.now():%Y%m%d-%H%M%S}"} if not po else None)
    if request.method == 'POST' and form.is_valid():
        po = form.save(commit=False); po.created_by = po.created_by or user.username; po.save()
        messages.success(request, 'Purchase order saved. Add its stock items below.'); return redirect('purchase_order_detail', pk=po.pk)
    return render(request, 'Inventory/form.html', _context(user, kind, form=form, title='Edit purchase order' if pk else 'Create purchase order', back_url='purchase_order_list'))


def purchase_order_detail(request, pk):
    auth, response = _guard(request)
    if response: return response
    user, kind = auth; po = get_object_or_404(PurchaseOrder.objects.prefetch_related('items__inventory_item'), pk=pk)
    form = PurchaseOrderItemForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        line = form.save(commit=False); line.purchase_order = po
        try: line.save()
        except Exception:
            form.add_error('inventory_item', 'This stock item is already on the purchase order.')
        else:
            messages.success(request, 'Purchase item added.'); return redirect('purchase_order_detail', pk=pk)
    return render(request, 'Inventory/po_detail.html', _context(user, kind, purchase_order=po, form=form))


def purchase_order_item_edit(request, pk):
    auth, response = _guard(request)
    if response: return response
    user, kind = auth
    line = get_object_or_404(PurchaseOrderItem, pk=pk)
    form = PurchaseOrderItemForm(request.POST or None, instance=line)
    if request.method == 'POST' and form.is_valid():
        form.save(); messages.success(request, 'Purchase item updated.'); return redirect('purchase_order_detail', pk=line.purchase_order_id)
    return render(request, 'Inventory/form.html', _context(user, kind, form=form, title='Update purchase item', back_url='purchase_order_list'))


def purchase_order_receive(request, pk):
    auth, response = _guard(request)
    if response: return response
    user, kind = auth; po = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        try:
            changed = receive_purchase_order(po, user.username)
            messages.success(request, 'Received quantities posted to stock.' if changed else 'No new received quantity to post.')
        except ValidationError as exc: messages.error(request, '; '.join(exc.messages))
    return redirect('purchase_order_detail', pk=pk)


def movement_list(request):
    auth, response = _guard(request)
    if response: return response
    user, kind = auth; movements = StockMovement.objects.select_related('inventory_item')
    if request.GET.get('item'): movements = movements.filter(inventory_item_id=request.GET['item'])
    return render(request, 'Inventory/movement_list.html', _context(user, kind, movements=movements, items=Inventory.objects.all()))


def movement_create(request, item_pk=None):
    auth, response = _guard(request)
    if response: return response
    user, kind = auth; item = get_object_or_404(Inventory, pk=item_pk) if item_pk else None
    form = MovementForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        item = item or get_object_or_404(Inventory, pk=request.POST.get('inventory_item'))
        try:
            record_movement(item=item, created_by=user.username, reference_type='manual_entry', **form.cleaned_data)
            messages.success(request, 'Stock movement recorded.'); return redirect('movement_list')
        except ValidationError as exc: form.add_error('quantity', '; '.join(exc.messages))
    return render(request, 'Inventory/movement_form.html', _context(user, kind, form=form, item=item, items=Inventory.objects.all()))


def daily_inventory_report(request):
    auth, response = _guard(request)
    if response: return response
    user, kind = auth
    try: selected = datetime.strptime(request.GET.get('date', ''), '%Y-%m-%d').date()
    except ValueError: selected = timezone.localdate()
    movements = StockMovement.objects.filter(movement_at__date=selected).select_related('inventory_item')
    rows = []
    for item in Inventory.objects.all():
        day_moves = movements.filter(inventory_item=item)
        purchased = day_moves.filter(movement_type=StockMovement.PURCHASE_RECEIVED).aggregate(v=Coalesce(Sum('quantity_in'), Decimal('0')))['v']
        issued = day_moves.filter(movement_type=StockMovement.KITCHEN_ISSUE).aggregate(v=Coalesce(Sum('quantity_out'), Decimal('0')))['v']
        wastage = day_moves.filter(movement_type=StockMovement.WASTAGE).aggregate(v=Coalesce(Sum('quantity_out'), Decimal('0')))['v']
        net = day_moves.aggregate(v=Coalesce(Sum(F('quantity_in') - F('quantity_out')), Decimal('0'), output_field=DecimalField()))['v']
        closing = day_moves.order_by('-movement_at', '-id').values_list('balance_after', flat=True).first()
        if closing is None: closing = item.quantity
        if day_moves.exists(): rows.append({'item': item, 'opening': closing - net, 'purchased': purchased, 'issued': issued, 'wastage': wastage, 'closing': closing})
    purchase_paid = PurchaseOrder.objects.filter(payment_date=selected).aggregate(v=Coalesce(Sum('amount_paid'), Decimal('0')))['v']
    sale_value = Payments.objects.filter(payment_status='Completed', order_no__in=Orders.objects.filter(order_date__date=selected).values('order_no')).aggregate(v=Coalesce(Sum('total_amount'), Decimal('0')))['v']
    totals = {'purchase_paid': purchase_paid, 'sale_value': sale_value, 'difference': sale_value - purchase_paid,
              'issued': sum((r['issued'] for r in rows), Decimal('0')), 'wastage': sum((r['wastage'] for r in rows), Decimal('0'))}
    return render(request, 'Inventory/daily_report.html', _context(user, kind, selected_date=selected, rows=rows, totals=totals))
