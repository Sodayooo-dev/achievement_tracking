from django.urls import path

from player_achievements.views import PlayerAchievementsList, PlayerAchievementsCreate, PlayerAchievementsDetail, PlayerAchievementsUpdate, PlayerAchievementsDelete

urlpatterns = [
    path('player_achievements/', PlayerAchievementsList.as_view()),
    path('player_achievements/new/', PlayerAchievementsCreate.as_view()),
    path('player_achievements/<int:pk>/', PlayerAchievementsDetail.as_view()),
    path('player_achievements/<int:pk>/update/', PlayerAchievementsUpdate.as_view()),
    path('player_achievements/<int:pk>/delete/', PlayerAchievementsDelete.as_view()),
]