from django.db import models
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.contrib.auth.hashers import make_password, check_password




class Restaurants(models.Model):   
    name = models.CharField(max_length=100)    
    phone_number = models.BigIntegerField()
    mobile_number = models.BigIntegerField(blank=True, null=True)
    email = models.EmailField()    
    address1 = models.TextField(blank=True, null=True)
    address2 = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    gst_no = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)    
    pay_name = models.CharField(max_length=200, blank=True, null=True)
    upi_id = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return self.name
    


class Admin(models.Model):   
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    phone_number = models.BigIntegerField()
    email = models.EmailField()    
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):        
        if self.pk:
            original = Admin.objects.get(pk=self.pk)            
            if original.password != self.password:
                self.password = make_password(self.password)
        else:            
            self.password = make_password(self.password)

        super(Admin, self).save(*args, **kwargs)

    def __str__(self):
        return self.username
