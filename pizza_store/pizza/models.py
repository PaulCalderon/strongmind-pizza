from django.db import models

# Create your models here.

class PizzaTopping(models.Model):
    #db_collation is set to make the topping_name unique irregardless of case. 
    #might only be applicable to sqlite3 database.
    topping_name = models.CharField(max_length=200, unique=True, error_messages={'unique':'Topping already exists'}, db_collation= 'NOCASE')
    #TODO can hyperlink to pizzas using it

    def __str__(self):
        return str(self.topping_name)