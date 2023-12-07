from django.db import IntegrityError
from django.test import TestCase
from pizza.models import PizzaTopping

# Create your tests here.

class TestPizzaToppingModel(TestCase): 
    def test_pizza_topping_should_return_error_when_duplicate_entry_is_made(self): #integration test
        duplicate_name = 'duplicate'
        PizzaTopping.objects.create(topping_name=duplicate_name)

        with self.assertRaises(IntegrityError):
            PizzaTopping.objects.create(topping_name=duplicate_name)

    def test_pizza_topping_unique_constraint_should_be_case_insensitive(self): #integration test
        duplicate_name = 'duplicate'
        capitalized_duplicate_name = 'DUPLICATE'
        PizzaTopping.objects.create(topping_name=duplicate_name)

        with self.assertRaises(IntegrityError):
            PizzaTopping.objects.create(topping_name=capitalized_duplicate_name)


    
        
