from django.urls import path
from pizza import views

#TODO toppings/<int:pk> can be <slug:slug> but needs add slug to 
urlpatterns = [
    path('toppings/', views.ToppingList.as_view(), name='toppings_list'),
    path('toppings/<int:pk>', views.ToppingDetails.as_view(), name='toppings_detail')
    
]