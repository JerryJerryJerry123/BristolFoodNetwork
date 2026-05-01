from django.contrib.auth.models import User
from django.db import models


class ProducerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    business_name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    address = models.TextField()
    postcode = models.CharField(max_length=20)

    def __str__(self):
        return f"Producer: {self.user.username}"


class CustomerProfile(models.Model):
    ACCOUNT_TYPES = [
        ('restaurant', 'Restaurant'),
        ('organisation', 'Organisation'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    delivery_address = models.TextField()
    postcode = models.CharField(max_length=20)
    account_type = models.CharField(
            max_length=20,
            choices=ACCOUNT_TYPES,
            default='organisation'
        )
    def __str__(self):
        return f"Customer: {self.user.username}"
    
class Notification(models.Model):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.customer.user.username}"