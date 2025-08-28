from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('pizza_back.menu.urls')), # Include the menu app's URLs
    path('api/', include('pizza_back.order.urls')), # Include the order app's URLs
    path('api/', include('pizza_back.login.urls')),  # Include the login app's URLs
]
