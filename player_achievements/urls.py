from django.urls import path

from player_achievements.views import PlayerAchievementsListCreate

urlpatterns = [
    path('player_achievements/', PlayerAchievementsListCreate.as_view()),
]