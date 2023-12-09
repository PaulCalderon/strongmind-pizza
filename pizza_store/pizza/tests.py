from unittest import skip
from unittest.mock import patch, MagicMock, ANY
from django.db import IntegrityError
from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.urls import Resolver404, resolve
from rest_framework import permissions
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory, force_authenticate
from pizza.models import PizzaTopping
from pizza.serializers import PizzaToppingSerializer
from pizza.views import ToppingList, ToppingDetails



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
        cls.factory = APIRequestFactory()

    # can mock validator checker to return false
    def test_serializer_is_valid_method_should_return_false_for_invalid_data(self): #integration test
        invalid_data=None
        serializer = PizzaToppingSerializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())

    # Checks that is_valid isn't just returning false for all data
    @patch.object(PizzaToppingSerializer, 'run_validation')
    def test_serializer_is_valid_method_should_return_true_for_valid_data(self, mock_run_validation): #integration test maybe
        mock_run_validation.return_value = 'some valid data'
        serializer = PizzaToppingSerializer(data='some valid data')

        self.assertTrue(serializer.is_valid())

class TestPizzaToppingURLs(TestCase):
    """Unit tests for URL Conf"""

    def test_homepage_url_is_correct(self):
        reverse_url = reverse(viewname='homepage')
        resolve_url = resolve('/')

        self.assertEqual(reverse_url, '/')
        self.assertEqual(resolve_url.url_name, 'homepage')

    def test_toppings_list_url_is_correct(self):
        reverse_url = reverse(viewname='toppings_list')
        resolve_url = resolve('/toppings/')

        self.assertEqual(reverse_url, '/toppings/')
        self.assertEqual(resolve_url.url_name, 'toppings_list')
    
    def test_toppings_detail_url_is_correct(self):
        reverse_url = reverse(viewname='toppings_detail', kwargs={'pk':1})
        resolve_url = resolve('/toppings/1')

        self.assertEqual(reverse_url, '/toppings/1')
        self.assertEqual(resolve_url.url_name, 'toppings_detail')
        self.assertDictEqual(resolve_url.kwargs, {'pk':1})

    def test_resolving_invalid_links_should_raise_expection(self):

        with self.assertRaises(Resolver404):
            resolve('invalid_link/')

    @skip("Unimplemented yet") # TODO
    def test_invalid_link_should_raise_status_code_404(self): # integration test
        assert False

class TestPizzaToppingListView(TestCase):
    """ Tests ToppingList class views"""

    @classmethod
    def setUpTestData(cls):
        cls.factory = APIRequestFactory()
        cls.topping_list_view = ToppingList.as_view()

    @patch('pizza.views.ToppingList.get_queryset') # bit complicated to mock return of get_queryset
    @patch('pizza.views.PizzaToppingSerializer')
    def test_topping_list_should_return_data_from_serializer_on_get(self, mock_serializer, mock_get_queryset):
        """Checks if serializer processed queryset and get returns correct data."""
        get_queryset_instance = mock_get_queryset.return_value
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.data = 'data'
        request = self.factory.get('/')
        response = self.topping_list_view(request)

        mock_serializer.assert_called_with(get_queryset_instance, many=ANY, context=ANY)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, 'data')

    @patch('pizza.views.ToppingList.get_queryset') # bit complicated to mock return of get_queryset
    @patch('pizza.views.PizzaToppingSerializer')
    def test_topping_list_should_allow_anonymous_users_to_see_topping_list(self, mock_serializer, mock_get_queryset):
        """Checks if get returns correct data."""
        mock_instance = mock_serializer.return_value
        mock_instance.data = 'data'
        request = self.factory.get('/')
        response = self.topping_list_view(request)
        
        self.assertTrue(request.user.is_anonymous)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, 'data')
    
    @patch('pizza.views.permissions.DjangoModelPermissionsOrAnonReadOnly.has_permission')
    @patch('pizza.views.PizzaToppingSerializer')
    def test_topping_list_should_receive_correct_data_from_request_on_post(self, mock_serializer, mock_permission):
        """Mocks serializer to return dummy data and permission to be granted"""
        mock_permission.return_value = True
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.data = 'data'
        request = self.factory.post("/toppings/", {'topping_name': 'data'}, format='json')
        response = self.topping_list_view(request)

        mock_serializer.assert_called_with(data={'topping_name': 'data'}, context=ANY)


    @patch('pizza.views.permissions.DjangoModelPermissionsOrAnonReadOnly.has_permission')
    @patch('pizza.views.PizzaToppingSerializer')
    def test_topping_list_should_return_201_and_response_data_on_valid_post(self, mock_serializer, mock_permission):
        """Mocks serializer to return dummy data and permission to be granted"""
        mock_permission.return_value = True
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.data = 'data'
        request = self.factory.post("/toppings/", {'topping_name': 'data'}, format='json')
        response = self.topping_list_view(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, 'data')
    
    @patch('pizza.views.permissions.DjangoModelPermissionsOrAnonReadOnly.has_permission')
    @patch('pizza.views.PizzaToppingSerializer')
    def test_topping_list_should_return_400_if_serializer_is_invalid_on_post(self, mock_serializer, mock_permission):
        """Mocks serializer receiving invalid request, therefore is_valid fails. Checks POST"""
        mock_permission.return_value = True
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.errors = 'error'
        mock_serializer_instance.is_valid.return_value = False
        request = self.factory.post("/toppings/", {'error': 'error'}, format='json')
        response = self.topping_list_view(request)
        
        self.assertEqual(response.data, 'error')
        self.assertEqual(response.status_code, 400)

    @patch('pizza.views.PizzaToppingSerializer')
    def test_topping_list_should_return_403_if_request_is_unauthenticated_on_post(self, mock_serializer):
        """Permission is not mocked"""
        request = self.factory.post("/toppings/", {'topping_name': 'data'}, format='json')
        response = self.topping_list_view(request)

        mock_serializer.assert_not_called()
        self.assertContains(response, status_code=403, text='Authentication credentials were not provided')
        self.assertEqual(response.status_code, 403)

    @patch('pizza.views.permissions.DjangoModelPermissionsOrAnonReadOnly.has_permission')
    def test_topping_list_unimplemented_methods_should_return_405(self, mock_permission):
        mock_permission.return_value = True
        request = self.factory.put("/toppings/", {'topping_name': 'data'}, format='json')
        response = self.topping_list_view(request)

        self.assertContains(response, status_code=405, text='Method \\"PUT\\" not allowed')


class TestPizzaToppingPermissions(TestCase):
    def test_view_should_return_403_when_unauthorized_user_tries_to_use_write_methods(self):
        pass
    def test_members_of_owner_group_should_have_permission_to_add_delete_view_change_model(self):
        pass
    