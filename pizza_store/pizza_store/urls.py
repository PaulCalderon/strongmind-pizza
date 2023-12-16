from django.contrib import admin
from django.urls import path, include
from pizza import views


urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('admin/', admin.site.urls, name='admin'),
    path('swagger-index', views.swagger, name='swagger'),
    path('', include('pizza.urls')),
    path('', views.Homepage.as_view(), name='homepage')
]
