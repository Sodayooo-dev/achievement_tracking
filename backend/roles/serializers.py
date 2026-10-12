from rest_framework import serializers

from roles.models import Roles


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = '__all__'