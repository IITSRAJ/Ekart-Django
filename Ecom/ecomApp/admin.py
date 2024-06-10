from django.contrib import admin
from . models import Product, CartItem, Order, UserAddress

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ('prod_name', 'category')

admin.site.register(Product, ProductAdmin)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(UserAddress)
