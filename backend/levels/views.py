from config.api import ResourceList, ResourceCreate, ResourceDetail, ResourceUpdate, ResourceDelete
from levels.models import Levels
from levels.serializers import LevelsSerializer


class Configuration:
    model = Levels
    serializer_class = LevelsSerializer
    search_fields = ('title',)
    filter_fields = ()
    scope_player = False

    def queryset(self):
        return super().queryset().order_by('number')


class LevelsList(Configuration, ResourceList):
    pass


class LevelsCreate(Configuration, ResourceCreate):
    pass


class LevelsDetail(Configuration, ResourceDetail):
    pass


class LevelsUpdate(Configuration, ResourceUpdate):
    pass


class LevelsDelete(Configuration, ResourceDelete):
    pass
