from django.urls import path
from . import views

urlpatterns = [
    path('order/myorder/', views.myorder_list, name='myorder_list'),
    path('order/', views.order, name='order'),
]