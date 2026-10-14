from django.db import models
from games.artwork import game_artwork_path

class Games(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    publisher = models.CharField(max_length=100)
    genre = models.CharField(max_length=100)
    image_url = models.URLField(max_length=2048, blank=True, default='')
    image = models.ImageField(upload_to=game_artwork_path, blank=True, default='')
