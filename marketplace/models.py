from django.db import models
from django.contrib.auth.models import User
from accounts.models import CustomerProfile

class Product(models.Model):

    STATUS_CHOICES = [
        ('seasonal', 'Seasonal'),
        ('non_seasonal', 'Non Seasonal'),
        ('all_year', 'All Year'),
    ]

    producer = models.ForeignKey(User, on_delete=models.CASCADE)

    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=255)
    description = models.TextField()

    price = models.DecimalField(max_digits=10, decimal_places=2)

    unit = models.CharField(max_length=50)
    quantity = models.IntegerField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )

    is_surplus = models.BooleanField(default=False)

    discount_percentage = models.IntegerField(default=0)

    organic_certified = models.BooleanField(default=False)

    allergen_info = models.JSONField(blank=True, null=True)

    harvest_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=255,unique=True)

    def __str__(self):
        return self.name
    
class Cart(models.Model):
    customer = models.OneToOneField(CustomerProfile, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.customer.user.username}"

    @property
    def total(self):
        return sum(item.line_total for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=1)

    class Meta:
        unique_together = ("cart", "product")

    @property
    def line_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"