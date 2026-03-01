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
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    delivery_address = models.TextField()
    postcode = models.CharField(max_length=20)

    def __str__(self):
        return f"Customer: {self.user.username}"