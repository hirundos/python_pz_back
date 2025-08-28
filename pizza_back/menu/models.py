from django.db import models

class PizzaType(models.Model):
    pizza_type_id = models.CharField(max_length=50, primary_key=True)
    pizza_nm = models.CharField(max_length=50)
    pizza_categ = models.CharField(max_length=50)
    pizza_img_url = models.CharField(max_length=100)

    class Meta:
        db_table = 'pizza_types'  

class Pizza(models.Model):
    pizza_id = models.CharField(max_length=50, primary_key=True)
    pizza_type = models.ForeignKey(PizzaType, on_delete=models.CASCADE, db_column='pizza_type_id')
    size = models.CharField(max_length=50)
    price = models.FloatField()

    class Meta:
        db_table = 'pizza'  