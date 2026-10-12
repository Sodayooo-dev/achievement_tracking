"""Read-only verification through the frontend's real API proxy.

Set CARTRIDGE_TEST_PASSWORD or enter the test account password at the prompt.
Optionally set CARTRIDGE_TEST_URL to the Vite URL (default: port 5174).
"""
import getpass
import json
import os
from urllib.request import Request, urlopen

base = os.environ.get('CARTRIDGE_TEST_URL', 'http://127.0.0.1:5174').rstrip('/')
password = os.environ.get('CARTRIDGE_TEST_PASSWORD') or getpass.getpass('UI test account password: ')

def request(path, body=None, access=None):
    headers = {'Content-Type': 'application/json'}
    if access:
        headers['Authorization'] = f'Bearer {access}'
    data = json.dumps(body).encode() if body is not None else None
    with urlopen(Request(base + '/api/' + path, data=data, headers=headers), timeout=15) as response:
        return json.load(response)

session = request('login/', {'username': 'cartridge_tester', 'password': password})
access = session['tokens']['access']
profile = session['profile']
assert profile['role'] == 2, 'Test profile must be a regular user.'
games = request('games/', access=access)
achievements = request('achievements/', access=access)
levels = request('levels/', access=access)
library = [row for row in request('player_games/', access=access) if row['player_id'] == profile['id']]
unlocks = [row for row in request('player_achievements/', access=access) if row['player_id'] == profile['id']]
unlocked_ids = {row['achievement_id'] for row in unlocks}
xp = sum(item['exp_value'] for item in achievements if item['id'] in unlocked_ids)
completed = []
untouched = []
for owned in library:
    items = [item for item in achievements if item['game_id'] == owned['game_id']]
    got = sum(item['id'] in unlocked_ids for item in items)
    title = next(game['title'] for game in games if game['id'] == owned['game_id'])
    if items and got == len(items):
        completed.append(title)
    if got == 0:
        untouched.append(title)
assert len(library) >= 18 and len(unlocks) >= 132
assert len(completed) >= 2 and len(untouched) >= 3
assert len({row['acquired_date'][:7] for row in unlocks}) >= 6
rank = max((level for level in levels if level['exp_required'] <= xp), key=lambda level: level['exp_required'], default=None)
print(json.dumps({'login': 'OK', 'player_id': profile['id'], 'catalog_games': len(games),
                  'achievements': len(achievements), 'owned_games': len(library),
                  'unlocks': len(unlocks), 'xp': xp, 'rank': rank['title'] if rank else 'Unranked',
                  'completed_games': completed, 'untouched_games': untouched,
                  'history_months': sorted({row['acquired_date'][:7] for row in unlocks})}, indent=2))
