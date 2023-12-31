from django.http import Http404, HttpResponse
from django.template import loader
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.decorators import APIView
from pizza.models import PizzaTopping, Pizza
from pizza.serializers import PizzaToppingSerializer, PizzaSerializer



def swagger(request):
    """Swagger View"""
    template = loader.get_template("pizza/swagger-index.html")
    return HttpResponse(template.render(request=request))

# /
class Homepage(APIView):
    """Click on the links below to navigate to different parts of the Pizza Store project"""

    def get(self, request):

        return Response({
            'Topping List' : reverse('toppings_list', request=request),
            'Pizza List' : reverse('pizzas_list', request=request),
            'Swagger' : reverse('swagger', request=request)
            })

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

    def get(self, request) :
        """Returns a list of all pizza toppings."""
        topping_list = self.get_queryset()
        serializer = PizzaToppingSerializer(topping_list, many=True, context={'request': request})

        return Response(serializer.data)

    def post(self, request):
        """Submits a new pizza topping. Must be unique."""
        new_topping = request.data
        serializer = PizzaToppingSerializer(data=new_topping, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# toppings/<int:pk>
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
        """Returns an individual topping."""
        topping = self._get_object(pk=pk)
        serializer = PizzaToppingSerializer(topping, context={'request': request})

        return Response(serializer.data)

    def put(self, request, pk):
        """Updates the topping entry.""" 
        topping = self._get_object(pk=pk)
        serializer = PizzaToppingSerializer(topping,  data=request.data, partial=False, context= {'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """Deletes the topping entry."""
        topping = self._get_object(pk=pk)
        topping.delete()

        return Response("Sucessfully Deleted", status=status.HTTP_204_NO_CONTENT)


# pizzas/
class PizzaList(generics.GenericAPIView):
    """
    Lists pizzas added by a pizza chef.<br>
    Implemented methods are **GET**, **POST**.<br>
    Non authenticated users will only be able to use GET.<br>
    Only 'chef' users will be able to POST new toppings.<br>
    URLs are included to navigate to individual pizza pages.
    """

    serializer_class = PizzaSerializer
    queryset = Pizza.objects.all()
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    def get(self, request):
        """Returns a list of all pizzas."""
        pizza_list = self.get_queryset()
        serializer = PizzaSerializer(pizza_list, many=True, context={'request': request})

        return Response(serializer.data)

    def post(self, request):
        """Submits a new pizza. Must be unique. Toppings must have entry"""
        new_pizza = request.data
        serializer = PizzaSerializer(data=new_pizza, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# pizzas/<int:pk>
class PizzaDetails(generics.GenericAPIView):
    """
    Displays an individual pizza<br>
    Implemented methods are **GET**, **PUT**, **DELETE**.<br>
    Non authenticated users will only be able to use GET.<br>
    Only 'chef' users will be able to edit and delete pizzas.<br>
    You can use Ctrl+Click to select multiple toppings.
    """

    serializer_class = PizzaSerializer
    queryset = Pizza.objects.all()
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def _get_object(self, pk):
        try:
            pizza = Pizza.objects.get(pk=pk)
            return pizza

        except Pizza.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """Returns an individual pizza."""
        pizza = self._get_object(pk=pk)
        serializer = PizzaSerializer(pizza, context={'request': request})

        return Response(serializer.data)

    def put(self, request, pk):
        """Updates the pizza."""
        pizza = self._get_object(pk=pk)
        serializer = PizzaSerializer(pizza,  data=request.data, partial=False, context= {'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Deletes the pizza entry."""
        pizza = self._get_object(pk=pk)
        pizza.delete()

        return Response("Sucessfully Deleted", status=status.HTTP_204_NO_CONTENT)

