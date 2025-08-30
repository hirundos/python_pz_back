from django.db import models
from pizza_back.menu.models import Pizza

class Order(models.Model):
    order_id = models.CharField(max_length=50, primary_key=True)
    member_id = models.CharField(max_length=50)
    bran_id = models.CharField(max_length=100)
    date = models.CharField(max_length=50)
    time = models.CharField(max_length=50)

    class Meta:
        db_table = 'orders'  

class OrderDetail(models.Model):
    order_detail_id = models.IntegerField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_column='order_id')
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE, db_column='pizza_id')
    quantity = models.IntegerField()

    class Meta:
        db_table = 'order_detail'

class Branch(models.Model):
    bran_id = models.CharField(max_length=100, primary_key=True)
    bran_nm = models.CharField(max_length=100)

    class Meta:
        db_table = 'branch'