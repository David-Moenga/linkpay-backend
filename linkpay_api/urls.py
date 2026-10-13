from django.contrib import admin
from django.urls import include, path

from .views import health_check

urlpatterns = [
    path("", health_check, name="health-check"),
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/users/", include("accounts.user_urls")),
    path("api/wallet/", include("wallets.urls")),
    path("api/", include("transactions.urls")),
    path("api/", include("requests_app.urls")),
]
