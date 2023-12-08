from django.db import IntegrityError
from django.test import RequestFactory, TestCase
from django.contrib.auth.models import User
from pizza.models import PizzaTopping
from pizza.serializers import PizzaToppingSerializer
from rest_framework.reverse import reverse
from unittest.mock import patch


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

class TestPizzaToppingSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('user', 'pass')
        cls.factory = RequestFactory()

    # can mock validator checker to return false
    def test_serializer_is_valid_method_should_return_false_for_invalid_data(self): #integration test
        invalid_data=None
        serializer = PizzaToppingSerializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())

    # Checks that is_valid isn't just returning false for all data
    @patch.object(PizzaToppingSerializer, 'run_validation')
    def test_serializer_is_valid_method_should_return_true_for_valid_data(self, mock_run_validation): #integration test
        mock_run_validation.return_value = 'some valid data'
        serializer = PizzaToppingSerializer(data='some valid data')

        self.assertTrue(serializer.is_valid())

class TestPizzaToppingURLs(TestCase):
    
    def test_homepage_url_is_as_expected(self):

        pass

# Tests ToppingList and ToppingDetails class views
class TestPizzaToppingViews(TestCase):
    def test(self):
        pass

class TestPizzaToppingPermissions(TestCase):
    def test_view_should_return_403_when_unauthorized_user_tries_to_use_write_methods(self):
        pass
