from decimal import Decimal

from django.db import transaction as db_transaction
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from wallets.models import Wallet
from .models import Transaction
from .serializers import TransactionSerializer, TransferCreateSerializer

PER_TRANSACTION_LIMIT = Decimal("100000.00")
DAILY_LIMIT = Decimal("500000.00")


class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(sender=user) | Transaction.objects.filter(recipient=user)


class TransactionDetailView(generics.RetrieveAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "reference"

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(sender=user) | Transaction.objects.filter(recipient=user)


class TransferCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TransferCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        from django.contrib.auth import get_user_model
        User = get_user_model()
        recipient = User.objects.get(username__iexact=data["recipient_username"])
        sender = request.user
        amount = data["amount"]
        currency = data.get("currency", "KES") or "KES"
        description = data.get("description", "")

        # Daily limit check
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        daily_total = Transaction.objects.filter(
            sender=sender, status=Transaction.Status.COMPLETED, created_at__gte=today_start
        ).aggregate(total=__import__("django.db.models", fromlist=["Sum"]).Sum("amount"))["total"] or Decimal("0")
        if daily_total + amount > DAILY_LIMIT:
            return Response({"detail": "Daily transfer limit exceeded."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with db_transaction.atomic():
                sender_wallet = Wallet.objects.select_for_update().get(user=sender)
                recipient_wallet = Wallet.objects.select_for_update().get(user=recipient)

                if sender_wallet.balance < amount:
                    raise ValueError("Insufficient balance.")

                tx = Transaction.objects.create(
                    sender=sender,
                    recipient=recipient,
                    amount=amount,
                    currency=currency,
                    description=description,
                    transaction_type=Transaction.Type.TRANSFER,
                    status=Transaction.Status.PENDING,
                )

                sender_wallet.balance = sender_wallet.balance - amount
                recipient_wallet.balance = recipient_wallet.balance + amount
                sender_wallet.save(update_fields=["balance", "updated_at"])
                recipient_wallet.save(update_fields=["balance", "updated_at"])

                tx.status = Transaction.Status.COMPLETED
                tx.save(update_fields=["status", "updated_at"])
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": "Transfer failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)
