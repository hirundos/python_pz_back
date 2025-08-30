from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class Member(models.Model):
    member_id = models.CharField(max_length=100, primary_key=True)
    member_pwd = models.CharField(max_length=100)  
    member_nm = models.CharField(max_length=100)

    class Meta:
        db_table = 'member'  

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False