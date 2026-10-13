import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from decimal import Decimal


class Transaction(models.Model):
    class Type(models.TextChoices):
        TRANSFER = "transfer", "Peer-to-peer transfer"
        MERCHANT_PAYMENT = "merchant_payment", "Merchant payment"
        INVOICE_PAYMENT = "invoice_payment", "Invoice payment"
        ADJUSTMENT = "adjustment", "Adjustment"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        REVERSED = "reversed", "Reversed"

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="sent_transactions")
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="received_transactions")
    amount = models.DecimalField(max_digits=18, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    currency = models.CharField(max_length=8, default="KES")
    description = models.CharField(max_length=255, blank=True)
    reference = models.CharField(max_length=40, unique=True, editable=False)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    transaction_type = models.CharField(max_length=24, choices=Type.choices, default=Type.TRANSFER)
    invoice = models.ForeignKey("requests_app.PaymentRequest", null=True, blank=True, on_delete=models.SET_NULL, related_name="payments")
    failure_reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = "TX-" + uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.reference


class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=128)
    target_type = models.CharField(max_length=64, blank=True)
    target_id = models.CharField(max_length=64, blank=True)
    detail = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
