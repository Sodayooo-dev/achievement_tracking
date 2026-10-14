from config.api import ResourceList, ResourceCreate, ResourceDetail, ResourceUpdate, ResourceDelete
from player_games.models import PlayerGames
from player_games.serializers import PlayerGamesSerializer


class Configuration:
    model = PlayerGames
    serializer_class = PlayerGamesSerializer
    search_fields = ('game_id__title', 'player_id__username',)
    filter_fields = ('game_id', 'player_id',)
    scope_player = True


class PlayerGamesList(Configuration, ResourceList):
    pass


class PlayerGamesCreate(Configuration, ResourceCreate):
    success_status = 201


class PlayerGamesDetail(Configuration, ResourceDetail):
    pass


class PlayerGamesUpdate(Configuration, ResourceUpdate):
    pass


class PlayerGamesDelete(Configuration, ResourceDelete):
    pass
