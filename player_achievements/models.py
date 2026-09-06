from django.db import models

from achievements.models import Achievements
from player_profiles.models import PlayerProfiles


class PlayerAchievements(models.Model):
    id = models.AutoField(primary_key=True)
    player_id = models.ForeignKey(PlayerProfiles, on_delete=models.PROTECT)
    achievement_id = models.ForeignKey(Achievements, on_delete=models.PROTECT)
    acquired_date = models.DateField()