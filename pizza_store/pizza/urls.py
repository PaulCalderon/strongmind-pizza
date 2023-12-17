from django.urls import path
from pizza import views


# toppings/<int:pk> and pizza/<int:pk> can be <slug:slug> but code will need refactoring
urlpatterns = [
    path('toppings/', views.ToppingList.as_view(), name='toppings_list'),
    path('toppings/<int:pk>', views.ToppingDetails.as_view(), name='toppings_detail'),
    path('pizzas/', views.PizzaList.as_view(), name='pizzas_list'),
    path('pizzas/<int:pk>', views.PizzaDetails.as_view(), name='pizzas_detail')
]