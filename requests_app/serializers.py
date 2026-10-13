from rest_framework import serializers

from django.contrib.auth import get_user_model

from .models import PaymentRequest, Report

User = get_user_model()


class PaymentRequestSerializer(serializers.ModelSerializer):
    merchant_username = serializers.CharField(source="merchant.username", read_only=True)
    merchant_name = serializers.CharField(source="merchant.display_name", read_only=True)
    customer_username = serializers.CharField(source="customer.username", read_only=True, allow_null=True)
    is_paid = serializers.BooleanField(read_only=True)

    class Meta:
        model = PaymentRequest
        fields = (
            "id",
            "reference",
            "merchant",
            "merchant_username",
            "merchant_name",
            "customer",
            "customer_username",
            "amount",
            "currency",
            "description",
            "status",
            "is_paid",
            "created_at",
            "expires_at",
            "paid_transaction",
        )
        read_only_fields = ("id", "reference", "merchant", "status", "created_at", "paid_transaction")


class PaymentRequestCreateSerializer(serializers.ModelSerializer):
    customer_username = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = PaymentRequest
        fields = ("amount", "currency", "description", "customer_username", "expires_at")

    def create(self, validated_data):
        customer_username = validated_data.pop("customer_username", "")
        merchant = self.context["request"].user
        customer = None
        if customer_username:
            try:
                customer = User.objects.get(username__iexact=customer_username)
            except User.DoesNotExist:
                raise serializers.ValidationError({"customer_username": "Customer not found."})
        return PaymentRequest.objects.create(merchant=merchant, customer=customer, **validated_data)


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ("id", "reporter", "reported_user", "transaction", "reason", "details", "status", "created_at")
        read_only_fields = ("id", "reporter", "status", "created_at")
