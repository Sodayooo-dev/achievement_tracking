from django.urls import path
from achievements.views import AchievementsListCreate

urlpatterns = [
    path('achievements/', AchievementsListCreate.as_view()),
]