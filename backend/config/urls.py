from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

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
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
