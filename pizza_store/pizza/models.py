from django.db import models

# Create your models here.

class PizzaTopping(models.Model):
    """
    definition
    """
    # db_collation is set to make the topping_name unique irregardless of case.
    # might only be applicable to sqlite3 database.
    topping = models.CharField(max_length=200,
                                    unique=True,
                                    error_messages={'unique':'Topping already exists'},
                                    db_collation= 'NOCASE') #rename to topping


    #TODO can hyperlink to pizzas using it
    def __str__(self):
        return str(self.topping)

class Pizza(models.Model):
    """
    definition
    """
    pizza = models.CharField(max_length=200,
                                  unique=True,
                                  error_messages={'unique':'Pizza already exists'},
                                  db_collation= 'NOCASE') # rename to pizza
    # size = choicesfield here
    toppings = models.ManyToManyField(PizzaTopping)

    def __str__(self):
        return str(self.pizza)
