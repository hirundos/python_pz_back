from django.db import models


class Branch(models.Model):
    bran_id = models.CharField(primary_key=True, max_length=100)
    bran_nm = models.CharField(max_length=100)

    def __str__(self):
        return self.bran_id

    class Meta:
        db_table = "branch"
        app_label = 'orders'  # 명시적 app_label 설정


class Order(models.Model):
    order_id = models.CharField(primary_key=True, max_length=50)
    member_id = models.CharField(max_length=50)
    bran = models.ForeignKey(Branch, on_delete=models.DO_NOTHING, db_column="bran_id")
    date = models.CharField(max_length=50)
    time = models.CharField(max_length=50)

    def __str__(self):
        return self.order_id

    class Meta:
        db_table = "orders"
        app_label = 'orders'  # 명시적 app_label 설정


class OrderDetail(models.Model):
    order_detail_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_column="order_id")
    pizza_id = models.CharField(max_length=50)
    quantity = models.IntegerField()

    def __str__(self):
        return f"OrderDetail {self.order_detail_id}"

    class Meta:
        db_table = "order_detail"
        app_label = 'orders'  # 명시적 app_label 설정
