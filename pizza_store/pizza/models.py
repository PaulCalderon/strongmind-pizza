from django.db import models


class PizzaTopping(models.Model): # TODO Change to Topping
    """Models a single PizzaTopping instance"""

    # db_collation is set to make the topping unique irregardless of case.
    # might only be applicable to sqlite3 database.
    topping = models.CharField(
                            max_length=200, unique=True,
                            error_messages={'unique':'Topping already exists'},
                            db_collation= 'NOCASE'
                            )
    def __str__(self):
        return str(self.topping)


class Pizza(models.Model):
    """Models a single Pizza instance"""

    pizza = models.CharField(
                            max_length=200, unique=True,
                            error_messages={'unique':'Pizza already exists'},
                            db_collation= 'NOCASE'
                            )
    toppings = models.ManyToManyField(PizzaTopping)

    def __str__(self):
        return str(self.pizza)
