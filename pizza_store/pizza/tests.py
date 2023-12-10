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

class TestPizzaToppingDetailsView(TestCase):
        
    @classmethod
    def setUpTestData(cls):
        cls.factory = APIRequestFactory()
        cls.topping_detail_view = ToppingDetails.as_view()

    @patch.object(PizzaTopping.objects, 'get')
    def test_get_object_method_returns_404_when_object_does_not_exist(self, mock_get_object):
        """Test overidden method"""
        mock_get_object.side_effect = PizzaTopping.DoesNotExist
        topping_detail_instance = ToppingDetails()
        
        with self.assertRaises(Http404):
            topping_detail_instance._get_object(pk=1)

    @patch('pizza.views.PizzaTopping.objects.get')
    @patch('pizza.views.PizzaToppingSerializer')
    def test_get_should_retrieve_individual_topping_data(self, mock_serializer, mock_get_object): # Retest in integeration
        """Checks if get returns correct data."""
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.data = 'data'
        mock_get_object.return_value = 'topping_query_data'
        pk = 1
        request = self.factory.get(f'/toppings/{pk}/')
        response = self.topping_detail_view(request, pk=pk)

        mock_serializer.assert_called_with('topping_query_data', context=ANY)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, 'data')

    @patch('pizza.views.PizzaTopping.objects.get')
    @patch('pizza.views.PizzaToppingSerializer')
    def test_get_should_allow_anonymous_users_to_see_topping_list(self, mock_serializer, mock_get_object):
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.data = 'data'
        mock_get_object.return_value = 'topping_query_data'
        pk = 1
        request = self.factory.get(f'/toppings/{pk}/')
        response = self.topping_detail_view(request, pk=pk)

        self.assertTrue(request.user.is_anonymous)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, 'data')

    @patch('pizza.views.PizzaTopping.objects.get')
    def test_get_should_return_404_if_topping_does_not_exist(self, mock_get_object):
        mock_get_object.side_effect = PizzaTopping.DoesNotExist
        pk = 1
        request = self.factory.get(f'/toppings/{pk}/')
        response = self.topping_detail_view(request, pk=pk)

        self.assertEqual(response.status_code, 404)

    @patch('pizza.views.PizzaTopping.objects.get')
    @patch('pizza.views.permissions.DjangoModelPermissionsOrAnonReadOnly.has_permission')
    @patch('pizza.views.PizzaToppingSerializer')
    def test_put_can_be_used_by_authenticated_users_with_permissions(self, mock_serializer, mock_permission, mock_get_object):
        """Mocks serializer to return dummy data and permission to be granted"""
        mock_permission.return_value = True
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.data = 'data'
        mock_serializer_instance.is_valid.return_value = True
        mock_get_object.return_value = 'topping_query_data'
        pk=1
        data = {'topping_name': 'data'}
        request = self.factory.put(f'/toppings/{pk}', data=data, format='json')
        response = self.topping_detail_view(request, pk=pk)
        
        mock_serializer.assert_called_with('topping_query_data', data={'topping_name': 'data'}, partial=ANY, context=ANY)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, 'data')
    
    @patch('pizza.views.PizzaTopping.objects.get')
    def test_put_should_return_error_for_unathenticated_user(self, mock_get_object):
        """When accessed by an unathenticated user, exception will be raised before any code in the view"""
        pk = 1
        data = {'topping_name': 'data'}
        request = self.factory.put(f'/toppings/{pk}', data=data, format='json')
        response = self.topping_detail_view(request, pk=pk)

        # breakpoint()
        mock_get_object.assert_not_called()
        self.assertTrue(request.user.is_anonymous)
        self.assertEqual(response.data['detail'].code, 'not_authenticated')
        self.assertEqual(response.status_code, 403)

    @patch('pizza.views.PizzaTopping.objects.get')
    @patch('pizza.views.permissions.DjangoModelPermissionsOrAnonReadOnly.has_permission')
    @patch('pizza.views.PizzaToppingSerializer')
    def test_put_sucessfully_send_update_command(self, mock_serializer, mock_permission, mock_get_object):
        """Mocks serializer to return dummy data and permission to be granted"""
        mock_permission.return_value = True
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.data = 'data'
        mock_serializer_instance.is_valid.return_value = True
        mock_get_object.return_value = 'topping_query_data'
        pk=1
        data = {'topping_name': 'data'}
        request = self.factory.put(f'/toppings/{pk}', data=data, format='json')
        response = self.topping_detail_view(request, pk=pk)
        
        mock_serializer_instance.save.assert_called()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, 'data')
    
    @patch('pizza.views.PizzaTopping.objects.get')
    @patch('pizza.views.permissions.DjangoModelPermissionsOrAnonReadOnly.has_permission')
    @patch('pizza.views.PizzaToppingSerializer')
    def test_put_should_return_error_for_invalid_data(self, mock_serializer, mock_permission, mock_get_object):
        """Mocks serializer.is_valid() to simulate invalid data"""
        mock_permission.return_value = True
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.errors = 'invalid data'
        mock_serializer_instance.is_valid.return_value = False
        mock_get_object.return_value = 'topping_query_data'
        pk=1
        data = 'invalid_data'
        request = self.factory.put(f'/toppings/{pk}', data=data, format='json')
        response = self.topping_detail_view(request, pk=pk)

        mock_serializer.assert_called_with('topping_query_data', data='invalid_data', partial=ANY, context=ANY)
        self.assertEqual(response.data, 'invalid data')
        self.assertEqual(response.status_code, 400)

    @patch('pizza.views.PizzaTopping.objects.get')
    @patch('pizza.views.permissions.DjangoModelPermissionsOrAnonReadOnly.has_permission')
    def test_delete_can_be_used_by_authenticated_users_with_permissions(self, mock_permission, mock_get_object):
        """Mocks for permission to be granted. Also checks if """
        mock_permission.return_value = True
        mock_get_object.return_value = MagicMock()
        pk=1
        request = self.factory.delete(f'/toppings/{pk}', format='json')
        response = self.topping_detail_view(request, pk=pk)

        # topping.delete() was called
        mock_get_object.return_value.delete.assert_called()
        self.assertNotContains(response, status_code=204, text='Authentication credentials were not provided')
        self.assertNotEqual(response.status_code, 403)

    @patch('pizza.views.PizzaTopping.objects.get')
    def test_delete_should_return_error_for_unathenticated_user(self, mock_get_object):
    
        mock_get_object.return_value = MagicMock()
        pk=1
        request = self.factory.delete(f'/toppings/{pk}', format='json')
        response = self.topping_detail_view(request, pk=pk)
        
        # topping.delete() was not called
        mock_get_object.return_value.delete.assert_not_called()
        self.assertContains(response, status_code=403, text='Authentication credentials were not provided')
        
    @patch('pizza.views.PizzaTopping.objects.get')
    @patch('pizza.views.permissions.DjangoModelPermissionsOrAnonReadOnly.has_permission')
    def test_delete_sucessfully_send_delete_command(self, mock_permission, mock_get_object):
        """Mocks for permission to be granted"""
        mock_permission.return_value = True
        mock_get_object.return_value = MagicMock()
        pk=1
        request = self.factory.delete(f'/toppings/{pk}', format='json')
        response = self.topping_detail_view(request, pk=pk)

        # topping.delete() was called
        mock_get_object.return_value.delete.assert_called()
        self.assertEqual(response.data, 'Sucessfully Deleted')
        self.assertEqual(response.status_code, 204)
        
    @patch('pizza.views.PizzaTopping.objects.get')
    @patch('pizza.views.permissions.DjangoModelPermissionsOrAnonReadOnly.has_permission')
    def test_trying_to_delete_non_existent_topping_should_return_404(self, mock_permission, mock_get_object):
        """Objects.get raise exception to simulate non existent topping"""
        mock_permission.return_value = True
        mock_get_object.side_effect = PizzaTopping.DoesNotExist
        pk=1
        request = self.factory.delete(f'/toppings/{pk}', format='json')
        response = self.topping_detail_view(request, pk=pk)

        self.assertContains(response, 'Not found', status_code=404)

    @patch('pizza.views.permissions.DjangoModelPermissionsOrAnonReadOnly.has_permission')
    def test_unimplemented_methods_should_return_405(self, mock_permission):
        mock_permission.return_value = True
        request = self.factory.post("/toppings/", {'topping_name': 'data'}, format='json')
        response = self.topping_detail_view(request)

        self.assertContains(response, status_code=405, text='Method \\"POST\\" not allowed')


class TestPizzaToppingPermissions(TestCase):
    def test_view_should_return_403_when_unauthorized_user_tries_to_use_write_methods(self):
        pass
    def test_members_of_owner_group_should_have_permission_to_add_delete_view_change_model(self):
        pass
    