from django.urls import path

from player_achievements.views import PlayerAchievementsList, PlayerAchievementsCreate, PlayerAchievementsDetail

urlpatterns = [
    path('player_achievements/', PlayerAchievementsList.as_view()),
    path('player_achievements/new/', PlayerAchievementsCreate.as_view()),
    path('player_achievcements/<int:pk>/', PlayerAchievementsDetail.as_view()),
]