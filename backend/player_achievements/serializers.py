from rest_framework import serializers
from player_achievements.models import PlayerAchievements


class PlayerAchievementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerAchievements
        fields = '__all__'
