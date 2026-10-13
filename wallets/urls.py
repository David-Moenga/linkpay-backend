from django.urls import path
from .views import WalletOverviewView

urlpatterns = [
    path("", WalletOverviewView.as_view(), name="wallet-overview"),
]
