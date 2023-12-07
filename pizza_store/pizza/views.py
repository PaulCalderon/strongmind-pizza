from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view
from pizza.models import PizzaTopping
from pizza.serializers import PizzaToppingSerializer


@api_view(['GET'])
def homepage(request):
    "Click on the links below to navigate to different parts of the Pizza Store project"
    return Response({
        'Topping List' : reverse('toppings_list', request=request)})

class ToppingList(generics.GenericAPIView):
    """
    Lists pizza toppings added by an owner<br>
    Implemented methods are **GET**, **POST**, **PUT**, **DELETE**<br>
    Non authenticated users will only be able to use GET<br>
    Only 'owner' users will be able to use the other methods<br>
    """
    serializer_class = PizzaToppingSerializer



    def get(self, request):
        """
        Returns a list of all pizza toppings
        """
        return Response(data="test")
