from django.urls import path
from .views import HealthView, RegisterView, LoginView, LogoutView, VerifyTokenView

urlpatterns = [
    path("healthz", HealthView.as_view()),
    path("livez", HealthView.as_view()),
    path("login/", LoginView.as_view(), name="login"),
    path("login/logout/", LogoutView.as_view(), name="logout"),
    path("login/register/", RegisterView.as_view(), name="register"),
    path("int/auth/verify", VerifyTokenView.as_view()),
]


