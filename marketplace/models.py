from django.db import models
from django.contrib.auth.models import User
from accounts.models import CustomerProfile
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

class Recipe(models.Model):
    producer = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    description = models.TextField()
    cooking_instructions = models.TextField()

    ingredients = models.ManyToManyField('Product')

    SEASON_CHOICES = [
        ('autumn', 'Autumn'),
        ('winter', 'Winter'),
    ]

    season = models.CharField(max_length=20, choices=SEASON_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class FarmStory(models.Model):
    producer = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    content = models.TextField()

    HARVEST_CHOICES = [
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('autumn', 'Autumn'),
        ('winter', 'Winter'),
    ]

    harvest_season = models.CharField(max_length=20, choices=HARVEST_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Product(models.Model):

    STATUS_CHOICES = [
        ('seasonal', 'Seasonal'),
        ('out_of_season', 'Out of Season'),
        ('unavailable', 'Unavailable'),
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

    season_start_month = models.CharField(max_length=20, blank=True, null=True)
    
    season_end_month = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name
    
    @property
    def discounted_price(self):
        if self.is_surplus and self.discount_percentage and self.discount_percentage > 0:
            discount = self.price * Decimal(self.discount_percentage) / Decimal("100")
            return self.price - discount
        return self.price

    @property
    def has_discount(self):
        return self.is_surplus and self.discount_percentage and self.discount_percentage > 0

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
        return self.product.discounted_price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class Order(models.Model):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.id} by {self.customer.user.username}"


class SubOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('ready', 'Ready for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="suborders")
    producer = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_date = models.DateField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    @property
    def total(self):
        return sum(item.line_total for item in self.items.all())

    def is_valid_delivery_date(self):
        minimum_date = timezone.now() + timedelta(hours=48)
        return self.delivery_date >= minimum_date.date()


    def __str__(self):
        return f"SubOrder #{self.id} - {self.producer.username}"
    



class OrderItem(models.Model):
    suborder = models.ForeignKey(SubOrder, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=8, decimal_places=2)

    @property
    def line_total(self):
        return self.product.discounted_price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)

    rating = models.IntegerField()  # 1–5
    title = models.CharField(max_length=255)
    text = models.TextField()

    created_at = models.DateTimeField(default=timezone.now)

    # Important for case study (step 15/16)
    class Meta:
        unique_together = ("product", "customer")

    def __str__(self):
        return f"{self.product.name} - {self.rating}"

class RecurringOrder(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)

    frequency = models.CharField(max_length=20, default="weekly")  # NEW

    day_of_week = models.CharField(max_length=10)  # Monday
    delivery_day = models.CharField(max_length=10)  # Wednesday

    next_order_date = models.DateField(null=True, blank=True)  # NEW

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.username} - {self.day_of_week}"

class RecurringOrderItem(models.Model):
    recurring_order = models.ForeignKey(
        RecurringOrder,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class ScheduledOrder(models.Model):
    recurring_order = models.ForeignKey(
        RecurringOrder,
        on_delete=models.CASCADE,
        related_name="scheduled_orders"
    )

    scheduled_date = models.DateField()
    is_modified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.recurring_order.customer.username} - {self.scheduled_date}"


class ScheduledOrderItem(models.Model):
    scheduled_order = models.ForeignKey(
        ScheduledOrder,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"