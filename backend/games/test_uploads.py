from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from games.models import Games
from levels.models import Levels
from roles.models import Roles
from player_profiles.models import PlayerProfiles


def icon(name='icon.png', image_format='PNG'):
    stream = BytesIO()
    Image.new('RGB', (32, 32), '#d7263d').save(stream, format=image_format)
    return SimpleUploadedFile(name, stream.getvalue(), content_type=f'image/{image_format.lower()}')


class GameArtworkUploadTests(TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory(prefix='cartridge-upload-tests-')
        self.addCleanup(self.directory.cleanup)
        self.media = override_settings(MEDIA_ROOT=self.directory.name)
        self.media.enable()
        self.addCleanup(self.media.disable)
        level = Levels.objects.create(number=1, title='Test', exp_required=0)
        admin_role = Roles.objects.create(name='Admin')
        user_role = Roles.objects.create(name='User')
        self.admin = PlayerProfiles.objects.create_user(username='upload-admin', password='test-only', role=admin_role, level=level)
        self.player = PlayerProfiles.objects.create_user(username='upload-player', password='test-only', role=user_role, level=level)
        self.client = APIClient()
        self.client.force_authenticate(self.admin)
        self.body = {'title': 'Artwork Test', 'publisher': 'Test Studio', 'genre': 'Puzzle'}

    def test_admin_multipart_upload_stores_original_bytes_and_relative_url(self):
        file = icon(name='icon.png')
        original = file.read()
        file.seek(0)
        response = self.client.post('/api/games/new/', {**self.body, 'image': file}, format='multipart')
        self.assertEqual(response.status_code, 200, response.data)
        game = Games.objects.get(pk=response.data['id'])
        self.assertTrue(game.image.name.endswith('.png'))
        self.assertTrue(Path(self.directory.name, game.image.name).is_file())
        with game.image.open('rb') as saved:
            self.assertEqual(saved.read(), original)
        self.assertEqual(response.data['image_url'], game.image.url)
        self.assertTrue(response.data['image_url'].startswith('/media/game_icons/'))
        listing = self.client.get('/api/games/')
        self.assertEqual(listing.data[0]['image_url'], game.image.url)

    def test_metadata_update_keeps_existing_image_and_upload_replaces_it(self):
        game = Games.objects.create(**self.body)
        first = self.client.put(f'/api/games/{game.pk}/update/', {**self.body, 'image': icon()}, format='multipart')
        self.assertEqual(first.status_code, 200, first.data)
        first_path = first.data['image_url']
        metadata = self.client.put(f'/api/games/{game.pk}/update/', {**self.body, 'title': 'Renamed'}, format='json')
        self.assertEqual(metadata.data['image_url'], first_path)
        second = self.client.put(f'/api/games/{game.pk}/update/', {**self.body, 'image': icon('replacement.webp', 'WEBP')}, format='multipart')
        self.assertEqual(second.status_code, 200, second.data)
        self.assertNotEqual(second.data['image_url'], first_path)
        self.assertTrue(second.data['image_url'].endswith('.webp'))

    def test_regular_player_and_anonymous_uploads_are_rejected(self):
        self.client.force_authenticate(self.player)
        self.assertEqual(self.client.post('/api/games/new/', {**self.body, 'image': icon()}, format='multipart').status_code, 403)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.post('/api/games/new/', {**self.body, 'image': icon()}, format='multipart').status_code, 401)
        self.assertEqual(Games.objects.count(), 0)

    def test_corrupt_unsupported_and_oversized_images_are_rejected(self):
        files = [SimpleUploadedFile('fake.png', b'<html>not an image</html>', content_type='image/png'), icon('image.gif', 'GIF')]
        oversized = icon()
        files.append(SimpleUploadedFile('large.png', oversized.read() + b'\0' * (5 * 1024 * 1024), content_type='image/png'))
        for file in files:
            with self.subTest(file=file.name):
                response = self.client.post('/api/games/new/', {**self.body, 'image': file}, format='multipart')
                self.assertEqual(response.status_code, 400, response.data)
                self.assertIn('image', response.data)
        self.assertEqual(Games.objects.count(), 0)
