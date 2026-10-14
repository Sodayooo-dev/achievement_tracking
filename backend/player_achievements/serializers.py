from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from player_achievements.models import PlayerAchievements
from player_games.models import PlayerGames


class PlayerAchievementsSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        player = attrs.get('player_id', getattr(self.instance, 'player_id', None))
        achievement = attrs.get('achievement_id', getattr(self.instance, 'achievement_id', None))
        changed = not self.instance or player.pk != self.instance.player_id_id or achievement.pk != self.instance.achievement_id_id
        if changed and not PlayerGames.objects.filter(player_id=player, game_id=achievement.game_id_id).exists():
            raise serializers.ValidationError({'achievement_id': ['Add this game to the player library before granting its achievements.']})
        return attrs

    class Meta:
        model = PlayerAchievements
        fields = '__all__'
        validators = [UniqueTogetherValidator(queryset=PlayerAchievements.objects.all(), fields=('player_id', 'achievement_id'), message='This player already has this achievement.')]
