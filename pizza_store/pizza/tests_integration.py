from django.contrib.auth.models import User, Group, Permission
from django.test import TestCase
from rest_framework.test import APIClient
from pizza.models import Pizza, PizzaTopping




class TestHomepage(TestCase):
    def test_get_request_on_homepage_should_return_urls_to_pizza_and_topping(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('http://testserver/toppings/', response.data.values())
        self.assertIn('http://testserver/pizzas/', response.data.values())
    
    def test_view_should_be_limited_to_implemented_methods_otherwise_raise_405(self):
        response = self.client.put('/')
        self.assertContains(response, status_code=405, text='Method \\"PUT\\" not allowed')
        
        response = self.client.delete('/')
        self.assertContains(response, status_code=405, text='Method \\"DELETE\\" not allowed')

        response = self.client.post('/')
        self.assertContains(response, status_code=405, text='Method \\"POST\\" not allowed')

class TestPizzaToppingEndpoints(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner_user = User.objects.create_user(username='owner', password='pass')
        cls.chef_user = User.objects.create_user(username='chef', password='pass')
        chef_group, created = Group.objects.get_or_create(name='Pizza Chef')
        owner_group, created = Group.objects.get_or_create(name='Pizza Owner')

        view_topping = Permission.objects.get(codename='view_pizzatopping')
        add_topping = Permission.objects.get(codename='add_pizzatopping')
        change_topping = Permission.objects.get(codename='change_pizzatopping')
        delete_topping = Permission.objects.get(codename='delete_pizzatopping')
        view_pizza = Permission.objects.get(codename='view_pizza')
        add_pizza = Permission.objects.get(codename='add_pizza')
        change_pizza = Permission.objects.get(codename='change_pizza')
        delete_pizza = Permission.objects.get(codename='delete_pizza')
        owner_group.permissions.add(add_topping, view_topping, change_topping, delete_topping)
        chef_group.permissions.add(view_pizza, add_pizza, change_pizza, delete_pizza)

        # Users will now have permissions of their assigned group
        cls.owner_user.groups.add(owner_group)
        cls.chef_user.groups.add(chef_group)

        cls.client = APIClient()

    def setUp(self):
        """Sets up database to have 3 toppings initially"""
        PizzaTopping.objects.create(topping='Pepperoni')
        PizzaTopping.objects.create(topping='Bacon')
        PizzaTopping.objects.create(topping='Onion')

    def test_get_should_return_list_of_all_toppings(self):
        response = self.client.get('/toppings/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['topping'], 'Pepperoni')
        self.assertEqual(response.data[1]['topping'], 'Bacon')
        self.assertEqual(response.data[2]['topping'], 'Onion')
    
    def test_owner_should_have_full_permissions_to_make_changes_to_topping(self):
        self.assertTrue(self.owner_user.has_perm('pizza.view_pizzatopping'))
        self.assertTrue(self.owner_user.has_perm('pizza.add_pizzatopping'))
        self.assertTrue(self.owner_user.has_perm('pizza.change_pizzatopping'))
        self.assertTrue(self.owner_user.has_perm('pizza.delete_pizzatopping'))

    def test_get_return_empty_list_if_database_is_empty(self):
        PizzaTopping.objects.all().delete()
        response = self.client.get('/toppings/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])
        self.assertEqual(len(response.data), 0)

    def test_post_should_be_able_to_add_new_toppings_if_user_has_permission(self):
        post_data = {'topping' : 'Ham'}
        # Expected to fail. Logged in user does not have permission
        self.client.login(username='chef', password='pass')
        response = self.client.post('/toppings/', data=post_data)
        self.assertContains(response, status_code=403, text='You do not have permission to perform this action.')

        # Expected to succeed
        self.client.login(username='owner', password='pass')
        response = self.client.post('/toppings/', data=post_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['topping'], 'Ham')

        # check that topping Ham was saved to the database
        stored_toppings = PizzaTopping.objects.all()
        self.assertEqual(stored_toppings.values()[3]['topping'], 'Ham')

    def test_post_should_validate_input_and_return_error_if_request_is_invalid(self):
        """topping field is required for all toppings"""
        post_data = {'None existing field' : 'Bacon'}
        self.client.login(username='owner', password='pass')
        response = self.client.post('/toppings/', data=post_data)

        self.assertContains(response, status_code=400, text='This field is required')

    def test_get_should_be_able_to_retrieve_individual_topping_details(self):
        response_pepperoni = self.client.get('/toppings/1')
        response_bacon = self.client.get('/toppings/2')
        response_onion = self.client.get('/toppings/3')

        self.assertEqual(response_pepperoni.status_code, 200)
        self.assertDictContainsSubset( {'topping' : 'Pepperoni'}, response_pepperoni.data)
        self.assertEqual(response_bacon.status_code, 200)
        self.assertDictContainsSubset({'topping' : 'Bacon'}, response_bacon.data)
        self.assertEqual(response_onion.status_code, 200)
        self.assertDictContainsSubset({'topping' : 'Onion'}, response_onion.data)

    def test_put_should_be_able_to_update_a_topping_if_user_has_permission(self):
        """PUT should change Bacon topping to Ham and save to database"""
        post_data = {'topping' : 'Ham'}
        # Checks that topping to be edited isn't already 'Ham'
        stored_toppings = PizzaTopping.objects.all()
        self.assertNotEqual(stored_toppings.values()[1]['topping'], 'Ham')

        # Expected to fail. Logged in user does not have permission
        self.client.login(username='chef', password='pass')
        response = self.client.put('/toppings/2', data=post_data, content_type='application/json')
        self.assertContains(response, status_code=403, text='You do not have permission to perform this action.')

        # Expected to succeed
        self.client.login(username='owner', password='pass')
        response = self.client.put('/toppings/2', data=post_data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['topping'], 'Ham')

        # Check that topping was changed to Ham and saved to the database
        stored_toppings = PizzaTopping.objects.all()
        self.assertEqual(stored_toppings.values()[1]['topping'], 'Ham')

    def test_put_should_validate_input_and_return_error_if_request_is_invalid(self):
        put_data = {'None existing field' : 'Ham'}
        self.client.login(username='owner', password='pass')
        response = self.client.put('/toppings/2', data=put_data, content_type='application/json')

        self.assertContains(response, status_code=400, text='This field is required')

    def test_delete_should_be_able_to_delete_a_topping_if_user_has_permission(self):
        """Deletes topping Bacon and asserts it doesn't exist in the database"""
        # Checks that topping to be deleted exists
        stored_toppings = PizzaTopping.objects.all()
        self.assertEqual(stored_toppings.values()[1]['topping'], 'Bacon')

        # Expected to fail. Logged in user does not have permission
        self.client.login(username='chef', password='pass')
        response = self.client.delete('/toppings/2', content_type='application/json')
        self.assertContains(response, status_code=403, text='You do not have permission to perform this action.')

        # Expected to succeed
        self.client.login(username='owner', password='pass')
        response = self.client.delete('/toppings/2', content_type='application/json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, 'Sucessfully Deleted')

        # Check that topping was deleted from the database
        stored_toppings = PizzaTopping.objects.all()

        self.assertEqual(stored_toppings.values()[1]['topping'], 'Onion')
        with self.assertRaises(PizzaTopping.DoesNotExist):
            PizzaTopping.objects.get(topping='Bacon')

    def test_duplicate_toppings_should_not_be_allowed(self):
        """POST and PUT should not allow duplicate toppings"""
        self.client.login(username='owner', password='pass')
        duplicate_topping = {'topping' : 'Bacon'}
        response = self.client.post('/toppings/', data=duplicate_topping)
        self.assertContains(response, status_code=400, text='Topping already exists')

        response = self.client.put('/toppings/1', data=duplicate_topping, content_type='application/json')
        self.assertContains(response, status_code=400, text='Topping already exists')

    def test_view_should_be_limited_to_implemented_methods_otherwise_raise_405(self):
        """Trying to send an unimplemented method will return a 405"""
        self.client.login(username='owner', password='pass')
        topping_data = {'topping', 'Ham'}
        response = self.client.put('/toppings/', data=topping_data, content_type='application/json')
        self.assertContains(response, status_code=405, text='Method \\"PUT\\" not allowed')
        
        response = self.client.delete('/toppings/')
        self.assertContains(response, status_code=405, text='Method \\"DELETE\\" not allowed')

        response = self.client.post('/toppings/1')
        self.assertContains(response, status_code=405, text='Method \\"POST\\" not allowed')
    
    def test_trying_to_access_a_topping_with_no_entry_should_return_404(self):
        """_get_object method of PizzaToppingDetails should raise Http404"""
        topping_data = {'topping' : 'Ham'}
        self.client.login(username='owner', password='pass')
        response = self.client.get('/toppings/4')
        self.assertContains(response, status_code=404, text='Not found.')

        response = self.client.put('/toppings/4', data=topping_data, content_type='application/json')
        self.assertContains(response, status_code=404, text='Not found.')

        response = self.client.delete('/toppings/4')
        self.assertContains(response, status_code=404, text='Not found.')
