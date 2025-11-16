
from django import forms
from .models import UserProfile, Product, Order, OrderItem


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['address', 'phone_number']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'available_quantity', 'image']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user', 'status','payment_method']


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']
