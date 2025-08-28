from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_check, name='login_check'),
    path('login/logout/', views.logout_view, name='logout_view'),
    path('login/register/', views.register_member, name='register_member')
]