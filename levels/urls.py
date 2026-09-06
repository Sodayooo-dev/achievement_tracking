from django.urls import path
from levels.views import LevelsListCreate

urlpatterns = [
    path('levels/', LevelsListCreate.as_view()),
]