from django.contrib.auth.models import AbstractUser
from django.db import models

from levels.models import Levels


# Create your models here.
class PlayerProfiles(AbstractUser):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    level = models.ForeignKey(
        Levels,
        on_delete=models.PROTECT
    )