from django.http import Http404
from rest_framework import generics, status, permissions
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
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    # returns a json of toppings
    # needs to implement a custom serializer to only display the toppings themselves
    def get(self, request):
        """
        Returns a list of all pizza toppings
        """
        # breakpoint()
        topping_list = self.get_queryset()
        serializer = PizzaToppingSerializer(topping_list, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        """
        Submits a new pizza topping. Must be Unique.
        """
        new_topping = request.data
        serializer = PizzaToppingSerializer(data=new_topping, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ToppingDetails(generics.GenericAPIView):
    """
    Displays an individual topping<br>
    Implemented methods are **GET**, **PUT**, **DELETE**.<br>
    Non authenticated users will only be able to use GET.<br>
    Only 'owner' users will be able to edit and delete toppings.
    """
    serializer_class = PizzaToppingSerializer
    queryset = PizzaTopping.objects.all()
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def _get_object(self, pk):
        try:
            topping = PizzaTopping.objects.get(pk=pk)
            return topping

        except PizzaTopping.DoesNotExist:
            raise Http404
        
    def get(self, request, pk):
        """
        Returns an individual topping
        """
        topping = self._get_object(pk=pk)
        serializer = PizzaToppingSerializer(topping, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Updates the currently viewed topping
        """
        topping = self._get_object(pk=pk)
        serializer = PizzaToppingSerializer(topping,  data=request.data, partial=True, context= {'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """
        Deletes the currently viewed topping
        """
        topping = self._get_object(pk=pk)
        topping.delete()
        return Response("Sucessfully Deleted", status=status.HTTP_204_NO_CONTENT)
