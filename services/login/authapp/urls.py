from django.urls import path
from .views import HealthView, RegisterView, LoginView, LogoutView, VerifyTokenView

urlpatterns = [
    path("", HealthView.as_view()),
    path("healthz", HealthView.as_view()),
    path("livez", HealthView.as_view()),
    path("api/login/", LoginView.as_view(), name="login"),
    path("api/login/logout/", LogoutView.as_view(), name="logout"),
    path("api/login/register/", RegisterView.as_view(), name="register"),
    path("api/login/int/auth/verify", VerifyTokenView.as_view()),
]


