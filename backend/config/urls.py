from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('api/', include('games.urls')),
    path('api/', include('levels.urls')),
    path('api/', include('player_games.urls')),
    path('api/', include('player_profiles.urls')),
    path('api/', include('player_achievements.urls')),
    path('api/', include('achievements.urls')),
    path('api/', include('games.urls')),
]
