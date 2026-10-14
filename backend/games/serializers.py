from rest_framework import serializers

from games.models import Games

class GameSerializer(serializers.ModelSerializer):
    remove_image = serializers.BooleanField(write_only=True, required=False, default=False)

    def create(self, validated_data):
        validated_data.pop('remove_image', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        remove = validated_data.pop('remove_image', False)
        if remove:
            validated_data['image'] = ''
            validated_data['image_url'] = ''
        return super().update(instance, validated_data)

    def validate_image(self, value):
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('Choose an image up to 5 MB.')
        if value.image.format not in {'JPEG', 'PNG', 'WEBP'}:
            raise serializers.ValidationError('Choose a PNG, JPG or WebP image.')
        if value.image.width * value.image.height > 16_000_000:
            raise serializers.ValidationError('Image dimensions are too large (maximum 16 megapixels).')
        extension = {'JPEG': 'jpg', 'PNG': 'png', 'WEBP': 'webp'}[value.image.format]
        value.name = f'uploaded.{extension}'
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.image:
            data['image'] = instance.image.url
            data['image_url'] = instance.image.url
        return data

    class Meta:
        model = Games
        fields = '__all__'
