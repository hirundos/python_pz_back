from django.db import models

class Member(models.Model):
    member_id = models.CharField(max_length=100, primary_key=True)
    member_pwd = models.CharField(max_length=100)  
    member_nm = models.CharField(max_length=100)

    class Meta:
        db_table = 'member'  
