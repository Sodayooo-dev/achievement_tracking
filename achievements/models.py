from django.db import models

from games.models import Games


class Achievements(models.Model):
    id = models.AutoField(primary_key=True)
    game_id = models.ForeignKey(Games, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    description = models.TextField()
    exp_value = models.IntegerField()
