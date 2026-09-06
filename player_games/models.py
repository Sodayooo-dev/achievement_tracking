from django.db import models

from games.models import Games
from player_profiles.models import PlayerProfiles


class PlayerGames(models.Model):
    id = models.AutoField(primary_key=True)
    game_id = models.ForeignKey(Games, on_delete=models.PROTECT)
    player_id = models.ForeignKey(PlayerProfiles, on_delete=models.PROTECT)