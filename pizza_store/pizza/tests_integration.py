from django.contrib.auth.models import User, Group, Permission
from django.test import TestCase
from rest_framework.test import APIClient
from pizza.models import Pizza, PizzaTopping
from pizza.views import ToppingDetails, PizzaDetails


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
    """Tests endpoints located at /toppings/ and /toppings/<int:pk>"""

    @classmethod
    def setUpTestData(cls):
        cls.owner_username = 'owner_created'
        cls.chef_username = 'chef_created'
        cls.owner_user = User.objects.create_user(username=cls.owner_username, password='pass')
        cls.chef_user = User.objects.create_user(username=cls.chef_username, password='pass')
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
        cls.topping_detail_view = ToppingDetails.as_view()
        cls.pizza_detail_view = PizzaDetails.as_view()


    def setUp(self):
        """Sets up database to have 3 toppings initially"""
        PizzaTopping.objects.create(topping='Pepperoni')
        PizzaTopping.objects.create(topping='Bacon')
        PizzaTopping.objects.create(topping='Onion')
    
    def test_owner_should_have_full_permissions_to_make_changes_to_topping(self):
        self.assertTrue(self.owner_user.has_perm('pizza.view_pizzatopping'))
        self.assertTrue(self.owner_user.has_perm('pizza.add_pizzatopping'))
        self.assertTrue(self.owner_user.has_perm('pizza.change_pizzatopping'))
        self.assertTrue(self.owner_user.has_perm('pizza.delete_pizzatopping'))

    def test_get_should_return_list_of_all_toppings(self):
        response = self.client.get('/toppings/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['topping'], 'Pepperoni')
        self.assertEqual(response.data[1]['topping'], 'Bacon')
        self.assertEqual(response.data[2]['topping'], 'Onion')

    def test_get_return_empty_list_if_database_is_empty(self):
        PizzaTopping.objects.all().delete()
        response = self.client.get('/toppings/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])
        self.assertEqual(len(response.data), 0)

    def test_post_should_be_able_to_add_new_toppings_if_user_has_permission(self):
        post_data = {'topping' : 'Ham'}

        # Expected to fail. User is not logged in
        response = self.client.post('/toppings/', data=post_data)
        self.assertContains(response, status_code=401, text='Authentication credentials were not provided.')

        # Expected to fail. Logged in user does not have permission
        self.client.login(username=self.chef_username, password='pass')
        response = self.client.post('/toppings/', data=post_data)
        self.assertContains(response, status_code=403, text='You do not have permission to perform this action.')

        # Expected to succeed
        self.client.login(username=self.owner_username, password='pass')
        response = self.client.post('/toppings/', data=post_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['topping'], 'Ham')

        # check that topping Ham was saved to the database
        stored_toppings = PizzaTopping.objects.all()
        self.assertEqual(stored_toppings.values()[3]['topping'], 'Ham')

    def test_post_should_validate_input_and_return_error_if_request_is_invalid(self):
        """topping field is required for all toppings"""
        post_data = {'None existing field' : 'Bacon'}
        self.client.login(username=self.owner_username, password='pass')
        response = self.client.post('/toppings/', data=post_data)

        self.assertContains(response, status_code=400, text='This field is required')
    
    def test_get_object_should_return_pizza_topping_object(self):
        topping_detail_instance = ToppingDetails()

        self.assertIsInstance(topping_detail_instance._get_object(pk=1), PizzaTopping)
        
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

        # Expected to fail. User is not logged in
        response = self.client.put('/toppings/2', data=post_data, content_type='application/json')
        self.assertContains(response, status_code=401, text='Authentication credentials were not provided.')

        # Expected to fail. Logged in user does not have permission
        self.client.login(username=self.chef_username, password='pass')
        response = self.client.put('/toppings/2', data=post_data, content_type='application/json')
        self.assertContains(response, status_code=403, text='You do not have permission to perform this action.')

        # Expected to succeed
        self.client.login(username=self.owner_username, password='pass')
        response = self.client.put('/toppings/2', data=post_data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['topping'], 'Ham')

        # Check that topping was changed to Ham and saved to the database
        stored_toppings = PizzaTopping.objects.all()
        self.assertEqual(stored_toppings.values()[1]['topping'], 'Ham')

    def test_put_should_validate_input_and_return_error_if_request_is_invalid(self):
        put_data = {'None existing field' : 'Ham'}
        self.client.login(username=self.owner_username, password='pass')
        response = self.client.put('/toppings/2', data=put_data, content_type='application/json')

        self.assertContains(response, status_code=400, text='This field is required')

    def test_delete_should_be_able_to_delete_a_topping_if_user_has_permission(self):
        """Deletes topping Bacon and asserts it doesn't exist in the database"""
        # Checks that topping to be deleted exists
        stored_toppings = PizzaTopping.objects.all()
        self.assertEqual(stored_toppings.values()[1]['topping'], 'Bacon')

        # Expected to fail. user is not logged in.
        response = self.client.delete('/toppings/2', content_type='application/json')
        self.assertContains(response, status_code=401, text='Authentication credentials were not provided.')

        # Expected to fail. Logged in user does not have permission
        self.client.login(username=self.chef_username, password='pass')
        response = self.client.delete('/toppings/2', content_type='application/json')
        self.assertContains(response, status_code=403, text='You do not have permission to perform this action.')

        # Expected to succeed
        self.client.login(username=self.owner_username, password='pass')
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
        self.client.login(username=self.owner_username, password='pass')
        duplicate_topping = {'topping' : 'Bacon'}
        response = self.client.post('/toppings/', data=duplicate_topping)
        self.assertContains(response, status_code=400, text='Topping already exists')

        response = self.client.put('/toppings/1', data=duplicate_topping, content_type='application/json')
        self.assertContains(response, status_code=400, text='Topping already exists')

    def test_view_should_be_limited_to_implemented_methods_otherwise_raise_405(self):
        """Trying to send an unimplemented method will return a 405"""
        self.client.login(username=self.owner_username, password='pass')
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
        self.client.login(username=self.owner_username, password='pass')
        response = self.client.get('/toppings/4')
        self.assertContains(response, status_code=404, text='Not found.')

        response = self.client.put('/toppings/4', data=topping_data, content_type='application/json')
        self.assertContains(response, status_code=404, text='Not found.')

        response = self.client.delete('/toppings/4')
        self.assertContains(response, status_code=404, text='Not found.')


class TestPizzaEndpoints(TestCase):
    """Tests endpoints located at /pizzas/ and /pizzas/<int:pk>"""

    @classmethod
    def setUpTestData(cls):
        cls.owner_username = 'owner_created'
        cls.chef_username = 'chef_created'
        cls.owner_user = User.objects.create_user(username=cls.owner_username, password='pass')
        cls.chef_user = User.objects.create_user(username=cls.chef_username, password='pass')
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
        """Sets up database to have 3 toppings and 2 pizzas initially"""
        pepperoni_topping = PizzaTopping.objects.create(topping='Pepperoni')
        bacon_topping = PizzaTopping.objects.create(topping='Bacon')
        onion_topping = PizzaTopping.objects.create(topping='Onion')
        pepperoni_pizza = Pizza.objects.create(pizza='Pepperoni Pizza')
        pepperoni_pizza.toppings.set([pepperoni_topping])
        bacon_and_onion_pizza = Pizza.objects.create(pizza='Bacon and Onion Pizza')
        bacon_and_onion_pizza.toppings.set([bacon_topping, onion_topping])

    def test_chef_should_have_full_permissions_to_make_changes_to_pizza(self):
        self.assertTrue(self.chef_user.has_perm('pizza.view_pizza'))
        self.assertTrue(self.chef_user.has_perm('pizza.add_pizza'))
        self.assertTrue(self.chef_user.has_perm('pizza.change_pizza'))
        self.assertTrue(self.chef_user.has_perm('pizza.delete_pizza'))

    def test_get_should_return_list_of_all_pizzas(self):
        response = self.client.get('/pizzas/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['pizza'], 'Pepperoni Pizza')
        self.assertEqual(response.data[0]['toppings'], ['Pepperoni'])
        self.assertEqual(response.data[1]['pizza'], 'Bacon and Onion Pizza')
        self.assertEqual(response.data[1]['toppings'], ['Bacon', 'Onion'])

    def test_get_return_empty_list_if_database_is_empty(self):
        Pizza.objects.all().delete()
        response = self.client.get('/pizzas/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])
        self.assertEqual(len(response.data), 0)

    def test_post_should_be_able_to_add_new_pizza_if_user_has_permission(self):
        post_data = {'pizza' : 'All Meat Pizza', 'toppings' : ['Pepperoni', 'Bacon']}

        # Expected to fail. User is not logged in.
        response = self.client.post('/pizzas/', data=post_data)
        self.assertContains(response, status_code=401, text='Authentication credentials were not provided.')

        # Expected to fail. Logged in user does not have permission
        self.client.login(username=self.owner_username, password='pass')
        response = self.client.post('/pizzas/', data=post_data)
        self.assertContains(response, status_code=403, text='You do not have permission to perform this action.')

        # Expected to succeed
        self.client.login(username=self.chef_username, password='pass')
        response = self.client.post('/pizzas/', data=post_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['pizza'], 'All Meat Pizza')
        self.assertEqual(response.data['toppings'], ['Pepperoni', 'Bacon'])

        # check that All Meat Pizza and associated toppings was saved to the database
        stored_pizzas = Pizza.objects.all()
        stored_pizzas_toppings = stored_pizzas[2].toppings.all()

        self.assertEqual(stored_pizzas.values()[2]['pizza'], 'All Meat Pizza')
        self.assertEqual(stored_pizzas_toppings.values()[0]['topping'], 'Pepperoni')
        self.assertEqual(stored_pizzas_toppings.values()[1]['topping'], 'Bacon')

    def test_post_should_validate_input_and_return_error_if_request_is_invalid(self):
        """pizza field is required for all pizzas"""
        post_data = {'None existing field' : 'All Meat Pizza', 'toppings' : ['Pepperoni', 'Bacon']}
        self.client.login(username=self.chef_username, password='pass')
        response = self.client.post('/pizzas/', data=post_data)

        self.assertContains(response, status_code=400, text='This field is required')

    def test_get_should_be_able_to_retrieve_individual_pizza_details(self):
        response_pepperoni_pizza = self.client.get('/pizzas/1')
        response_bacon_and_onion_pizza = self.client.get('/pizzas/2')

        self.assertEqual(response_pepperoni_pizza.status_code, 200)
        self.assertDictContainsSubset({'pizza' : 'Pepperoni Pizza'}, response_pepperoni_pizza.data)
        self.assertDictContainsSubset({'toppings' : ['Pepperoni']}, response_pepperoni_pizza.data)
        self.assertEqual(response_bacon_and_onion_pizza.status_code, 200)
        self.assertDictContainsSubset({'pizza' : 'Bacon and Onion Pizza'}, response_bacon_and_onion_pizza.data)
        self.assertDictContainsSubset({'toppings' : ['Bacon', 'Onion']}, response_bacon_and_onion_pizza.data)

    def test_get_object_should_return_pizza_object(self):
        pizza_detail_instance = PizzaDetails()

        self.assertIsInstance(pizza_detail_instance._get_object(pk=1), Pizza)

    def test_put_should_be_able_to_update_a_pizza_if_user_has_permission(self):
        """PUT should change Bacon and Onion pizza to Pepperoni and Onion Pizza and save to database"""
        put_data = {'pizza' : 'Pepperoni and Onion Pizza', 'toppings' : ['Pepperoni', 'Onion']}
        # Checks that topping to be edited isn't already 'Pepperoni and Onion Pizza'
        stored_pizzas = Pizza.objects.all()
        self.assertNotEqual(stored_pizzas.values()[1]['pizza'], 'Pepperoni and Onion Pizza')

        # Expected to fail. Logged in user does not have permission
        response = self.client.put('/pizzas/1', data=put_data, content_type='application/json')
        self.assertContains(response, status_code=401, text='Authentication credentials were not provided.')

        # Expected to fail. Logged in user does not have permission
        self.client.login(username=self.owner_username, password='pass')
        response = self.client.put('/pizzas/1', data=put_data, content_type='application/json')
        self.assertContains(response, status_code=403, text='You do not have permission to perform this action.')

        # Expected to succeed
        self.client.login(username=self.chef_username, password='pass')
        response = self.client.put('/pizzas/2', data=put_data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['pizza'], 'Pepperoni and Onion Pizza')

        # Check that pizza was changed to Pepperoni and Onion Pizza and saved to the database
        stored_toppings = Pizza.objects.all()
        stored_pizzas_toppings = stored_pizzas[1].toppings.all()

        self.assertEqual(stored_toppings.values()[1]['pizza'], 'Pepperoni and Onion Pizza')
        self.assertEqual(stored_pizzas_toppings.values()[0]['topping'], 'Pepperoni')
        self.assertEqual(stored_pizzas_toppings.values()[1]['topping'], 'Onion')

    def test_put_should_validate_input_and_return_error_if_request_is_invalid(self):
        put_data = {'None existing field' : 'Pepperoni and Onion Pizza', 'toppings' : ['Pepperoni', 'Onion']}
        self.client.login(username=self.chef_username, password='pass')
        response = self.client.put('/pizzas/1', data=put_data, content_type='application/json')

        self.assertContains(response, status_code=400, text='This field is required')

    def test_delete_should_be_able_to_delete_a_pizza_if_user_has_permission(self):
        """Deletes Pepperoni Pizza and checks it doesn't exist in the database"""
        # Checks that topping to be deleted exists
        stored_pizza = Pizza.objects.all()
        self.assertEqual(stored_pizza.values()[0]['pizza'], 'Pepperoni Pizza')

        # Expected to fail. User is not logged in.
        response = self.client.delete('/pizzas/1', content_type='application/json')
        self.assertContains(response, status_code=401, text='Authentication credentials were not provided.')

        # Expected to fail. Logged in user does not have permission
        self.client.login(username=self.owner_username, password='pass')
        response = self.client.delete('/pizzas/1', content_type='application/json')
        self.assertContains(response, status_code=403, text='You do not have permission to perform this action.')

        # Expected to succeed
        self.client.login(username=self.chef_username, password='pass')
        response = self.client.delete('/pizzas/1', content_type='application/json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, 'Sucessfully Deleted')

        # Check that topping was deleted from the database
        stored_pizza = Pizza.objects.all()

        self.assertEqual(stored_pizza.values()[0]['pizza'], 'Bacon and Onion Pizza')
        with self.assertRaises(Pizza.DoesNotExist):
            Pizza.objects.get(pizza='Pepperoni Pizza')

    def test_duplicate_pizzas_should_not_be_allowed(self):
        """POST and PUT should not allow duplicate toppings"""
        self.client.login(username=self.chef_username, password='pass')
        duplicate_pizza = {'pizza' : 'Pepperoni Pizza', 'toppings' : ['Pepperoni']}
        response = self.client.post('/pizzas/', data=duplicate_pizza)
        self.assertContains(response, status_code=400, text='Pizza already exists')

        response = self.client.put('/pizzas/2', data=duplicate_pizza, content_type='application/json')
        self.assertContains(response, status_code=400, text='Pizza already exists')

    def test_view_should_be_limited_to_implemented_methods_otherwise_raise_405(self):
        """Trying to send an unimplemented method will return a 405"""
        self.client.login(username=self.chef_username, password='pass')
        pizza_data = {'pizza' : 'All Meat Pizza', 'toppings' : ['Pepperoni', 'Bacon']}
        response = self.client.put('/pizzas/', data=pizza_data, content_type='application/json')
        self.assertContains(response, status_code=405, text='Method \\"PUT\\" not allowed')

        response = self.client.delete('/pizzas/')
        self.assertContains(response, status_code=405, text='Method \\"DELETE\\" not allowed')

        response = self.client.post('/pizzas/1', data=pizza_data)
        self.assertContains(response, status_code=405, text='Method \\"POST\\" not allowed')

    def test_trying_to_access_a_pizza_with_no_entry_should_return_404(self):
        """_get_object method of PizzaDetails should raise Http404"""
        pizza_data = {'pizza' : 'All Meat Pizza', 'toppings' : ['Pepperoni', 'Bacon']}
        self.client.login(username=self.chef_username, password='pass')
        response = self.client.get('/pizzas/3')
        self.assertContains(response, status_code=404, text='Not found.')

        response = self.client.put('/pizzas/3', data=pizza_data, content_type='application/json')
        self.assertContains(response, status_code=404, text='Not found.')

        response = self.client.delete('/pizzas/3')
        self.assertContains(response, status_code=404, text='Not found.')

    def test_editing_a_topping_should_apply_changes_to_existing_pizzas_with_the_topping(self):
        """Changes Bacon topping to Ham and checks if pizza topping was changed as well"""
        new_topping = {'topping' : 'Ham'}
        stored_pizzas = Pizza.objects.all()
        stored_pizzas_toppings = stored_pizzas[1].toppings.all()
        # Check current toppings of Bacon and Onion Pizza
        self.assertEqual(stored_pizzas_toppings.values()[0]['topping'], 'Bacon')
        self.assertEqual(stored_pizzas_toppings.values()[1]['topping'], 'Onion')

        self.client.login(username=self.owner_username, password='pass')
        response = self.client.put('/toppings/2', data=new_topping, content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # Checks that Bacon was changed to Ham in the pizza
        stored_pizzas = Pizza.objects.all()
        stored_pizzas_toppings = stored_pizzas[1].toppings.all()

        self.assertEqual(stored_pizzas_toppings.values()[0]['topping'], 'Ham')
        self.assertEqual(stored_pizzas_toppings.values()[1]['topping'], 'Onion')

    def test_deleting_a_topping_should_remove_it_from_any_pizzas_that_include_it(self):
        """Delete Bacon topping and checks if pizza topping was changed as well"""
        stored_pizzas = Pizza.objects.all()
        stored_pizzas_toppings = stored_pizzas[1].toppings.all()
        # Check current toppings of Bacon and Onion Pizza
        self.assertEqual(stored_pizzas_toppings.values()[0]['topping'], 'Bacon')
        self.assertEqual(stored_pizzas_toppings.values()[1]['topping'], 'Onion')
        self.assertEqual(len(stored_pizzas_toppings.values()), 2)

        self.client.login(username=self.owner_username, password='pass')
        response = self.client.delete('/toppings/2')
        self.assertEqual(response.status_code, 204)

        # Checks that Bacon was removed and only 1 topping is left
        stored_pizzas = Pizza.objects.all()
        stored_pizzas_toppings = stored_pizzas[1].toppings.all()

        self.assertEqual(stored_pizzas_toppings.values()[0]['topping'], 'Onion')
        self.assertEqual(len(stored_pizzas_toppings.values()), 1)

