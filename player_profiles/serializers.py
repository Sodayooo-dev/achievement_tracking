from rest_framework import serializers

from player_profiles.models import PlayerProfiles


class PlayerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerProfiles
        fields = '__all__'
        extra_kwargs = {
            'password': {
                'write_only': True,
            }
        }

    def create(self, validated_data):
        password = validated_data.pop('password')

        profile = PlayerProfiles.objects.create(**validated_data)
        profile.set_password(password)
        profile.save()
        return profile

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
        instance.save()
        return instance