from django.contrib import admin
from .models import UserProfile, Product, Order, OrderItem

admin.site.register(UserProfile)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)