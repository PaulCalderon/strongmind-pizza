from pizza.models import PizzaTopping
from rest_framework import serializers

class PizzaToppingSerializer(serializers.ModelSerializer):

    class Meta:
        model = PizzaTopping
        fields = ['topping_name']
