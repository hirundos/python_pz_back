from django.urls import path
from .views import HealthView, MyOrderView, CreateOrderView, BranchListView

urlpatterns = [
    path("", HealthView.as_view()),
    path("healthz", HealthView.as_view()),
    path("livez", HealthView.as_view()),
    path("api/order/myorder/", MyOrderView.as_view(), name="myorder"),
    path("api/order/", CreateOrderView.as_view(), name="order-list"),
    path("api/order/branch/", BranchListView.as_view(), name="branch-list"),
]


