from django.db import models
from userapi.models import FitnessUser


class JogRecord(models.Model):
    jogger = models.ForeignKey(FitnessUser, on_delete=models.CASCADE, db_index=True)
    date = models.DateField(db_index=True, null=False)
    distance = models.FloatField(default=0, help_text="Distance covered in jog in meters")
    time = models.FloatField(default=0, help_text="Total jog time in seconds")
    location = models.CharField(max_length=255, null=False)
    weather = models.CharField(max_length=255, null=False)

    def __str__(self):
        return f"{self.date}: {self.jogger.username}: {self.time} seconds, {self.distance} meters, {self.location}, {self.weather}"





