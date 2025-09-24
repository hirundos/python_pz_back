from django.urls import path
from .views import HealthView, MyOrderView, CreateOrderView, BranchListView

urlpatterns = [
    path("healthz", HealthView.as_view()),
    path("livez", HealthView.as_view()),
    path("order/myorder/", MyOrderView.as_view()),
    path("order/", CreateOrderView.as_view()),
    path("order/branch/", BranchListView.as_view()),
]


