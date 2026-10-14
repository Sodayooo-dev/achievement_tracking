"""Disposable local browser QA server. No PostgreSQL reads or writes.

Run from backend/. Point a separate Vite process at CARTRIDGE_API_TARGET=http://127.0.0.1:8001.
The temporary SQLite database and artwork disappear when the server exits.
"""
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0, str(Path.cwd()))
os.environ['DJANGO_SETTINGS_MODULE'] = 'upload_test_settings'
from django.conf import settings
with TemporaryDirectory(prefix='cartridge-browser-qa-') as workspace:
    settings.DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': str(Path(workspace) / 'qa.sqlite3')}}
    settings.MEDIA_ROOT = Path(workspace) / 'media'
    import django
    django.setup()
    from django.core.management import call_command
    from django.core.files.base import ContentFile
    from roles.models import Roles
    from levels.models import Levels
    from games.models import Games
    from achievements.models import Achievements
    from player_profiles.models import PlayerProfiles
    from player_games.models import PlayerGames
    from player_achievements.models import PlayerAchievements
    call_command('migrate', verbosity=0)
    admin_role = Roles.objects.create(id=1, name='Admin')
    user_role = Roles.objects.create(id=2, name='User')
    level = Levels.objects.create(id=1, number=1, title='Noob', exp_required=1000)
    admin = PlayerProfiles.objects.create_user(username='qa-admin', password='QaConsole-Test-937!', role=admin_role, level=level)
    player = PlayerProfiles.objects.create_user(username='qa-player', password='QaConsole-Test-938!', role=user_role, level=level)
    for index, genre in enumerate(['Sandbox', 'RPG', 'Platformer', 'FPS', 'Fighting', 'Racing', 'Puzzle'], 1):
        game = Games.objects.create(title=f'QA {genre}', publisher='Test studio', genre=genre)
        original = next((Path.cwd() / 'media/game_icons').glob('*.jpg'))
        game.image.save(original.name, ContentFile(original.read_bytes()))
        for n in range(35):
            achievement = Achievements.objects.create(game_id=game, name=f'Objective {n+1}', description='Complete the objective. '+('A long description to verify the detail panel scrolls without moving the screen. ' * 25 if n==1 else 'Use keyboard or touch to inspect.'), exp_value=100)
            if index<=2 and n<3:
                PlayerGames.objects.get_or_create(player_id=player, game_id=game)
                PlayerAchievements.objects.create(player_id=player, achievement_id=achievement, acquired_date='2026-10-14')
    print('Disposable QA server: qa-admin / QaConsole-Test-937!; qa-player / QaConsole-Test-938!', flush=True)
    call_command('runserver', '127.0.0.1:8001', use_reloader=False)
