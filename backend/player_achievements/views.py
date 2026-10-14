from config.api import ResourceList, ResourceCreate, ResourceDetail, ResourceUpdate, ResourceDelete
from player_achievements.models import PlayerAchievements
from player_achievements.serializers import PlayerAchievementsSerializer


class Configuration:
    model = PlayerAchievements
    serializer_class = PlayerAchievementsSerializer
    search_fields = ('achievement_id__name', 'player_id__username',)
    filter_fields = ('player_id', 'achievement_id',)
    scope_player = True


class PlayerAchievementsList(Configuration, ResourceList):
    pass


class PlayerAchievementsCreate(Configuration, ResourceCreate):
    pass


class PlayerAchievementsDetail(Configuration, ResourceDetail):
    pass


class PlayerAchievementsUpdate(Configuration, ResourceUpdate):
    pass


class PlayerAchievementsDelete(Configuration, ResourceDelete):
    pass
