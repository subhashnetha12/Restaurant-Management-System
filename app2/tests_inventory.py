from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from app1.models import Admin
from .inventory_services import adjust_stock, receive_purchase_order, record_movement
from .models import Inventory, PurchaseOrder, PurchaseOrderItem, Staff, StockMovement, Vendor


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
