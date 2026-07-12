from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from app1.models import Admin
from .inventory_services import adjust_stock, receive_purchase_order, record_movement
from .inventory_forms import InventoryForm, PurchaseOrderItemForm
from .models import Inventory, PurchaseOrder, PurchaseOrderItem, PurchasePayment, Staff, StockMovement, Vendor


class StockServiceTests(TestCase):
    def setUp(self):
        self.item = Inventory.objects.create(item_name='Rice', quantity=10, min_quantity=3, unit='kg')

    def test_outgoing_movement_updates_stock_and_audit(self):
        movement = record_movement(item=self.item, movement_type=StockMovement.KITCHEN_ISSUE, quantity=4, created_by='store')
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, Decimal('6'))
        self.assertEqual(movement.balance_after, Decimal('6'))
        self.assertEqual(movement.quantity_out, Decimal('4'))

    def test_movement_cannot_make_stock_negative(self):
        with self.assertRaises(ValidationError):
            record_movement(item=self.item, movement_type=StockMovement.WASTAGE, quantity=11)
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, Decimal('10'))
        self.assertFalse(StockMovement.objects.exists())

    def test_adjustment_is_audited(self):
        adjust_stock(item=self.item, new_quantity=7, created_by='admin')
        movement = StockMovement.objects.get()
        self.assertEqual(movement.movement_type, StockMovement.ADJUSTMENT)
        self.assertEqual(movement.quantity_out, Decimal('3'))

    def test_purchase_receipt_is_idempotent(self):
        vendor = Vendor.objects.create(name='Foods Ltd')
        po = PurchaseOrder.objects.create(number='PO-1', vendor=vendor)
        PurchaseOrderItem.objects.create(purchase_order=po, inventory_item=self.item, quantity_ordered=5, quantity_received=5, unit='kg', unit_cost=20)
        self.assertTrue(receive_purchase_order(po, 'store'))
        self.assertFalse(receive_purchase_order(po, 'store'))
        self.item.refresh_from_db(); po.refresh_from_db()
        self.assertEqual(self.item.quantity, Decimal('15'))
        self.assertEqual(po.status, 'received')
        self.assertEqual(StockMovement.objects.count(), 1)


class InventoryViewTests(TestCase):
    def setUp(self):
        self.admin = Admin.objects.create(username='owner', password='secret', phone_number=111, email='owner@example.com')
        self.inventory_staff = Staff.objects.create(username='store', password='secret', phone_number=222, email='store@example.com', role='inventory')
        self.chef = Staff.objects.create(username='chef', password='secret', phone_number=333, email='chef@example.com', role='chef')

    def login_as(self, user, kind='staff'):
        session = self.client.session; session['user_id'] = user.pk; session['user_type'] = kind; session.save()

    def test_inventory_staff_can_open_dashboard(self):
        self.login_as(self.inventory_staff)
        self.assertEqual(self.client.get(reverse('inventory_dashboard')).status_code, 200)

    def test_chef_cannot_open_inventory(self):
        self.login_as(self.chef)
        response = self.client.get(reverse('inventory_list'))
        self.assertRedirects(response, reverse('staff_dashboard'))

    def test_creating_opening_stock_creates_audit(self):
        self.login_as(self.admin, 'admin')
        response = self.client.post(reverse('inventory_add'), {'item_name': 'Tomato', 'quantity': '8', 'min_quantity': '2', 'unit': 'kg'})
        self.assertRedirects(response, reverse('inventory_list'))
        item = Inventory.objects.get(item_name='Tomato')
        movement = item.movements.get()
        self.assertEqual(movement.movement_type, StockMovement.OPENING_STOCK)
        self.assertEqual(movement.balance_after, Decimal('8'))

    def test_low_stock_filter(self):
        Inventory.objects.create(item_name='Salt', quantity=1, min_quantity=2, unit='kg')
        Inventory.objects.create(item_name='Oil', quantity=10, min_quantity=2, unit='liter')
        self.login_as(self.inventory_staff)
        response = self.client.get(reverse('inventory_list') + '?low=1')
        self.assertContains(response, 'Salt')
        self.assertNotContains(response, 'Oil')

    def test_empty_daily_report_renders(self):
        self.login_as(self.admin, 'admin')
        response = self.client.get(reverse('daily_inventory_report'), {'date': date.today().isoformat()})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gross difference')

    def test_purchase_screen_creates_multiple_linked_items(self):
        vendor = Vendor.objects.create(name='Test Supplier')
        oil = Inventory.objects.create(item_name='Test Oil', quantity=0, min_quantity=2, unit='liter')
        rice = Inventory.objects.create(item_name='Test Rice', quantity=0, min_quantity=5, unit='kg')
        self.login_as(self.admin, 'admin')
        payload = {
            'number': 'PO-MULTI-1', 'vendor': vendor.pk, 'purchase_date': date.today(),
            'status': 'ordered', 'amount_paid': '0', 'payment_method': '', 'payment_date': '', 'notes': '',
            'items-TOTAL_FORMS': '3', 'items-INITIAL_FORMS': '0', 'items-MIN_NUM_FORMS': '1', 'items-MAX_NUM_FORMS': '1000',
            'items-0-inventory_item': oil.pk, 'items-0-quantity_ordered': '20', 'items-0-quantity_received': '20', 'items-0-unit': 'liter', 'items-0-unit_cost': '110',
            'items-1-inventory_item': rice.pk, 'items-1-quantity_ordered': '25', 'items-1-quantity_received': '25', 'items-1-unit': 'kg', 'items-1-unit_cost': '55',
            'items-2-inventory_item': '', 'items-2-quantity_ordered': '', 'items-2-quantity_received': '0', 'items-2-unit': '', 'items-2-unit_cost': '',
        }
        response = self.client.post(reverse('purchase_order_add'), payload)
        po = PurchaseOrder.objects.get(number='PO-MULTI-1')
        self.assertRedirects(response, reverse('purchase_order_detail', args=[po.pk]))
        self.assertEqual(po.items.count(), 2)
        self.assertEqual(oil.quantity, Decimal('0'))
        receive_purchase_order(po, 'owner')
        oil.refresh_from_db(); rice.refresh_from_db()
        self.assertEqual(oil.quantity, Decimal('20'))
        self.assertEqual(rice.quantity, Decimal('25'))

    def test_units_are_dropdowns_and_stock_choice_is_name_only(self):
        item = Inventory.objects.create(item_name='Fresh Tomato', quantity=12, min_quantity=2, unit='kg')
        inventory_form = InventoryForm()
        self.assertIn(('kg', 'Kilograms (kg)'), list(inventory_form.fields['unit'].choices))
        line_form = PurchaseOrderItemForm()
        choices = dict(line_form.fields['inventory_item'].choices)
        self.assertEqual(choices[item.pk], 'Fresh Tomato')
        self.assertNotIn('12', choices[item.pk])

    def test_multiple_payments_create_payable_then_vendor_advance(self):
        vendor = Vendor.objects.create(name='Accounts Supplier')
        item = Inventory.objects.create(item_name='Accounts Rice', quantity=0, min_quantity=2, unit='kg')
        po = PurchaseOrder.objects.create(number='PO-ACCOUNTS-1', vendor=vendor)
        PurchaseOrderItem.objects.create(purchase_order=po, inventory_item=item, quantity_ordered=10, unit='kg', unit_cost=100)
        self.login_as(self.admin, 'admin')
        first = self.client.post(reverse('purchase_payment_add', args=[po.pk]), {
            'payment_date': date.today(), 'amount': '600', 'payment_method': 'cash', 'reference_number': 'PAY-1', 'notes': ''})
        self.assertRedirects(first, reverse('purchase_order_detail', args=[po.pk]))
        self.assertEqual(po.total_paid, Decimal('600'))
        self.assertEqual(po.payable_amount, Decimal('400'))
        second = self.client.post(reverse('purchase_payment_add', args=[po.pk]), {
            'payment_date': date.today(), 'amount': '450', 'payment_method': 'upi', 'reference_number': 'PAY-2', 'notes': ''})
        self.assertRedirects(second, reverse('purchase_order_detail', args=[po.pk]))
        self.assertEqual(po.total_paid, Decimal('1050'))
        self.assertEqual(po.advance_amount, Decimal('50'))
        ledger = self.client.get(reverse('vendor_ledger', args=[vendor.pk]))
        self.assertContains(ledger, 'PAY-1')
        self.assertContains(ledger, 'PAY-2')
        dashboard = self.client.get(reverse('inventory_dashboard'))
        self.assertContains(dashboard, 'Vendor advances')

    def test_quick_create_stock_item_returns_item_and_audits_opening_stock(self):
        self.login_as(self.admin, 'admin')
        response = self.client.post(reverse('inventory_quick_create'), {
            'item_name': 'Idly Ravva', 'quantity': '2', 'min_quantity': '5', 'unit': 'kg',
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertTrue(payload['ok'])
        self.assertEqual(payload['item']['name'], 'Idly Ravva')
        self.assertEqual(payload['item']['unit'], 'kg')
        item = Inventory.objects.get(item_name='Idly Ravva')
        self.assertEqual(item.quantity, Decimal('2'))
        self.assertEqual(item.movements.get().movement_type, StockMovement.OPENING_STOCK)

    def test_purchase_form_has_search_and_inline_create_controls(self):
        Vendor.objects.create(name='UX Supplier')
        Inventory.objects.create(item_name='Existing Item', quantity=0, min_quantity=1, unit='kg')
        self.login_as(self.admin, 'admin')
        response = self.client.get(reverse('purchase_order_add'))
        self.assertContains(response, "select2({placeholder: 'Search stock item'")
        self.assertContains(response, 'aria-label="Create new stock item"')
        self.assertContains(response, 'Create and select')
        self.assertContains(response, 'Add another item')
        self.assertContains(response, 'emptyPurchaseLine')
