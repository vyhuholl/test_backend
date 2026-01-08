"""URL patterns for authentication endpoints."""

from django.urls import path

from authentication.views import (
    DeleteAccountView,
    LoginView,
    LogoutView,
    ProfileView,
    RegisterView,
)


app_name = "authentication"

urlpatterns = [
    path("register", RegisterView.as_view(), name="register"),
    path("login", LoginView.as_view(), name="login"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("profile", ProfileView.as_view(), name="profile"),
    path("profile/delete", DeleteAccountView.as_view(), name="delete_account"),
]
