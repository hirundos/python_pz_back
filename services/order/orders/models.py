from django.db import models


class Branch(models.Model):
    bran_id = models.CharField(primary_key=True, max_length=100)
    bran_nm = models.CharField(max_length=100)

    class Meta:
        db_table = "branch"


class Order(models.Model):
    order_id = models.CharField(primary_key=True, max_length=50)
    member_id = models.CharField(max_length=50)
    bran = models.ForeignKey(Branch, on_delete=models.DO_NOTHING, db_column="bran_id")
    date = models.CharField(max_length=50)
    time = models.CharField(max_length=50)

    class Meta:
        db_table = "orders"


class OrderDetail(models.Model):
    order_detail_id = models.IntegerField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_column="order_id")
    pizza_id = models.CharField(max_length=50)
    quantity = models.IntegerField()

    class Meta:
        db_table = "order_detail"
