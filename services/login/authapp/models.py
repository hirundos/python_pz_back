from django.db import models


class Member(models.Model):
    member_id = models.CharField(primary_key=True, max_length=100)
    member_pwd = models.CharField(max_length=100)
    member_nm = models.CharField(max_length=100)

    class Meta:
        db_table = "member"

    def __str__(self):
        return self.member_id


