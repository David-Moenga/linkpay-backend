from django.urls import path
from .views import TransactionDetailView, TransactionListView, TransferCreateView

urlpatterns = [
    path("transactions/", TransactionListView.as_view(), name="transaction-list"),
    path("transactions/<str:reference>/", TransactionDetailView.as_view(), name="transaction-detail"),
    path("transfers/", TransferCreateView.as_view(), name="transfer-create"),
]
