from django.db import models
import uuid
from django.db.models import *
from account.managers import UserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator, MinLengthValidator
from datetime import date
from account.models import CustomerAddressModel, User
from catalogue.models import ProductModel
from core.base.models import BaseModel
from django.utils.text import slugify
from core.base.models import BaseModel
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings



class Transaction(BaseModel):
    user = ForeignKey(User, on_delete=SET_NULL, null=True, related_name='transactions')
    transaction_user = CharField(max_length=50, null=True, blank=True)
    purpose = CharField(max_length=50)
    amount = DecimalField(max_digits=10, decimal_places=2)
    order_info = JSONField(null=True, blank=True)
    payment_status = BooleanField(default=False) # e.g., Success, Pending, Failed 



class Cart(BaseModel):
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='carts')
   
    def subtotal(self):
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"Cart #{self.id} for {self.user}"

class CartItem(Model):
    cart = ForeignKey(Cart, on_delete=CASCADE, related_name='items')
    product = ForeignKey(ProductModel, on_delete=CASCADE)
    quantity = PositiveIntegerField(default=1)
    
    def save(self, *args, **kwargs):
        if self.product.stock_quantity is not None and self.quantity > self.product.stock_quantity:
            raise ValueError("Quantity cannot exceed available stock.")
        super().save(*args, **kwargs)

    def total_price(self):
        return self.product.offer_price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"





class OrderModel(Model):
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='orders')
    transaction = ForeignKey('orders.Transaction', on_delete=SET_NULL, null=True, blank=True, related_name='orders')
    pg_order_id = CharField(max_length=100, unique=True)
    pg_order_status = CharField(max_length=50)
    address = ForeignKey(CustomerAddressModel, on_delete=SET_NULL, null=True, blank=True)
    order_summary = JSONField(null=True, blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.pg_order_id} for {self.user}"

class SellerOrderModel(BaseModel):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('PROCESSING', 'Processing'),
        ('PACKED', 'Packed'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
        ('RETURNED', 'Returned'),
        ('REFUNDED', 'Refunded'),
    )
    order = ForeignKey(OrderModel, on_delete=CASCADE, related_name='seller_orders')
    seller = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='received_orders')
    status = CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"SellerOrder {self.id} for Order {self.order.pg_order_id} (Seller: {self.seller})"

class OrderItemModel(Model):
    order = ForeignKey(OrderModel, on_delete=CASCADE, related_name='items')
    seller_order = ForeignKey(SellerOrderModel, on_delete=CASCADE, related_name='items', null=True, blank=True)
    product = ForeignKey(ProductModel, on_delete=SET_NULL, null=True)
    quantity = PositiveIntegerField(default=1)
    price = DecimalField(max_digits=10, decimal_places=2)