from django.db import models

# Create your models here.
from django.db import models
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.contrib.auth.hashers import make_password, check_password


from django.db import models
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone

INVENTORY_UNIT_CHOICES = [
    ('kg', 'Kilograms (kg)'), ('g', 'Grams (g)'), ('liter', 'Litres (L)'),
    ('ml', 'Millilitres (ml)'), ('piece', 'Pieces'), ('packet', 'Packets'),
    ('box', 'Boxes'), ('bottle', 'Bottles'), ('can', 'Cans'), ('dozen', 'Dozen'),
]
import qrcode
from io import BytesIO


class Staff(models.Model):
    ROLE_CHOICES = [        
        ('manager', 'Manager'),
        ('receptionist', 'Receptionist'),
        ('chef', 'Chef'),
        ('waiter', 'Waiter'),
        ('cashier', 'Cashier'),     
        ('inventory', 'Inventory')   
    ]
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    phone_number = models.BigIntegerField()
    email = models.EmailField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):               
        db = kwargs.get('using', 'default')
        if self.pk:         
            original = Staff.objects.using(db).get(pk=self.pk)            
            if original.password != self.password:
                self.password = make_password(self.password)
        else:            
            self.password = make_password(self.password)        
        super(Staff, self).save(*args, **kwargs)


    def __str__(self):
        return self.username
    
    
class Customer(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    phone_number = models.BigIntegerField()
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    date_joined = models.DateTimeField()


    def save(self, *args, **kwargs):        
        if self.pk:
            original = Customer.objects.get(pk=self.pk)            
            if original.password != self.password:
                self.password = make_password(self.password)
        else:            
            self.password = make_password(self.password)

        super(Customer, self).save(*args, **kwargs)

    def __str__(self):
        return self.username

class CustomerAddress(models.Model):
    username = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    def __str__(self):
        return self.username


class Categories(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='Categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)
    code = models.IntegerField(null=True, default=None)
    def __str__(self):
        return self.name

class MenuItems(models.Model):
    category = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField()
    available = models.BooleanField(default=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='MenuItems/', blank=True, null=True)
    type = models.CharField(max_length=50, choices=[('Veg', 'Veg'), ('Non-Veg', 'Non-Veg')])
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    gst = models.CharField(max_length=150)
    gst_type = models.CharField(max_length=100)
    hsn_code = models.CharField(max_length=150)

    def __str__(self):
        return self.name
    
class Menuitems_details(models.Model):
    name = models.CharField(max_length=255)
    size = models.CharField(max_length=150)
    table_price = models.DecimalField(max_digits=10, decimal_places=2)
    takeaway_price = models.DecimalField(max_digits=10, decimal_places=2)
    swiggy_price = models.DecimalField(max_digits=10, decimal_places=2)
    zomoto_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Table_list(models.Model):
    table_no = models.CharField(max_length=150)
    capacity = models.BigIntegerField()
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='Table_list/', blank=True, null=True)
    status = models.CharField(max_length=50, choices=[('Available', 'Available'), ('Occupied', 'Occupied')], default='Available')
    occupied_order_no = models.CharField(max_length=40, null=True , blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)  
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.table_no


class Orders(models.Model):
    username = models.CharField(max_length=100)
    order_no = models.CharField(max_length=40)
    order_type = models.CharField(max_length=40)
    order_date = models.DateTimeField()
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'),('Served', 'Served'),('Ready for Pickup', 'Ready for Pickup'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')])
    table_no = models.CharField(max_length=50,null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100,blank=True, null=True)
    postal_code = models.CharField(max_length=20,blank=True, null=True)
    def __str__(self):
        return self.order_no
        

class OrderItems(models.Model):
    order_no = models.CharField(max_length=40)
    menu_item = models.CharField(max_length=100)
    size = models.CharField(max_length=150)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return self.order_no


class KOT(models.Model):
    kot_no = models.CharField(max_length=40)
    order_no = models.CharField(max_length=40)  
    order_type = models.CharField(max_length=40)
    table_no = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Preparing', 'Preparing'), ('Ready', 'Ready'), ('Served', 'Served'),('Cancelled', 'Cancelled')], default='Pending')
    created_at = models.DateTimeField()
    served_by = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"KOT for {self.order_no} - {self.status}"

class KOTItems(models.Model):
    kot_no = models.CharField(max_length=40)  
    order_no = models.CharField(max_length=40)  
    order_item = models.CharField(max_length=100) 
    size = models.CharField(max_length=150)
    quantity = models.PositiveIntegerField(default=1) 

    def __str__(self):
        return f"{self.order_no} ({self.kot_no})"        

class Payments(models.Model):
    order_no = models.CharField(max_length=40)
    payment_method = models.CharField(max_length=50)
    payment_status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Failed', 'Failed')])
    transaction_id = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return self.order_no
    
class bill_pdf(models.Model):
    order_no = models.CharField(max_length=40, unique=True)
    transaction_id = models.CharField(max_length=100)
    file_name = models.CharField(max_length =100)
    pdf_file = models.FileField(upload_to='bills/')  
    datetime = models.DateTimeField()
    def _str_(self):
        return self.order_no   


class Invoices(models.Model):
    order_no = models.CharField(max_length=40)
    invoice_date = models.DateTimeField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return self.order_no

class RestaurantInfo(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    logo = models.ImageField()


class Notifications(models.Model):
    username = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField()

class OffersDiscounts(models.Model):    
    name = models.CharField(max_length=255)
    description = models.TextField()
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

class Inventory(models.Model):
    item_name = models.CharField(max_length=255, unique=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=3, default=0, validators=[MinValueValidator(Decimal('0'))])
    min_quantity = models.DecimalField(max_digits=12, decimal_places=3, default=0, validators=[MinValueValidator(Decimal('0'))])
    unit = models.CharField(max_length=50, choices=INVENTORY_UNIT_CHOICES)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['item_name']

    @property
    def is_low_stock(self):
        return self.quantity <= self.min_quantity

    def __str__(self):
        return f"{self.item_name} ({self.quantity} {self.unit})"


class Vendor(models.Model):
    name = models.CharField(max_length=255, unique=True)
    contact_person = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    gst_number = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [('draft', 'Draft'), ('ordered', 'Ordered'), ('received', 'Received'), ('cancelled', 'Cancelled')]
    PAYMENT_METHOD_CHOICES = [('cash', 'Cash'), ('card', 'Card'), ('upi', 'UPI'), ('bank', 'Bank Transfer'), ('credit', 'Credit')]

    number = models.CharField(max_length=40, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='purchase_orders')
    purchase_date = models.DateField(default=datetime.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-purchase_date', '-id']

    @property
    def total_amount(self):
        return sum((item.line_total for item in self.items.all()), Decimal('0'))

    @property
    def balance_amount(self):
        return self.total_amount - self.total_paid

    @property
    def total_paid(self):
        if not self.pk:
            return Decimal('0')
        return self.payments.aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

    @property
    def payable_amount(self):
        return max(self.balance_amount, Decimal('0'))

    @property
    def advance_amount(self):
        return max(-self.balance_amount, Decimal('0'))

    def __str__(self):
        return self.number


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    inventory_item = models.ForeignKey(Inventory, on_delete=models.PROTECT, related_name='purchase_items')
    quantity_ordered = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(Decimal('0.001'))])
    quantity_received = models.DecimalField(max_digits=12, decimal_places=3, default=0, validators=[MinValueValidator(Decimal('0'))])
    quantity_posted = models.DecimalField(max_digits=12, decimal_places=3, default=0, editable=False)
    unit = models.CharField(max_length=50, choices=INVENTORY_UNIT_CHOICES)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])

    class Meta:
        unique_together = [('purchase_order', 'inventory_item')]

    @property
    def line_total(self):
        return self.quantity_ordered * self.unit_cost

    def __str__(self):
        return f"{self.purchase_order.number} - {self.inventory_item.item_name}"


class PurchasePayment(models.Model):
    METHOD_CHOICES = PurchaseOrder.PAYMENT_METHOD_CHOICES
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name='payments')
    payment_date = models.DateField(default=timezone.localdate, db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['payment_date', 'id']

    def __str__(self):
        return f"{self.purchase_order.number} - {self.amount}"


class StockMovement(models.Model):
    PURCHASE_RECEIVED = 'purchase_received'
    KITCHEN_ISSUE = 'kitchen_issue'
    WASTAGE = 'wastage'
    RETURN_VENDOR = 'return_vendor'
    ADJUSTMENT = 'adjustment'
    OPENING_STOCK = 'opening_stock'
    MOVEMENT_CHOICES = [
        (PURCHASE_RECEIVED, 'Purchase Received'), (KITCHEN_ISSUE, 'Kitchen Issue'),
        (WASTAGE, 'Wastage'), (RETURN_VENDOR, 'Return to Vendor'),
        (ADJUSTMENT, 'Stock Adjustment'), (OPENING_STOCK, 'Opening Stock'),
    ]
    inventory_item = models.ForeignKey(Inventory, on_delete=models.PROTECT, related_name='movements')
    movement_at = models.DateTimeField(default=timezone.now, db_index=True)
    movement_type = models.CharField(max_length=30, choices=MOVEMENT_CHOICES)
    quantity_in = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    quantity_out = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    unit = models.CharField(max_length=50)
    reference_type = models.CharField(max_length=50, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    purchase_cost_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sale_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_by = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    balance_after = models.DecimalField(max_digits=12, decimal_places=3)

    class Meta:
        ordering = ['-movement_at', '-id']

    def __str__(self):
        return f"{self.inventory_item.item_name} - {self.get_movement_type_display()}"



class Online_Orders(models.Model):
    STATUS_CHOICES = [
        ('Placed', 'Placed'),
        ('Confirmed', 'Confirmed'),
        ('Preparing', 'Preparing'),
        ('Ready for Pickup', 'Ready for Pickup'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    username = models.CharField(max_length=100)
    phone_number = models.BigIntegerField()
    email = models.EmailField(null=True, blank=True)
    order_no = models.CharField(max_length=40)
    order_date = models.DateTimeField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['-order_date']

    def __str__(self):
        return f"Order {self.order_no} by {self.username}"

        

class Online_OrderItems(models.Model):
    order_no = models.CharField(max_length=40)
    menu_item = models.CharField(max_length=100)
    size = models.CharField(max_length=150)     
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return self.order_no
