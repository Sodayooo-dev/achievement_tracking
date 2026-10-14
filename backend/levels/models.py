from django.db import models

class Levels(models.Model):
    id = models.AutoField(primary_key=True)
    number = models.IntegerField()
    exp_required = models.IntegerField()
    title = models.CharField(max_length=50)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('number',), name='unique_level_number'),
            models.UniqueConstraint(fields=('exp_required',), name='unique_level_threshold'),
            models.CheckConstraint(condition=models.Q(number__gte=1), name='level_number_positive'),
            models.CheckConstraint(condition=models.Q(exp_required__gte=0), name='level_xp_nonnegative'),
        ]
