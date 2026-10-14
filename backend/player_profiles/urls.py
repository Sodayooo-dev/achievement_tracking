from player_profiles.views import PlayerProfileLogin, PlayerProfileRegister, PlayerProfileDelete, PlayerProfileUpdate
from django.urls import path
from player_profiles.views import CurrentProfile, PlayerProfileList, PlayerProfileDetail
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('me/', CurrentProfile.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('players/', PlayerProfileList.as_view()),
    path('players/<int:pk>/', PlayerProfileDetail.as_view()),
    path('login/', PlayerProfileLogin.as_view()),
    path('register/', PlayerProfileRegister.as_view()),
    path('<int:pk>/delete/', PlayerProfileDelete.as_view()),
    path('<int:pk>/update/', PlayerProfileUpdate.as_view()),
]
