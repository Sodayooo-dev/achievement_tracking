from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from player_profiles.models import PlayerProfiles
from roles.models import Roles
from levels.models import Levels


class PlayerProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = PlayerProfiles
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'role', 'level', 'created_at', 'updated_at', 'password')
        read_only_fields = ('id', 'role', 'created_at', 'updated_at')

    def validate_password(self, value):
        candidate = self.instance or PlayerProfiles(username=self.initial_data.get('username', ''))
        validate_password(value, user=candidate)
        return value

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for name, value in validated_data.items():
            setattr(instance, name, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class RegistrationSerializer(PlayerProfileSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta(PlayerProfileSerializer.Meta):
        read_only_fields = PlayerProfileSerializer.Meta.read_only_fields + ('level',)

    def validate(self, attrs):
        forbidden = {'is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions', 'last_login', 'date_joined'}
        errors = {name: ['This field cannot be set during registration.'] for name in forbidden if name in self.initial_data}
        for name, expected in (('role', getattr(settings, 'REGISTRATION_ROLE_ID', 2)), ('level', getattr(settings, 'REGISTRATION_LEVEL_ID', 1))):
            supplied = self.initial_data.get(name)
            if supplied is not None and str(supplied) != str(expected):
                errors[name] = ['The server assigns the starting role and level.']
        if errors:
            raise serializers.ValidationError(errors)
        attrs.pop('level', None)
        return attrs

    def create(self, validated_data):
        role = Roles.objects.filter(pk=getattr(settings, 'REGISTRATION_ROLE_ID', 2), name='User').first()
        level = Levels.objects.filter(pk=getattr(settings, 'REGISTRATION_LEVEL_ID', 1)).first()
        if not role or not level:
            raise serializers.ValidationError({'non_field_errors': ['Registration defaults are not configured. Contact an administrator.']})
        password = validated_data.pop('password')
        return PlayerProfiles.objects.create_user(password=password, role=role, level=level, **validated_data)


class SelfProfileSerializer(PlayerProfileSerializer):
    class Meta(PlayerProfileSerializer.Meta):
        read_only_fields = PlayerProfileSerializer.Meta.read_only_fields + ('level',)
