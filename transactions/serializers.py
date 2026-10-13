from rest_framework import serializers

from decimal import Decimal
from django.contrib.auth import get_user_model

from .models import Transaction

User = get_user_model()


class TransactionSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source="sender.username", read_only=True)
    sender_name = serializers.CharField(source="sender.display_name", read_only=True)
    recipient_username = serializers.CharField(source="recipient.username", read_only=True)
    recipient_name = serializers.CharField(source="recipient.display_name", read_only=True)
    invoice_reference = serializers.CharField(source="invoice.reference", read_only=True, allow_null=True)

    class Meta:
        model = Transaction
        fields = (
            "id",
            "reference",
            "transaction_type",
            "status",
            "amount",
            "currency",
            "description",
            "sender",
            "sender_username",
            "sender_name",
            "recipient",
            "recipient_username",
            "recipient_name",
            "invoice",
            "invoice_reference",
            "failure_reason",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class TransferCreateSerializer(serializers.Serializer):
    recipient_username = serializers.CharField()
    amount = serializers.DecimalField(max_digits=18, decimal_places=2, min_value=Decimal("0.01"))
    description = serializers.CharField(required=False, allow_blank=True, max_length=255)
    currency = serializers.CharField(required=False, default="KES", max_length=8)

    def validate_recipient_username(self, value):
        try:
            recipient = User.objects.get(username__iexact=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Recipient not found.")
        if recipient == self.context["request"].user:
            raise serializers.ValidationError("Cannot transfer to yourself.")
        return recipient.username

    def validate_amount(self, value):
        # per-transaction limit
        if value > 100000:
            raise serializers.ValidationError("Amount exceeds per-transaction limit (100,000).")
        return value
