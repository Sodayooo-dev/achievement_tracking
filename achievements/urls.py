from django.urls import path
from achievements.views import AchievementsList, AchievementsCreate, AchievementsDetail, AchievementsUpdate,AchievementsDelete

urlpatterns = [
    path('achievements/', AchievementsList.as_view()),
    path('achievements/new/', AchievementsCreate.as_view()),
    path('achievements/<int:pk>/', AchievementsDetail.as_view()),
    path('achievements/<int:pk>/update/', AchievementsUpdate.as_view()),
    path('achievements/<int:pk>/delete/', AchievementsDelete.as_view()),
]