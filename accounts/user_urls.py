from django.urls import path

from .views import UserLookupView

urlpatterns = [
    path("lookup/", UserLookupView.as_view(), name="user-lookup"),
]
