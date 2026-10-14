from rest_framework import serializers
from levels.models import Levels


class LevelsSerializer(serializers.ModelSerializer):
    number = serializers.IntegerField(min_value=1)
    exp_required = serializers.IntegerField(min_value=0)

    def validate(self, attrs):
        number = attrs.get('number', getattr(self.instance, 'number', None))
        threshold = attrs.get('exp_required', getattr(self.instance, 'exp_required', None))
        others = Levels.objects.exclude(pk=self.instance.pk) if self.instance else Levels.objects.all()
        if others.filter(number=number).exists():
            raise serializers.ValidationError({'number': ['This level number already exists.']})
        if others.filter(exp_required=threshold).exists() or others.filter(number__lt=number, exp_required__gte=threshold).exists() or others.filter(number__gt=number, exp_required__lte=threshold).exists():
            raise serializers.ValidationError({'exp_required': ['XP thresholds must be unique and increase with level number.']})
        return attrs

    class Meta:
        model = Levels
        fields = '__all__'
