from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vouchers = models.IntegerField(default=0)
    transaction_history = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

class Bottle(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image_url = models.URLField(blank=True, help_text="Optional: URL to a bottle image")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Voucher(models.Model):
    DURATION_CHOICES = [
        (15, '15 minutes'),
        (30, '30 minutes'),
        (60, '60 minutes'),
        (120, '2 hours'),
    ]
    
    code = models.CharField(max_length=20, unique=True)
    duration_minutes = models.IntegerField(choices=DURATION_CHOICES, default=30)
    is_redeemed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    redeemed_at = models.DateTimeField(blank=True, null=True)
    redeemed_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.code} ({self.duration_minutes} mins) - {'Redeemed' if self.is_redeemed else 'Available'}"