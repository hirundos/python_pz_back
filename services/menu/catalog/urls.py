from django.urls import path
from .views import HealthView, PizzaListView, PizzaTypesView, GetPizzaIdView

urlpatterns = [
    path("healthz", HealthView.as_view()),
    path("livez", HealthView.as_view()),
    path("menu/", PizzaListView.as_view()),
    path("menu/types/", PizzaTypesView.as_view()),
    path("menu/get_pizza_id/", GetPizzaIdView.as_view()),
]


