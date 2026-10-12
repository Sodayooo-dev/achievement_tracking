import json
import re
from html import unescape
from pathlib import Path
from urllib.request import Request, urlopen

sources = {'Minecraft': 'https://wiki.ronlab.site/content/minecraftwiki_en_all_maxi_2025-11/Achievement', 'Gran Turismo 7': 'https://www.gtplanet.net/gran-turismo-7-trophy-list-leaks-20220226/'}
result = {}
for title, url in sources.items():
    with urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30) as response:
        page = response.read().decode('utf-8', errors='replace')
    rows = []
    if title == 'Gran Turismo 7':
        for item in re.findall(r'<li\b[^>]*>(.*?)</li>', page, re.S | re.I):
            text = unescape(re.sub('<[^>]+>', '', item)).strip()
            if ' – ' in text:
                name, description = text.split(' – ', 1)
                if len(name) < 100 and len(description) < 500:
                    rows.append([name, description])
    for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>', page, re.S | re.I):
        cells = re.findall(r'<td\b[^>]*>(.*?)</td>', row, re.S | re.I)
        text = [unescape(re.sub('<[^>]+>', ' ', c)).strip() for c in cells]
        if title == 'Minecraft' and len(text) >= 3:
            rows.append(text)
        elif title == 'Gran Turismo 7' and cells:
            name = re.search(r'<strong>(.*?)</strong>', cells[0], re.S)
            if name:
                before = cells[0].split('<br', 1)
                if len(before) == 2:
                    description = unescape(re.sub('<[^>]+>', ' ', before[1].split('>', 1)[-1])).strip()
                    rows.append([unescape(re.sub('<[^>]+>', '', name.group(1))).strip(), description])
    result[title] = {'source': url, 'rows': rows}
    print(title, len(rows), json.dumps(rows[:3]))
Path(__file__).resolve().parents[1].joinpath('data/console_achievements.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
