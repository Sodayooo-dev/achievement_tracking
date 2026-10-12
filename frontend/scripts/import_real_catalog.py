"""Run with Django shell from backend/. Imports cached sources without network access.

Converts only [UI Test] rows, keeping their IDs, XP and unlock references. Adds authentic
definitions and official artwork; no player records, grants or libraries are deleted.
"""
import json
import re
from pathlib import Path
from django.db import transaction
from games.models import Games
from achievements.models import Achievements

root = Path('../frontend/data')
snapshot = json.loads((root / 'real_catalog.json').read_text(encoding='utf-8'))
console_art = json.loads((root / 'console_artwork.json').read_text(encoding='utf-8'))
console = json.loads((root / 'console_achievements.json').read_text(encoding='utf-8'))
def clean(text):
    return re.sub(r'\s+', ' ', re.sub(r'[™®\ufffd]', '', text)).strip()

for title, publisher, genre in [('Minecraft', 'Mojang Studios', 'Sandbox / Survival (Bedrock)'), ('Gran Turismo 7', 'Sony Interactive Entertainment', 'Driving')]:
    rows = console[title]['rows']
    definitions = [{'name': clean(row[2]), 'description': clean(row[3])} for row in rows if len(row) == 8 and row[2] and row[3]] if title == 'Minecraft' else [{'name': clean(row[0]), 'description': clean(row[1])} for row in rows]
    snapshot['games'].append({'match_title': title, 'title': title, 'publisher': publisher, 'genre': genre,
                              'image_url': console_art[title]['image_url'], 'achievements': definitions,
                              'sources': {'metadata': console_art[title]['source'], 'achievements': console[title]['source']}})

backup = root / 'before_real_catalog.json'
if not backup.exists():
    backup.write_text(json.dumps({'games': list(Games.objects.values()), 'achievements': list(Achievements.objects.values())}, indent=2), encoding='utf-8')

stats = {'created_games': 0, 'converted_achievements': 0, 'created_achievements': 0}
with transaction.atomic():
    for entry in snapshot['games']:
        title = clean(entry['title'])
        game = Games.objects.filter(title__in=[entry['match_title'], entry['title'], title]).order_by('id').first()
        if not game:
            game = Games(title=title)
            stats['created_games'] += 1
        game.title = title
        game.publisher = clean(entry['publisher'])[:100]
        game.genre = entry['genre']
        game.image_url = entry['image_url']
        game.save()
        fixtures = list(Achievements.objects.filter(game_id=game, name__startswith='[UI Test]').order_by('id'))
        existing = {clean(item.name): item for item in Achievements.objects.filter(game_id=game).exclude(name__startswith='[UI Test]')}
        seen = set()
        for definition in entry['achievements']:
            name, description = clean(definition['name']), clean(definition['description'])
            if not name or name in seen:
                continue
            if not description:
                description = 'Secret achievement — the official public list does not reveal its requirements.'
            if len(name) > 100:
                raise ValueError(f'Achievement name exceeds the existing model limit: {name}')
            seen.add(name)
            item = existing.get(name)
            if item:
                item.name = name
                item.description = description
            elif fixtures:
                item = fixtures.pop(0)
                item.name, item.description = name, description
                stats['converted_achievements'] += 1
            else:
                item = Achievements(game_id=game, name=name, description=description, exp_value=100)
                stats['created_achievements'] += 1
            item.save()
            existing[name] = item
        if fixtures:
            raise ValueError(f'{title}: not enough verified definitions to replace all test objectives')
        print(f'{title}: {len(seen)} real achievements; artwork saved')
    mobile = Games.objects.filter(title='Mobile Legends').first()
    if mobile and 'Mobile Legends' in console_art:
        mobile.image_url = console_art['Mobile Legends']['image_url']
        mobile.save(update_fields=['image_url'])

(root / 'catalog_sources.json').write_text(json.dumps([{'title': clean(e['title']), 'sources': e['sources'], 'image_url': e['image_url']} for e in snapshot['games']], indent=2), encoding='utf-8')
print('IMPORT_RESULT=' + json.dumps({**stats, 'catalog_games': Games.objects.count(), 'achievements': Achievements.objects.count(), 'remaining_test_objectives': Achievements.objects.filter(name__startswith='[UI Test]').count(), 'games_with_artwork': Games.objects.exclude(image_url='').count()}))
