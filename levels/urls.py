from django.urls import path
from levels.views import LevelsList, LevelsCreate, LevelsDetail

urlpatterns = [
    path('levels/', LevelsList.as_view()),
    path('levels/new/', LevelsCreate.as_view()),
    path('levels/<int:pk>/', LevelsDetail.as_view()),
]