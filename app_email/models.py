from django.db import models


# Create your models here.
class EmailLog(models.Model):
    email_address = models.CharField(max_length=80)
    created = models.DateTimeField(auto_now_add=True)
