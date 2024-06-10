from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class CustomManager(models.Manager):
    def mobile_list(self):
        return self.filter(category__iexact = 'mobile')

    def tv_list(self):
        return self.filter(category__iexact = 'tv')    
    

class Product(models.Model):
    prod_id = models.IntegerField(primary_key = True)
    prod_name = models.CharField(max_length = 50)
    type = [("mobile",'Mobile'),
            ("laptop",'Laptop'),
            ("tv",'TV')]
    category = models.CharField(max_length = 25, choices = type )
    desc = models.CharField(max_length = 300)
    price = models.IntegerField()
    image = models.ImageField(upload_to = 'images')
    objects = models.Manager()     # default manager
    prod = CustomManager()         # custom manager      

    def __str__(self) -> str:
        return f'{self.prod_name}'


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    date_added = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete= models.CASCADE, default = '', null = True, blank = True)

    def __str__(self):
        # product.prod_name because we are using it from another model i.e in this case the Product model
        return f'{self.quantity} {self.product.prod_name} {self.user}'  
    


class Order(models.Model):
    order_id = models.CharField(max_length = 50, default = '0')
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    date_added = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete= models.CASCADE, default = '', null = True, blank = True)
    is_comleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.order_id} - {self.user} - {self.product.prod_name}'



class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    address = models.CharField(max_length=200)
    zipcode = models.PositiveIntegerField(validators = [MaxValueValidator(999999), MinValueValidator(100000)])
    phone = models.PositiveBigIntegerField()

    def __str__(self):
        return f"{self.address}"
    
