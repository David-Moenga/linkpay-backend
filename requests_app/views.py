from django.db import transaction as db_transaction
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from wallets.models import Wallet
from transactions.models import Transaction
from .models import PaymentRequest, Report
from .serializers import PaymentRequestSerializer, PaymentRequestCreateSerializer, ReportSerializer
from transactions.serializers import TransactionSerializer


class PaymentRequestListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PaymentRequestCreateSerializer
        return PaymentRequestSerializer

    def get_queryset(self):
        user = self.request.user
        return PaymentRequest.objects.filter(merchant=user) | PaymentRequest.objects.filter(customer=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        out = PaymentRequestSerializer(instance, context={"request": request})
        return Response(out.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save()


class PaymentRequestDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentRequestSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "reference"

    def get_queryset(self):
        user = self.request.user
        return PaymentRequest.objects.filter(merchant=user) | PaymentRequest.objects.filter(customer=user)


class PaymentRequestPayView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, reference):
        try:
            pr = PaymentRequest.objects.select_related("merchant", "customer").get(reference=reference)
        except PaymentRequest.DoesNotExist:
            return Response({"detail": "Payment request not found."}, status=status.HTTP_404_NOT_FOUND)

        if pr.status != PaymentRequest.Status.PENDING:
            return Response({"detail": "Payment request is not payable."}, status=status.HTTP_400_BAD_REQUEST)

        if pr.merchant == request.user:
            return Response({"detail": "Cannot pay your own request."}, status=status.HTTP_400_BAD_REQUEST)

        if pr.customer and pr.customer != request.user:
            return Response({"detail": "This request is for another customer."}, status=status.HTTP_403_FORBIDDEN)

        if pr.expires_at and pr.expires_at < timezone.now():
            pr.status = PaymentRequest.Status.EXPIRED
            pr.save(update_fields=["status"])
            return Response({"detail": "Payment request expired."}, status=status.HTTP_400_BAD_REQUEST)

        payer = request.user
        merchant = pr.merchant
        amount = pr.amount

        try:
            with db_transaction.atomic():
                payer_wallet = Wallet.objects.select_for_update().get(user=payer)
                merchant_wallet = Wallet.objects.select_for_update().get(user=merchant)
                if payer_wallet.balance < amount:
                    raise ValueError("Insufficient balance.")

                tx = Transaction.objects.create(
                    sender=payer,
                    recipient=merchant,
                    amount=amount,
                    currency=pr.currency,
                    description=pr.description or f"Payment request {pr.reference}",
                    transaction_type=Transaction.Type.MERCHANT_PAYMENT,
                    status=Transaction.Status.PENDING,
                    invoice=pr,
                )
                payer_wallet.balance -= amount
                merchant_wallet.balance += amount
                payer_wallet.save(update_fields=["balance", "updated_at"])
                merchant_wallet.save(update_fields=["balance", "updated_at"])

                tx.status = Transaction.Status.COMPLETED
                tx.save(update_fields=["status", "updated_at"])

                pr.status = PaymentRequest.Status.PAID
                pr.customer = payer
                pr.paid_transaction = tx
                pr.save(update_fields=["status", "customer", "paid_transaction"])
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"detail": "Payment failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"payment_request": PaymentRequestSerializer(pr).data, "transaction": TransactionSerializer(tx).data}, status=status.HTTP_200_OK)


class ReportCreateView(generics.CreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)
