"""Run via Django shell from backend/: download the catalog's current artwork into MEDIA_ROOT.

Original image bytes are preserved. Downloads are validated before updating each DB path.
Existing local files are reused, so repeat runs never depend on the remote host.
"""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from io import BytesIO
import json
from urllib.request import Request, urlopen
from PIL import Image
from django.core.files.base import ContentFile
from django.db import transaction
from games.models import Games

games = list(Games.objects.order_by('id'))

def download(game):
    if game.image and game.image.storage.exists(game.image.name):
        return game.pk, None, game.image.name
    if not game.image_url.startswith('https://'):
        raise ValueError(f'{game.title}: missing an HTTPS artwork source')
    with urlopen(Request(game.image_url, headers={'User-Agent': 'CartridgeHubArtworkImport/1.0'}), timeout=30) as response:
        data = response.read(5 * 1024 * 1024 + 1)
    if len(data) > 5 * 1024 * 1024:
        raise ValueError(f'{game.title}: artwork exceeds 5 MB')
    with Image.open(BytesIO(data)) as image:
        extension = {'JPEG': 'jpg', 'PNG': 'png', 'WEBP': 'webp'}.get(image.format)
        if not extension or image.width * image.height > 16_000_000:
            raise ValueError(f'{game.title}: unsupported artwork format or size')
        image.verify()
    name = f'game_icons/catalog-{game.pk}-{sha256(data).hexdigest()[:16]}.{extension}'
    return game.pk, data, name

with ThreadPoolExecutor(max_workers=4) as executor:
    downloads = list(executor.map(download, games))

with transaction.atomic():
    for game_id, data, name in downloads:
        game = Games.objects.get(pk=game_id)
        if data is not None and not game.image.storage.exists(name):
            name = game.image.storage.save(name, ContentFile(data))
        game.image.name = name
        game.image_url = ''
        game.save(update_fields=['image', 'image_url'])
        print(f'{game.title}: {game.image.url}')
print('LOCAL_ARTWORK_RESULT=' + json.dumps({'local_games': len(games), 'downloaded': sum(data is not None for _, data, _ in downloads), 'bytes': sum(len(data) for _, data, _ in downloads if data is not None)}))
