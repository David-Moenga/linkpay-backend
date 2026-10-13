import uuid

from django.conf import settings
from django.db import models


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet")
    currency = models.CharField(max_length=8, default="KES")
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=10000)
    public_id = models.CharField(max_length=32, unique=True, editable=False)
    stellar_public_key = models.CharField(max_length=128, blank=True)
    is_testnet = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.public_id:
            self.public_id = "LP-" + uuid.uuid4().hex[:10].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_id} {self.balance} {self.currency}"
