from django.db import models

class Games(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    publisher = models.CharField(max_length=100)
    genre = models.CharField(max_length=100)
    image_url = models.URLField(max_length=2048, blank=True, default='')
