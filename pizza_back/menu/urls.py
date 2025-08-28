from django.urls import path
from . import views

urlpatterns = [
    path('menu/', views.pizza_list, name='pizza_list'),
    path('menu/types/', views.pizza_type_list, name='pizza_type_list'),
    path('menu/get_pizza_id/', views.get_pizza_id, name='get_pizza_id')
]