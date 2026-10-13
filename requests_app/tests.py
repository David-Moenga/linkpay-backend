from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from wallets.models import Wallet

User = get_user_model()


class PaymentRequestTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.merchant = User.objects.create_user(username="bob", email="bob@test.com", password="Strong!pass123", account_type="merchant")
        self.customer = User.objects.create_user(username="alice", email="alice@test.com", password="Strong!pass123", account_type="individual")
        Wallet.objects.filter(user=self.customer).update(balance=Decimal("500.00"))
        Wallet.objects.filter(user=self.merchant).update(balance=Decimal("0.00"))
        self.customer_token = str(AccessToken.for_user(self.customer))
        self.merchant_token = str(AccessToken.for_user(self.merchant))

    def test_create_and_pay_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.merchant_token}")
        r = self.client.post("/api/payment-requests/", {"amount": "50.00", "description": "Invoice", "customer_username": "alice"}, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        ref = r.data["reference"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.customer_token}")
        r2 = self.client.post(f"/api/payment-requests/{ref}/pay/", {}, format="json")
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        self.assertEqual(r2.data["payment_request"]["status"], "paid")
        self.customer.refresh_from_db()
        self.merchant.refresh_from_db()
        self.assertEqual(self.customer.wallet.balance, Decimal("450.00"))
        self.assertEqual(self.merchant.wallet.balance, Decimal("50.00"))
