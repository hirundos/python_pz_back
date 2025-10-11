from django.urls import path
from .views import HealthView, PizzaListView, PizzaTypesView, GetPizzaIdView

urlpatterns = [
    path("", HealthView.as_view()),
    path("healthz", HealthView.as_view()),
    path("livez", HealthView.as_view()),
    path("api/menu/", PizzaListView.as_view(), name="menu-list"),
    path("api/menu/types/", PizzaTypesView.as_view(), name="pizza-types-list"),
    path("api/menu/get_pizza_id/", GetPizzaIdView.as_view(), name="get_pizza_id"),
]


