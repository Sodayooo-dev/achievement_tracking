from config.api import ResourceList, ResourceCreate, ResourceDetail, ResourceUpdate, ResourceDelete
from achievements.models import Achievements
from achievements.serializers import AchievementsSerializer


class Configuration:
    model = Achievements
    serializer_class = AchievementsSerializer
    search_fields = ('name', 'description',)
    filter_fields = ('game_id',)
    scope_player = False


class AchievementsList(Configuration, ResourceList):
    pass


class AchievementsCreate(Configuration, ResourceCreate):
    pass


class AchievementsDetail(Configuration, ResourceDetail):
    pass


class AchievementsUpdate(Configuration, ResourceUpdate):
    pass


class AchievementsDelete(Configuration, ResourceDelete):
    pass


