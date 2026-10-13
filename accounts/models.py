from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class AccountType(models.TextChoices):
        INDIVIDUAL = "individual", "Individual / Customer"
        MERCHANT = "merchant", "Merchant / Small business"
        FREELANCER = "freelancer", "Freelancer / Service provider"
        SERVICE_PROVIDER = "service_provider", "Service provider"
        SUPPLIER = "supplier", "Supplier / Business network"

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    account_type = models.CharField(
        max_length=32, choices=AccountType.choices, default=AccountType.INDIVIDUAL
    )
    phone = models.CharField(max_length=32, blank=True)
    business_name = models.CharField(max_length=255, blank=True)
    is_verified = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    @property
    def display_name(self):
        if self.business_name:
            return self.business_name
        full = self.get_full_name().strip()
        return full or self.username
