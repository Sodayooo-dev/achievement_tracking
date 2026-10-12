from django.db import models

class Levels(models.Model):
    id = models.AutoField(primary_key=True)
    number = models.IntegerField()
    exp_required = models.IntegerField()
    title = models.CharField(max_length=50)