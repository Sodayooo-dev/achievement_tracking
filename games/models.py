from django.db import models

class Games(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    publisher = models.CharField(max_length=100)
    genre = models.CharField(max_length=100)