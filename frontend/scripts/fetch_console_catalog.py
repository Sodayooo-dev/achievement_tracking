"""Add verified console-only games to the imported Steam metadata snapshot."""
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen
from html import unescape

def get(url):
    with urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30) as response:
        return response.read().decode('utf-8', errors='replace')

path = Path(__file__).resolve().parents[1] / 'data' / 'real_catalog.json'
snapshot = json.loads(path.read_text(encoding='utf-8'))
ms_source = 'https://displaycatalog.mp.microsoft.com/v7.0/products?bigIds=9NBLGGH2JHXJ&market=US&languages=en-us'
product = json.loads(get(ms_source))['Products'][0]['LocalizedProperties'][0]
images = product['Images']
image = next((i for i in images if i['ImagePurpose'] == 'BoxArt'), next(i for i in images if i['ImagePurpose'] == 'Logo'))['Uri']
print('Minecraft image:', image)
sony_source = 'https://www.playstation.com/en-us/games/gran-turismo-7/'
sony = get(sony_source)
sony_image = re.search(r'<meta[^>]+(?:property|name)="og:image"[^>]+content="([^"]+)', sony)
if not sony_image:
    raise RuntimeError('PlayStation artwork not found')
print('Gran Turismo image:', unescape(sony_image.group(1)))
apple_source = 'https://itunes.apple.com/search?term=mobile%20legends%20bang%20bang&entity=software&limit=10&country=sg'
mobile = next(item for item in json.loads(get(apple_source))['results'] if item['trackName'].startswith('Mobile Legends: Bang Bang'))
Path(__file__).resolve().parents[1].joinpath('data/console_artwork.json').write_text(json.dumps({'Minecraft': {'image_url': 'https:' + image if image.startswith('//') else image, 'source': ms_source}, 'Gran Turismo 7': {'image_url': unescape(sony_image.group(1)), 'source': sony_source}, 'Mobile Legends': {'image_url': mobile['artworkUrl512'], 'source': apple_source}}, indent=2), encoding='utf-8')
