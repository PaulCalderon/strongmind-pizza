from unittest import skip
from unittest.mock import patch, MagicMock, ANY
from django.db import IntegrityError
from django.test import TestCase
# from django.contrib.auth.models import User, Permission
from django.urls import Resolver404, resolve
from django.http import Http404
from rest_framework import permissions
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory, force_authenticate
from pizza.models import PizzaTopping
from pizza.serializers import PizzaToppingSerializer
from pizza.views import ToppingList, ToppingDetails, Homepage


class TestPizzaToppingModel(TestCase):

    def setUp(self):
        self.topping_field = PizzaTopping._meta.get_field('topping')

    def test_model_should_have_topping_field(self):
        pizza_topping_fields = [field.name for field in PizzaTopping._meta.get_fields()]

        self.assertIn('topping', pizza_topping_fields)

    def test_topping_field_should_have_unique_constraint(self):

        self.assertTrue(self.topping_field.unique)

    def test_tooping_field_db_collation_should_be_set_nocase(self):
        """db_collation set to 'NOCASE' in sqlite3 ensures uniqueness is case insensitive"""

        self.assertEqual(self.topping_field.db_collation, 'NOCASE')

    def test_str_should_be_same_as_topping_field(self):
        """__str__ of the instance should be topping field"""
        topping_instance = PizzaTopping(topping='Bacon')

        self.assertEqual(str(topping_instance), 'Bacon')


class TestPizzaToppingSerializer(TestCase):

    def test_contains_additional_fields_declared_in_serializer(self):
        serializer = PizzaToppingSerializer()

        self.assertIn('url', serializer.fields)


class TestPizzaAppURLs(TestCase):
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

    def test_pizzas_list_url_is_correct(self):
        reverse_url = reverse(viewname='pizzas_list')
        resolve_url = resolve('/pizzas/')

        self.assertEqual(reverse_url, '/pizzas/')
        self.assertEqual(resolve_url.url_name, 'pizzas_list')

    def test_pizzas_detail_url_is_correct(self):
        reverse_url = reverse(viewname='pizzas_detail', kwargs={'pk':1})
        resolve_url = resolve('/pizzas/1')

        self.assertEqual(reverse_url, '/pizzas/1')
        self.assertEqual(resolve_url.url_name, 'pizzas_detail')
        self.assertDictEqual(resolve_url.kwargs, {'pk':1})


class TestHomepage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.factory = APIRequestFactory()
        cls.homepage_view = Homepage.as_view()

    @patch('pizza.views.reverse')
    def test_homepage_response_should_contain_reversed_links(self, mock_reverse):
        mock_reverse.return_value = 'reversed_link'
        request = self.factory.get('/')
        response = self.homepage_view(request)

        self.assertEqual(response.data, {'Topping List': 'reversed_link', 'Pizza List': 'reversed_link'})
        self.assertEqual(response.status_code, 200)


class TestPizzaToppingListView(TestCase):
    """Tests ToppingList class views"""

    @classmethod
    def setUpTestData(cls):
        cls.factory = APIRequestFactory()
        cls.topping_list_view = ToppingList.as_view()

    @patch('pizza.views.ToppingList.get_queryset')  # bit complicated to mock return of get_queryset
    @patch('pizza.views.PizzaToppingSerializer')
    def test_get_should_return_topping_list(self, mock_serializer, mock_get_queryset):
        """Checks if serializer processed queryset and returns serialized data."""
        get_queryset_instance = mock_get_queryset.return_value
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.data = 'topping list'
        request = self.factory.get('/')
        response = self.topping_list_view(request)

        mock_serializer.assert_called_with(get_queryset_instance, many=ANY, context=ANY)
        self.assertContains(response, status_code=200, text='topping list')

    @patch('pizza.views.ToppingList.get_queryset')  # bit complicated to mock return of get_queryset
    @patch('pizza.views.PizzaToppingSerializer')
    def test_get_should_allow_anonymous_users_to_see_topping_list(self, mock_serializer, mock_get_queryset):
        mock_instance = mock_serializer.return_value
        mock_instance.data = 'topping list'
        request = self.factory.get('/')
        response = self.topping_list_view(request)
        
        self.assertTrue(request.user.is_anonymous)
        self.assertContains(response, status_code=200, text='topping list')

    @patch('pizza.views.permissions.DjangoModelPermissionsOrAnonReadOnly.has_permission')
    @patch('pizza.views.PizzaToppingSerializer')
    def test_post_can_be_used_by_authenticated_users_with_permissions(self, mock_serializer, mock_permission):
        """Mocks for permission to be granted. serializer.save() should be called"""
        mock_permission.return_value = True
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.data = 'topping data'
        request = self.factory.post("/toppings/", {'topping_name': 'data'}, format='json')
        response = self.topping_list_view(request)

        mock_serializer_instance.save.assert_called()  # serializer.save()
        self.assertNotContains(response, status_code=201, text='Authentication credentials were not provided')

    @patch('pizza.views.permissions.DjangoModelPermissionsOrAnonReadOnly.has_permission')
    @patch('pizza.views.PizzaToppingSerializer')
    def test_post_should_return_201_and_response_with_topping_data(self, mock_serializer, mock_permission):
        """Checks the response returned from post request"""
        mock_permission.return_value = True
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.data = 'topping data'
        request = self.factory.post("/toppings/", {'topping_name': 'data'}, format='json')
        response = self.topping_list_view(request)

        self.assertContains(response, status_code=201, text='topping data')

    @patch('pizza.views.PizzaToppingSerializer')
    def test_post_should_return_403_if_user_is_unauthenticated(self, mock_serializer):
        """When sent by an unathenticated user, exception will be raised before any code in the view is executed"""
        request = self.factory.post("/toppings/", {'topping_name': 'data'}, format='json')
        response = self.topping_list_view(request)

        mock_serializer.assert_not_called()
        self.assertContains(response, status_code=403, text='Authentication credentials were not provided')
    
    @patch('pizza.views.permissions.DjangoModelPermissionsOrAnonReadOnly.has_permission')
    @patch('pizza.views.PizzaToppingSerializer')
    def test_post_should_return_400_if_serializer_returns_invalid(self, mock_serializer, mock_permission):
        """Mocks serializer receiving invalid request via is_valid returning false."""
        mock_permission.return_value = True
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.errors = 'invalid data'  # serializer.errors
        mock_serializer_instance.is_valid.return_value = False

        request = self.factory.post("/toppings/", {'error': 'error'}, format='json')
        response = self.topping_list_view(request)

        mock_serializer_instance.save.assert_not_called()  # serializer.save()
        self.assertContains(response, status_code=400, text='invalid data')

    @patch('pizza.views.permissions.DjangoModelPermissionsOrAnonReadOnly.has_permission')
    def test_put_should_return_405(self, mock_permission):
        """Only GET and POST are implemented"""
        mock_permission.return_value = True
        request = self.factory.put("/toppings/", {'topping_name': 'data'}, format='json')
        response = self.topping_list_view(request)

        self.assertContains(response, status_code=405, text='Method \\"PUT\\" not allowed')

    @patch('pizza.views.permissions.DjangoModelPermissionsOrAnonReadOnly.has_permission')
    def test_delete_should_return_405(self, mock_permission):
        """Only GET and POST are implemented"""
        mock_permission.return_value = True
        request = self.factory.delete("/toppings/")
        response = self.topping_list_view(request)

        self.assertContains(response, status_code=405, text='Method \\"DELETE\\" not allowed')


class TestPizzaToppingDetailsView(TestCase):
    """ Tests ToppingDetails class views"""
        
    @classmethod
    def setUpTestData(cls):
        cls.factory = APIRequestFactory()
        cls.topping_detail_view = ToppingDetails.as_view()

    @patch.object(PizzaTopping.objects, 'get')
    def test_get_object_method_returns_retrieved_topping(self, mock_get_object):
        """Test overidden method"""
        mock_get_object.return_value = 'topping detail'
        topping_detail_instance = ToppingDetails()

        self.assertEqual(topping_detail_instance._get_object(pk=1), 'topping detail')

    @patch.object(PizzaTopping.objects, 'get')
    def test_get_object_method_returns_404_when_topping_does_not_exist(self, mock_get_object):
        """Test overidden method"""
        mock_get_object.side_effect = PizzaTopping.DoesNotExist
        topping_detail_instance = ToppingDetails()

        with self.assertRaises(Http404):
            topping_detail_instance._get_object(pk=1)

    @patch('pizza.views.PizzaTopping.objects.get')
    @patch('pizza.views.PizzaToppingSerializer')
    def test_get_should_return_individual_topping_details(self, mock_serializer, mock_get_object):
        """Checks if serializer processed topping query data and returns serialized data."""
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.data = 'topping data'
        mock_get_object.return_value = 'topping_query_data'
        pk = 1
        request = self.factory.get(f'/toppings/{pk}/')
        response = self.topping_detail_view(request, pk=pk)

        mock_serializer.assert_called_with('topping_query_data', context=ANY)
        self.assertContains(response, status_code=200, text='topping data')

    @patch('pizza.views.PizzaTopping.objects.get')
    @patch('pizza.views.PizzaToppingSerializer')
    def test_get_should_allow_anonymous_users_to_see_topping_details(self, mock_serializer, mock_get_object):
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.data = 'topping details'
        mock_get_object.return_value = 'topping_query_data'
        pk = 1
        request = self.factory.get(f'/toppings/{pk}/')
        response = self.topping_detail_view(request, pk=pk)

        self.assertTrue(request.user.is_anonymous)
        self.assertContains(response, status_code=200, text='topping details')

    @patch('pizza.views.PizzaTopping.objects.get')
    def test_get_should_return_404_if_topping_does_not_exist(self, mock_get_object):
        mock_get_object.side_effect = PizzaTopping.DoesNotExist
        pk = 1
        request = self.factory.get(f'/toppings/{pk}/')
        response = self.topping_detail_view(request, pk=pk)

        self.assertContains(response, status_code=404, text='Not found.')

    @patch('pizza.views.PizzaTopping.objects.get')
    @patch('pizza.views.permissions.DjangoModelPermissionsOrAnonReadOnly.has_permission')
    @patch('pizza.views.PizzaToppingSerializer')
    def test_put_can_be_used_by_authenticated_users_with_permissions(self, mock_serializer, mock_permission, mock_get_object):
        """Mocks for permission to be granted. serializer.save() should be called"""
        mock_permission.return_value = True
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.data = 'topping data'
        mock_serializer_instance.is_valid.return_value = True
        mock_get_object.return_value = 'topping_query_data'
        pk=1
        data = {'topping_name': 'data'}
        request = self.factory.put(f'/toppings/{pk}', data=data, format='json')
        response = self.topping_detail_view(request, pk=pk)

        mock_serializer_instance.save.assert_called()  # serializer.save()
        self.assertNotContains(response, status_code=200, text='Authentication credentials were not provided')

    @patch('pizza.views.PizzaTopping.objects.get')
    @patch('pizza.views.permissions.DjangoModelPermissionsOrAnonReadOnly.has_permission')
    @patch('pizza.views.PizzaToppingSerializer')
    def test_put_should_return_200_and_response_with_topping_data(self, mock_serializer, mock_permission, mock_get_object):
        """Checks the response returned from put request"""
        mock_permission.return_value = True
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.data = 'topping data'
        mock_serializer_instance.is_valid.return_value = True
        mock_get_object.return_value = 'topping_query_data'
        pk=1
        data = {'topping_name': 'data'}
        request = self.factory.put(f'/toppings/{pk}', data=data, format='json')
        response = self.topping_detail_view(request, pk=pk)

        self.assertContains(response, status_code=200, text='topping data')

    @patch('pizza.views.PizzaTopping.objects.get')
    @patch('pizza.views.permissions.DjangoModelPermissionsOrAnonReadOnly.has_permission')
    @patch('pizza.views.PizzaToppingSerializer')
    def test_put_should_return_400_if_serializer_returns_invalid(self, mock_serializer, mock_permission, mock_get_object):
        """Mocks serializer receiving invalid request via is_valid returning false."""
        mock_permission.return_value = True
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.errors = 'invalid data'  # serializer.errors
        mock_serializer_instance.is_valid.return_value = False
        mock_get_object.return_value = 'topping_query_data'
        pk=1
        data = 'invalid_data'
        request = self.factory.put(f'/toppings/{pk}', data=data, format='json')
        response = self.topping_detail_view(request, pk=pk)

        mock_serializer_instance.save.assert_not_called()  # serializer.save()
        self.assertContains(response, status_code=400, text='invalid data')

    @patch('pizza.views.PizzaTopping.objects.get')
    def test_put_should_return_403_if_user_is_unauthenticated(self, mock_get_object):
        """When sent by an unathenticated user, exception will be raised before any code in the view is executed"""
        pk = 1
        data = {'topping_name': 'data'}
        request = self.factory.put(f'/toppings/{pk}', data=data, format='json')
        response = self.topping_detail_view(request, pk=pk)

        mock_get_object.assert_not_called()
        self.assertTrue(request.user.is_anonymous)
        self.assertContains(response, status_code=403, text='Authentication credentials were not provided')

    @patch('pizza.views.PizzaTopping.objects.get')
    @patch('pizza.views.permissions.DjangoModelPermissionsOrAnonReadOnly.has_permission')
    def test_put_should_return_404_when_topping_does_not_exist(self, mock_permission, mock_get_object):
        """Objects.get raise exception to simulate non existent topping"""
        mock_permission.return_value = True
        mock_get_object.side_effect = PizzaTopping.DoesNotExist
        pk=1
        data = {'topping_name': 'data'}
        request = self.factory.put(f'/toppings/{pk}', data=data, format='json')
        response = self.topping_detail_view(request, pk=pk)

        self.assertContains(response, status_code=404, text='Not found')

    @patch('pizza.views.PizzaTopping.objects.get')
    @patch('pizza.views.permissions.DjangoModelPermissionsOrAnonReadOnly.has_permission')
    def test_delete_can_be_used_by_authenticated_users_with_permissions(self, mock_permission, mock_get_object):
        """Mocks for permission to be granted. topping.delete() should be called"""
        mock_permission.return_value = True
        mock_get_object.return_value = MagicMock()
        pk=1
        request = self.factory.delete(f'/toppings/{pk}', format='json')
        response = self.topping_detail_view(request, pk=pk)

        mock_get_object.return_value.delete.assert_called()  # topping.delete()
        self.assertNotContains(response, status_code=204, text='Authentication credentials were not provided')

    @patch('pizza.views.PizzaTopping.objects.get')
    @patch('pizza.views.permissions.DjangoModelPermissionsOrAnonReadOnly.has_permission')
    def test_valid_delete_should_return_204_and_sucess_message(self, mock_permission, mock_get_object):
        """Checks the response returned from delete request"""
        mock_permission.return_value = True
        mock_get_object.return_value = MagicMock()
        pk=1
        request = self.factory.delete(f'/toppings/{pk}', format='json')
        response = self.topping_detail_view(request, pk=pk)

        self.assertContains(response, status_code=204, text='Sucessfully Deleted')

    @patch('pizza.views.PizzaTopping.objects.get')
    def test_delete_should_return_403_for_unathenticated_user(self, mock_get_object):
        """When accessed by an unathenticated user, exception will be raised before any code in the view"""
        mock_get_object.return_value = MagicMock()
        pk=1
        request = self.factory.delete(f'/toppings/{pk}', format='json')
        response = self.topping_detail_view(request, pk=pk)

        # topping.delete() was not called
        mock_get_object.return_value.delete.assert_not_called()
        self.assertContains(response, status_code=403, text='Authentication credentials were not provided')

    @patch('pizza.views.PizzaTopping.objects.get')
    @patch('pizza.views.permissions.DjangoModelPermissionsOrAnonReadOnly.has_permission')
    def test_delete_should_return_404_when_topping_does_not_exist(self, mock_permission, mock_get_object):
        """Objects.get raise exception to simulate non existent topping"""
        mock_permission.return_value = True
        mock_get_object.side_effect = PizzaTopping.DoesNotExist
        pk=1
        request = self.factory.delete(f'/toppings/{pk}', format='json')
        response = self.topping_detail_view(request, pk=pk)

        self.assertContains(response, status_code=404, text='Not found')

    @patch('pizza.views.permissions.DjangoModelPermissionsOrAnonReadOnly.has_permission')
    def test_post_should_return_405(self, mock_permission):
        """Only GET, PUT and DELETE are implemented"""
        mock_permission.return_value = True

        request = self.factory.post("/toppings/", {'topping_name': 'data'}, format='json')
        response = self.topping_detail_view(request)

        self.assertContains(response, status_code=405, text='Method \\"POST\\" not allowed')

