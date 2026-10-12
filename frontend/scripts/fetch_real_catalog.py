"""Fetch public official Steam catalog metadata and achievement definitions. No API key needed."""
import html
import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

GAMES = [
    ('Terraria', 105600, 'Sandbox / Crafting'), ('Valheim', 892970, 'Survival'),
    ('The Elder Scrolls V: Skyrim', 489830, 'RPG'), ('Elden Ring', 1245620, 'Action RPG'),
    ("Baldur's Gate 3", 1086940, 'Role-playing'), ('Celeste', 504230, 'Platformer'),
    ('Hollow Knight', 367520, 'Platformer / Metroidvania'),
    ('Ori and the Will of the Wisps', 1057090, 'Platformer'), ('DOOM Eternal', 782330, 'FPS'),
    ('Titanfall 2', 1237970, 'Shooter'), ('Deep Rock Galactic', 548430, 'Co-op FPS'),
    ('Street Fighter 6', 1364780, 'Fighting'), ('Tekken 8', 1778820, 'Fighting'),
    ('Guilty Gear Strive', 1384160, 'Fighting'), ('Forza Horizon 5', 1551360, 'Racing'),
    ('Rocket League', 252950, 'Sports'), ('Stardew Valley', 413150, 'Farming / Simulation'),
    ('Portal 2', 620, 'Puzzle'), ('Hades', 1145360, 'Roguelike'),
    ('Assetto Corsa', 244210, 'Driving'), ("No Man's Sky", 275850, 'Survival / Sandbox'),
]

def get(url):
    with urlopen(Request(url, headers={'User-Agent': 'CartridgeHubCatalogImport/1.0'}), timeout=30) as response:
        return response.read().decode('utf-8', errors='replace')

def plain(value):
    return html.unescape(re.sub('<[^>]+>', '', value)).strip()

def fetch(entry):
    title, app_id, genre = entry
    store_source = f'https://store.steampowered.com/api/appdetails?appids={app_id}&l=english'
    metadata = json.loads(get(store_source))[str(app_id)]
    if not metadata.get('success'):
        raise RuntimeError(f'Steam metadata unavailable for {title}')
    data = metadata['data']
    achievement_source = f'https://steamcommunity.com/stats/{app_id}/achievements/?l=english'
    page = get(achievement_source)
    achievements = []
    for row in page.split('class="achieveRow')[1:]:
        name = re.search(r'<h3>(.*?)</h3>', row, re.S)
        description = re.search(r'<h5>(.*?)</h5>', row, re.S)
        if name and description:
            achievements.append({'name': plain(name.group(1)), 'description': plain(description.group(1))})
    # Some games have no achievements; do not manufacture objectives for them.
    result = {'match_title': title, 'title': data['name'], 'publisher': ', '.join(data.get('publishers', [])) or ', '.join(data.get('developers', [])),
              'genre': genre, 'image_url': data['header_image'], 'steam_app_id': app_id,
              'sources': {'metadata': store_source, 'achievements': achievement_source}, 'achievements': achievements}
    print(f'{title}: {len(achievements)} official achievements', flush=True)
    return result

if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=4) as executor:
        games = list(executor.map(fetch, GAMES))
    destination = Path(__file__).resolve().parents[1] / 'data' / 'real_catalog.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps({'fetched_at': datetime.now(timezone.utc).isoformat(), 'games': games}, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'Saved {len(games)} games to {destination}')
