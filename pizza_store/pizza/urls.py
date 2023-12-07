from django.urls import path
from pizza import views

urlpatterns = [
    path('toppings/', views.ToppingList.as_view(), name='toppings_list'),
    
]