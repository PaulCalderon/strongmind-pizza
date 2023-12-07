from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view
from pizza.models import PizzaTopping
from pizza.serializers import PizzaToppingSerializer

# /
@api_view(['GET'])
def homepage(request):
    "Click on the links below to navigate to different parts of the Pizza Store project"
    return Response({
        'Topping List' : reverse('toppings_list', request=request)})

# toppings/
class ToppingList(generics.GenericAPIView):
    """
    Lists pizza toppings added by an owner.<br>
    Implemented methods are **GET**, **POST**.<br>
    Non authenticated users will only be able to use GET.<br>
    Only 'owner' users will be able to POST new toppings.<br>
    URLs are included to navigate to individual topping pages.
    """
    serializer_class = PizzaToppingSerializer
    queryset = PizzaTopping.objects.all()

    #returns a json of toppings
    #needs to implement a custom serializer to only display the toppings themselves
    def get(self, request):
        """
        Returns a list of all pizza toppings
        """
        topping_list = self.get_queryset()
        serializer = PizzaToppingSerializer(topping_list, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Submits a new pizza topping. Must be Unique.
        """
        new_topping = request.data
        serializer = PizzaToppingSerializer(data=new_topping)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

