from django.urls import path
from .views import HealthView, MyOrderView, CreateOrderView, BranchListView

urlpatterns = [
    path("healthz", HealthView.as_view()),
    path("livez", HealthView.as_view()),
    path("order/myorder/", MyOrderView.as_view(), name="myorder"),
    path("order/", CreateOrderView.as_view(), name="order-list"),
    path("order/branch/", BranchListView.as_view(), name="branch-list"),
]


