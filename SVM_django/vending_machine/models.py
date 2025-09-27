from django.db import models

# Users collection
class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255) 
    role = models.CharField(max_length=10, choices=[("user", "User"), ("admin", "Admin")], default="user")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"   

# Vouchers collection
class Voucher(models.Model):
    code = models.CharField(max_length=50, unique=True)
    duration_minutes = models.IntegerField(default=30)
    is_redeemed = models.BooleanField(default=False)
    redeemed_at = models.DateTimeField(null=True, blank=True)
    redeemed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vouchers"

    def __str__(self):
        return self.code

# Activity Logs collection
class ActivityLog(models.Model):
    action = models.CharField(max_length=50) 
    voucher_code = models.CharField(max_length=50)
    email = models.EmailField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "activity_logs"  

