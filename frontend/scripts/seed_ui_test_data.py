"""Run through Django shell from backend/: exec(Path('../frontend/scripts/seed_ui_test_data.py').read_text()).

Creates additive, repeatable UI fixtures; never deletes data or changes backend source.
Objectives are UI test fixtures, not the games' official achievement lists.
"""
import json
import os
import secrets
from datetime import date, timedelta

from django.contrib.auth import authenticate
from django.db import transaction
from games.models import Games
from achievements.models import Achievements
from player_profiles.models import PlayerProfiles
from player_games.models import PlayerGames
from player_achievements.models import PlayerAchievements
from roles.models import Roles
from levels.models import Levels

GAMES = [
    ('Minecraft', 'Mojang Studios', 'Sandbox / Survival'),
    ('Terraria', 'Re-Logic', 'Sandbox / Crafting'),
    ('Valheim', 'Iron Gate Studio', 'Survival'),
    ('The Elder Scrolls V: Skyrim', 'Bethesda Game Studios', 'RPG'),
    ('Elden Ring', 'FromSoftware', 'Action RPG'),
    ("Baldur's Gate 3", 'Larian Studios', 'Role-playing'),
    ('Celeste', 'Maddy Makes Games', 'Platformer'),
    ('Hollow Knight', 'Team Cherry', 'Platformer / Metroidvania'),
    ('Ori and the Will of the Wisps', 'Moon Studios', 'Platformer'),
    ('DOOM Eternal', 'id Software', 'FPS'),
    ('Titanfall 2', 'Respawn Entertainment', 'Shooter'),
    ('Deep Rock Galactic', 'Ghost Ship Games', 'Co-op FPS'),
    ('Street Fighter 6', 'Capcom', 'Fighting'),
    ('Tekken 8', 'Bandai Namco Studios', 'Fighting'),
    ('Guilty Gear Strive', 'Arc System Works', 'Fighting'),
    ('Forza Horizon 5', 'Playground Games', 'Racing'),
    ('Rocket League', 'Psyonix', 'Sports'),
    ('Gran Turismo 7', 'Polyphony Digital', 'Driving'),
    ('Stardew Valley', 'ConcernedApe', 'Farming / Simulation'),
    ('Portal 2', 'Valve', 'Puzzle'),
    ('Hades', 'Supergiant Games', 'Roguelike'),
]

# Each tuple supplies a readable objective for the corresponding genre screen.
OBJECTIVES = {
    0: [
        ('First Shelter', 'Build a shelter before your first night.'),
        ('Tools of the Trade', 'Craft a complete set of basic tools.'),
        ('Deep Delver', 'Explore an underground cavern.'),
        ('A Growing Collection', 'Collect five different crafting materials.'),
        ('Home Sweet Home', 'Finish furnishing your first base.'),
        ('Into the Wild', 'Discover three different biomes.'),
        ('Rare Find', 'Bring a rare resource safely back to camp.'),
        ('Prepared for Anything', 'Craft equipment for your next expedition.'),
        ('A Helping Hand', 'Complete a building project with a friend.'),
        ('Night Watch', 'Survive a full night outside your shelter.'),
        ('Master Builder', 'Complete your most ambitious build yet.'),
        ('The Long Expedition', 'Return from a distant expedition with a full inventory.'),
    ],
    1: [
        ('The Journey Begins', 'Complete the opening chapter of your adventure.'),
        ('New Horizons', 'Discover a new region.'),
        ('Well Equipped', 'Upgrade a piece of equipment.'),
        ('Trusted Companion', 'Complete an objective with a companion.'),
        ('Side Quest Specialist', 'Complete five optional objectives.'),
        ('Scholar of the World', 'Read ten pieces of world lore.'),
        ('Power Within', 'Learn a new combat ability.'),
        ('Unexpected Treasure', 'Discover a hidden treasure.'),
        ('A Worthy Opponent', 'Defeat a formidable boss.'),
        ('Road Less Traveled', 'Finish an optional dungeon.'),
        ('Hero of the Realm', 'Resolve a major story conflict.'),
        ('Legend in the Making', 'Complete the final chapter.'),
    ],
    2: [
        ('First Steps', 'Clear the first area.'),
        ('Up and Over', 'Finish a challenging platforming section.'),
        ('Secret Passage', 'Find a hidden route.'),
        ('Collect Them All', 'Gather every collectible in an area.'),
        ('A New Technique', 'Unlock a movement ability.'),
        ('Perfect Landing', 'Complete a difficult jump sequence.'),
        ('No Looking Back', 'Finish a section without falling.'),
        ('The Scenic Route', 'Explore an optional area.'),
        ('Against the Odds', 'Complete a boss encounter.'),
        ('Speed Runner', 'Beat your previous best clear time.'),
        ('One More Try', 'Clear a difficult optional challenge.'),
        ('Summit Reached', 'Complete the adventure.'),
    ],
    3: [
        ('Boots on the Ground', 'Complete your first mission.'),
        ('Target Acquired', 'Complete a precision combat objective.'),
        ('Fully Loaded', 'Try every available weapon category.'),
        ('Squad Goals', 'Complete a mission alongside a teammate.'),
        ('Tactical Advantage', 'Use the environment to win an encounter.'),
        ('Clear the Room', 'Finish an encounter without taking damage.'),
        ('Supply Run', 'Find a hidden supply cache.'),
        ('Against the Clock', 'Finish a timed objective.'),
        ('Holding the Line', 'Survive a defensive encounter.'),
        ('Field Specialist', 'Complete five optional objectives.'),
        ('Veteran Operative', 'Complete a mission on a higher difficulty.'),
        ('Mission Accomplished', 'Finish the campaign or a full operation.'),
    ],
    4: [
        ('Enter the Arena', 'Complete your first match.'),
        ('Know Your Fighter', 'Finish a character tutorial.'),
        ('Combo Starter', 'Land a multi-hit combo.'),
        ('Perfect Defense', 'Successfully defend against a difficult attack.'),
        ('Counter Play', 'Win a round using a counterattack.'),
        ('On a Roll', 'Win three matches in a session.'),
        ('New Challenger', 'Try a fighter outside your usual roster.'),
        ('Training Pays Off', 'Complete a combo challenge.'),
        ('Down to the Wire', 'Win a close final round.'),
        ('Clean Sweep', 'Win a match without losing a round.'),
        ('Tournament Ready', 'Complete a tournament or arcade run.'),
        ('Champion', 'Complete your personal mastery challenge.'),
    ],
    5: [
        ('On the Starting Grid', 'Complete your first event.'),
        ('Clean Driving', 'Finish an event with no penalties.'),
        ('Personal Best', 'Set a new personal record.'),
        ('Taking the Lead', 'Finish an event in first place.'),
        ('A New Ride', 'Try a new vehicle or setup.'),
        ('Photo Finish', 'Win a closely contested event.'),
        ('Perfect Line', 'Complete a difficult driving challenge.'),
        ('Going the Distance', 'Complete a long event.'),
        ('Team Player', 'Complete an event with a teammate.'),
        ('Podium Regular', 'Earn five podium finishes.'),
        ('Season Veteran', 'Complete a series of events.'),
        ('Hall of Fame', 'Finish your championship challenge.'),
    ],
    6: [
        ('A Fresh Start', 'Complete the opening objective.'),
        ('Curiosity Rewarded', 'Discover something off the main path.'),
        ('Getting the Hang of It', 'Complete five objectives.'),
        ('A Useful Discovery', 'Learn a new technique.'),
        ('Making Progress', 'Reach your first major milestone.'),
        ('A Familiar Face', 'Complete an objective with an ally.'),
        ('Hidden in Plain Sight', 'Find a secret in a familiar area.'),
        ('A Little Detour', 'Finish an optional challenge.'),
        ('Practice Makes Perfect', 'Improve on your previous performance.'),
        ('Everything in Its Place', 'Complete a collection or puzzle set.'),
        ('The Final Stretch', 'Reach the final major objective.'),
        ('A Story Worth Saving', 'Complete your adventure.'),
    ],
}

username = 'cartridge_tester'
marker_email = 'cartridge_tester@example.invalid'
created = {'games': 0, 'achievements': 0, 'library': 0, 'unlocks': 0}
password = None

with transaction.atomic():
    role = Roles.objects.get(pk=2)
    if role.name.lower() == 'admin':
        raise RuntimeError('Role 2 must be a normal user role.')
    starting_level = Levels.objects.order_by('exp_required', 'id').first()
    if not starting_level:
        raise RuntimeError('Create a starting level before seeding UI data.')
    profile, is_new = PlayerProfiles.objects.get_or_create(
        username=username,
        defaults={'role': role, 'level': starting_level, 'first_name': 'Cartridge',
                  'last_name': 'Tester', 'email': marker_email},
    )
    if not is_new and (profile.email != marker_email or profile.role_id != role.id):
        raise RuntimeError('This username already belongs to another account; nothing was changed.')
    if is_new:
        password = os.environ.get('CARTRIDGE_TEST_PASSWORD') or secrets.token_urlsafe(15)
        profile.set_password(password)
        profile.save(update_fields=['password'])
        assert authenticate(username=username, password=password).id == profile.id

    seeded_games = []
    for index, (title, publisher, genre) in enumerate(GAMES):
        game, new = Games.objects.get_or_create(title=title, defaults={'publisher': publisher, 'genre': genre})
        created['games'] += int(new)
        seeded_games.append(game)
        objectives = list(OBJECTIVES[index // 3])
        if index < 3:
            objectives += [(f'Building Milestone {n:02}', f'Complete building project {n} and stock its storage area.') for n in range(1, 16)]
        items = []
        for position, (name, description) in enumerate(objectives):
            # Prefix fixture names so existing real achievement data is never overwritten.
            item, new = Achievements.objects.get_or_create(
                game_id=game, name=f'[UI Test] {name}',
                defaults={'description': description, 'exp_value': 50 + (position % 6) * 25},
            )
            created['achievements'] += int(new)
            items.append(item)
        # Keep one game of each of the last three genre groups as an unowned catalog title.
        if index in (14, 17, 20):
            continue
        _, new = PlayerGames.objects.get_or_create(player_id=profile, game_id=game)
        created['library'] += int(new)
        if index in (0, 5):
            # Include any pre-existing objectives on these titles so completion really reaches 100%.
            items = list(Achievements.objects.filter(game_id=game).order_by('id'))
            unlocked_count = len(items)  # Two gold-foil, perfectly completed cartridges.
        elif index in (2, 8, 13):
            unlocked_count = 0  # Three untouched cartridges.
        else:
            unlocked_count = min(len(items) - 1, (3, 5, 8, 10)[index % 4])
        for position, item in enumerate(items[:unlocked_count]):
            acquired = date(2026, 10, 12) - timedelta(days=(index * 19 + position * 7) % 181)
            _, new = PlayerAchievements.objects.get_or_create(
                player_id=profile, achievement_id=item, defaults={'acquired_date': acquired},
            )
            created['unlocks'] += int(new)

owned = PlayerGames.objects.filter(player_id=profile).count()
unlocks = PlayerAchievements.objects.filter(player_id=profile)
xp = sum(Achievements.objects.filter(id__in=unlocks.values('achievement_id')).values_list('exp_value', flat=True))
print('UI_SEED_RESULT=' + json.dumps({
    'username': username, 'password': password if is_new else '(unchanged)',
    'player_id': profile.id, 'new_account': is_new, 'created': created,
    'fixture_games': len(seeded_games), 'owned_games': owned,
    'unlocked_achievements': unlocks.count(), 'total_xp': xp,
    'catalog_total': Games.objects.count(), 'achievement_total': Achievements.objects.count(),
}))
