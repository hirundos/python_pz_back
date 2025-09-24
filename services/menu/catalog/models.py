from django.db import models


class PizzaType(models.Model):
    pizza_type_id = models.CharField(primary_key=True, max_length=50)
    pizza_nm = models.CharField(max_length=50)
    pizza_categ = models.CharField(max_length=50)
    pizza_img_url = models.CharField(max_length=100)

    class Meta:
        db_table = "pizza_types"
        app_label = 'catalog'  # 명시적 app_label 설정


class Pizza(models.Model):
    pizza_id = models.CharField(primary_key=True, max_length=50)
    pizza_type = models.ForeignKey(PizzaType, on_delete=models.DO_NOTHING, db_column="pizza_type_id")
    size = models.CharField(max_length=50)
    price = models.FloatField()

    class Meta:
        db_table = "pizza"
        app_label = 'catalog'  # 명시적 app_label 설정


