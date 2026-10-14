from django.db import IntegrityError, transaction
from django.test import TestCase
from rest_framework.test import APIClient
from achievements.models import Achievements
from games.models import Games
from levels.models import Levels
from player_profiles.models import PlayerProfiles
from roles.models import Roles
from player_games.models import PlayerGames
from player_achievements.models import PlayerAchievements


class WorkflowTests(TestCase):
    def setUp(self):
        self.admin_role = Roles.objects.create(id=1, name='Admin')
        self.user_role = Roles.objects.create(id=2, name='User')
        self.level = Levels.objects.create(id=1, number=1, title='Noob', exp_required=1000)
        self.admin = PlayerProfiles.objects.create_user(username='admin', password='StrongTest-941!', role=self.admin_role, level=self.level)
        self.a = PlayerProfiles.objects.create_user(username='player-a', password='StrongTest-942!', role=self.user_role, level=self.level)
        self.b = PlayerProfiles.objects.create_user(username='player-b', password='StrongTest-943!', role=self.user_role, level=self.level)
        self.game = Games.objects.create(title='Test game', publisher='Studio', genre='Puzzle')
        self.achievement = Achievements.objects.create(game_id=self.game, name='Objective', description='Complete it', exp_value=100)
        self.client = APIClient()

    def auth(self, user):
        self.client.force_authenticate(user)

    def test_registration_rejects_privilege_fields_and_admin_role(self):
        body = {'username': 'new-player', 'password': 'ValidPassword-991!'}
        for field, value in [('role', 1), ('level', 999), ('is_superuser', True), ('is_staff', True), ('groups', []), ('user_permissions', [])]:
            with self.subTest(field=field):
                response = self.client.post('/api/register/', {**body, field: value}, format='json')
                self.assertEqual(response.status_code, 400)
        self.assertFalse(PlayerProfiles.objects.filter(username='new-player').exists())
        response = self.client.post('/api/register/', body, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        player = PlayerProfiles.objects.get(username='new-player')
        self.assertEqual(player.role_id, 2)
        self.assertEqual(player.level_id, 1)
        self.assertFalse(player.is_staff or player.is_superuser)
        self.assertNotIn('password', response.data)

    def test_password_validation_is_enforced(self):
        response = self.client.post('/api/register/', {'username':'weak', 'password':'123'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.auth(self.admin)
        response = self.client.put(f'/api/{self.a.pk}/update/', {'username':self.a.username, 'level':1, 'password':'123'}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_player_lists_are_scoped_even_with_another_player_filter(self):
        PlayerGames.objects.create(player_id=self.a, game_id=self.game)
        PlayerGames.objects.create(player_id=self.b, game_id=self.game)
        PlayerAchievements.objects.create(player_id=self.b, achievement_id=self.achievement, acquired_date='2026-10-14')
        self.auth(self.a)
        self.assertEqual(len(self.client.get('/api/player_games/').data), 1)
        self.assertEqual(self.client.get(f'/api/player_games/?player_id={self.b.pk}').data, [])
        self.assertEqual(self.client.get('/api/player_achievements/').data, [])
        self.auth(self.admin)
        self.assertEqual(len(self.client.get('/api/player_games/').data), 2)

    def test_self_library_is_idempotent_and_cannot_choose_another_player(self):
        self.auth(self.a)
        first = self.client.post('/api/me/library/', {'game_id':self.game.pk}, format='json')
        self.assertEqual(first.status_code, 201)
        second = self.client.post('/api/me/library/', {'game_id':self.game.pk}, format='json')
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.data['id'], second.data['id'])
        self.assertEqual(self.client.post('/api/me/library/', {'game_id':self.game.pk, 'player_id':self.b.pk}, format='json').status_code, 400)
        self.assertEqual(PlayerGames.objects.count(), 1)
        self.assertEqual(self.client.post('/api/me/library/', {'game_id':9999}, format='json').status_code, 400)

    def test_admin_player_lookup_me_and_authentication_guards(self):
        self.auth(self.a)
        self.assertEqual(self.client.get('/api/me/').data['id'], self.a.pk)
        self.assertEqual(self.client.get('/api/players/').status_code, 403)
        self.assertEqual(self.client.post('/api/achievements/new/', {}, format='json').status_code, 403)
        self.auth(None)
        for url in ['/api/players/', '/api/achievements/new/', '/api/player_games/new/']:
            response = self.client.get(url) if url.endswith('players/') else self.client.post(url, {})
            self.assertEqual(response.status_code, 401)
        self.auth(self.admin)
        response = self.client.get('/api/players/?page=1&page_size=1&search=player-b')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.b.pk)
        self.assertEqual(self.client.delete(f'/api/{self.admin.pk}/delete/').status_code,409)

    def test_grants_require_library_and_duplicates_are_rejected(self):
        self.auth(self.admin)
        body={'player_id':self.a.pk, 'achievement_id':self.achievement.pk, 'acquired_date':'2026-10-14'}
        self.assertEqual(self.client.post('/api/player_achievements/new/',body,format='json').status_code,400)
        PlayerGames.objects.create(player_id=self.a, game_id=self.game)
        self.assertEqual(self.client.post('/api/player_achievements/new/',body,format='json').status_code,200)
        self.assertEqual(self.client.post('/api/player_achievements/new/',body,format='json').status_code,400)
        self.assertEqual(self.client.post('/api/player_games/new/',{'player_id':self.a.pk,'game_id':self.game.pk},format='json').status_code,400)
        with self.assertRaises(IntegrityError), transaction.atomic():
            PlayerGames.objects.create(player_id=self.a,game_id=self.game)

    def test_validation_and_protected_deletes_return_actionable_errors(self):
        self.auth(self.admin)
        response=self.client.post('/api/achievements/new/',{'game_id':self.game.pk,'name':'Invalid','description':'XP','exp_value':-1},format='json')
        self.assertEqual(response.status_code,400)
        for body in [{'number':0,'exp_required':2000,'title':'Invalid'}, {'number':2,'exp_required':500,'title':'Invalid'}, {'number':1,'exp_required':2000,'title':'Duplicate'}]:
            self.assertEqual(self.client.post('/api/levels/new/',body,format='json').status_code,400)
        response=self.client.delete(f'/api/games/{self.game.pk}/delete/')
        self.assertEqual(response.status_code,409)
        self.assertTrue(response.data['dependencies'])
        self.assertTrue(Games.objects.filter(pk=self.game.pk).exists())

    def test_detail_responses_and_optional_pagination(self):
        self.auth(self.admin)
        self.assertEqual(self.client.get(f'/api/achievements/{self.achievement.pk}/').data['id'],self.achievement.pk)
        self.assertEqual(self.client.get('/api/achievements/9999/').status_code,404)
        self.assertEqual(self.client.get(f'/api/achievements/?game_id={self.game.pk}&page=1&page_size=1').data['count'],1)
        self.assertEqual(self.client.get('/api/achievements/?page=bad').status_code,400)
        self.assertIsInstance(self.client.get('/api/achievements/').data,list)
        second=Achievements.objects.create(game_id=self.game,name='Second',description='Later',exp_value=200)
        descending=self.client.get('/api/achievements/?page=1&ordering=-exp_value').data['results']
        self.assertEqual(descending[0]['id'],second.pk)

    def test_refresh_and_me_with_real_jwt_authentication(self):
        response=self.client.post('/api/login/',{'username':self.a.username,'password':'StrongTest-942!'},format='json')
        self.assertEqual(response.status_code,200)
        refreshed=self.client.post('/api/token/refresh/',{'refresh':response.data['tokens']['refresh']},format='json')
        self.assertEqual(refreshed.status_code,200)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+refreshed.data['access'])
        self.assertEqual(self.client.get('/api/me/').data['id'],self.a.pk)
        self.assertEqual(self.client.post('/api/token/refresh/',{'refresh':'invalid'},format='json').status_code,401)
