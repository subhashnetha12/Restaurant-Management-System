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
    item_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    min_quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=50)
    last_updated = models.DateTimeField(auto_now=True)



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
