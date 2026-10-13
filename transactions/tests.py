from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from wallets.models import Wallet
from .models import Transaction

User = get_user_model()


class TransferTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.alice = User.objects.create_user(username="alice", email="alice@test.com", password="Strong!pass123", account_type="individual")
        self.bob = User.objects.create_user(username="bob", email="bob@test.com", password="Strong!pass123", account_type="merchant")
        # reset wallet balances deterministically
        Wallet.objects.filter(user=self.alice).update(balance=Decimal("1000.00"))
        Wallet.objects.filter(user=self.bob).update(balance=Decimal("0.00"))
        from rest_framework_simplejwt.tokens import AccessToken
        self.alice_token = str(AccessToken.for_user(self.alice))

    def test_transfer_updates_balances(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.alice_token}")
        r = self.client.post("/api/transfers/", {"recipient_username": "bob", "amount": "100.00", "description": "test"}, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.data["status"], "completed")
        self.alice.refresh_from_db()
        self.bob.refresh_from_db()
        self.assertEqual(self.alice.wallet.balance, Decimal("900.00"))
        self.assertEqual(self.bob.wallet.balance, Decimal("100.00"))
        self.assertEqual(Transaction.objects.count(), 1)

    def test_transfer_requires_auth(self):
        r = self.client.post("/api/transfers/", {"recipient_username": "bob", "amount": "10.00"}, format="json")
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)
