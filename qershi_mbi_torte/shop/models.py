from django.db import models
from django.contrib.auth.models import User

#User
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username



# Produkti
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    ingredients = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    available_quantity = models.IntegerField(default=0)
    ordered_quantity = models.IntegerField(default=0)
    image = models.ImageField(upload_to='images/', default='images/default.png')

    def __str__(self):
        return self.name

    @property
    def remaining_quantity(self):
        return self.available_quantity - self.ordered_quantity


# Porosia
class Order(models.Model):
    STATUS_CHOICES = (
        ('preparing', 'Në përgatitje'),
        ("shipped", "E dërguar"),
        ("delivered", "Përfunduar"),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="preparing")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    PAYMENT_CHOICES = (
        ("cash", "Pagesë me dorë"),
        ("bank_transfer", "Pagesë me bankë")
    )
    payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICES, default="cash")

    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.product.price * item.quantity for item in self.items.all())

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def subtotal(self):
        return self.product.price * self.quantity

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey('shop.Product', on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} ❤️ {self.product}"

class OrderNotification(models.Model):
        user = models.ForeignKey(User, on_delete=models.CASCADE)
        order = models.ForeignKey("Order", on_delete=models.CASCADE)
        message = models.TextField()
        created_at = models.DateTimeField(auto_now_add=True)
        read = models.BooleanField(default=False)

        def __str__(self):
            return f"Njoftim për {self.user.username} - {self.order.id}"

