from rest_framework import serializers
from achievements.models import Achievements


class AchievementsSerializer(serializers.ModelSerializer):
    exp_value = serializers.IntegerField(min_value=0)

    class Meta:
        model = Achievements
        fields = '__all__'
