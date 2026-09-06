from django.urls import path

from games.views import GamesListCreate

urlpatterns = [
    path('games/', GamesListCreate.as_view()),
]