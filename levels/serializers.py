from rest_framework import serializers

from .models import Levels

class LevelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Levels
        fields = '__all__'