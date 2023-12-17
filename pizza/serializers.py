from pizza.models import PizzaTopping, Pizza
from rest_framework import serializers

class PizzaToppingSerializer(serializers.ModelSerializer):
    """Displays toppings and url to individual topping pages."""

    # url for individual pizza topping entry
    url = serializers.HyperlinkedIdentityField(
                                            view_name='toppings_detail',
                                            read_only=True
                                            )

    class Meta:
        model = PizzaTopping
        fields = ['topping', 'url']


class PizzaSerializer(serializers.ModelSerializer):
    """Displays pizza, associated toppings and url to individual pizza pages."""

    # SlugRelatedField was used to represent field as 'topping' instead of pk
    toppings = serializers.SlugRelatedField(
                                            many=True,
                                            queryset= PizzaTopping.objects.all(),
                                            slug_field='topping'
                                            )
                                            
    url = serializers.HyperlinkedIdentityField(
                                            view_name='pizzas_detail',
                                            read_only=True
                                            )
    
    class Meta:
        model = Pizza
        fields = ['pizza', 'toppings', 'url' ]
