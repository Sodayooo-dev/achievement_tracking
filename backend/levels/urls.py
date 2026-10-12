from django.urls import path
from levels.views import LevelsList, LevelsCreate, LevelsDetail, LevelsUpdate, LevelsDelete

urlpatterns = [
    path('levels/', LevelsList.as_view()),
    path('levels/new/', LevelsCreate.as_view()),
    path('levels/<int:pk>/', LevelsDetail.as_view()),
    path('levels/<int:pk>/update/', LevelsUpdate.as_view()),
    path('levels/<int:pk>/delete/', LevelsDelete.as_view()),
]