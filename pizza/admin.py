from django.contrib import admin
from pizza.models import PizzaTopping, Pizza
# Register your models here.

admin.site.register(PizzaTopping)
admin.site.register(Pizza)
