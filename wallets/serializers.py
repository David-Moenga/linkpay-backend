from rest_framework import serializers

from .models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    display_name = serializers.CharField(source="user.display_name", read_only=True)
    account_type = serializers.CharField(source="user.account_type", read_only=True)

    class Meta:
        model = Wallet
        fields = ("public_id", "currency", "balance", "is_testnet", "stellar_public_key", "username", "display_name", "account_type", "created_at", "updated_at")
        read_only_fields = fields
