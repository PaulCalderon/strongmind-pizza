from pizza.models import PizzaTopping
from rest_framework import serializers

class PizzaToppingSerializer(serializers.ModelSerializer):
    # url for individual pizza topping entry
    url = serializers.HyperlinkedIdentityField(view_name='toppings_detail', read_only=True)

    class Meta:
        model = PizzaTopping
        fields = ['topping_name', 'url']
