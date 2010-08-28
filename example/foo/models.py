from django.db import models

# Create your models here.

class Bar(models.Model):
    f1 = models.CharField(max_length=255)

