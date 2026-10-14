from config.api import ResourceList, ResourceCreate, ResourceDetail, ResourceUpdate, ResourceDelete
from games.models import Games
from games.serializers import GameSerializer


class Configuration:
    model = Games
    serializer_class = GameSerializer
    search_fields = ('title', 'publisher', 'genre',)
    filter_fields = ()
    scope_player = False


class GamesList(Configuration, ResourceList):
    pass


class GamesCreate(Configuration, ResourceCreate):
    pass


class GamesDetail(Configuration, ResourceDetail):
    pass


class GamesUpdate(Configuration, ResourceUpdate):
    pass


class GamesDelete(Configuration, ResourceDelete):
    pass
