from player_profiles.views import PlayerProfileLogin, PlayerProfileRegister, PlayerProfileDelete, PlayerProfileUpdate
from django.urls import path

urlpatterns = [
    path('login/', PlayerProfileLogin.as_view()),
    path('register/', PlayerProfileRegister.as_view()),
    path('<int:pk>/delete/', PlayerProfileDelete.as_view()),
    path('<int:pk>/update/', PlayerProfileUpdate.as_view()),
]