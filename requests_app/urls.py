from django.urls import path
from .views import PaymentRequestDetailView, PaymentRequestListCreateView, PaymentRequestPayView, ReportCreateView

urlpatterns = [
    path("payment-requests/", PaymentRequestListCreateView.as_view(), name="payment-request-list"),
    path("payment-requests/<str:reference>/", PaymentRequestDetailView.as_view(), name="payment-request-detail"),
    path("payment-requests/<str:reference>/pay/", PaymentRequestPayView.as_view(), name="payment-request-pay"),
    path("reports/", ReportCreateView.as_view(), name="report-create"),
]
