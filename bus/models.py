
from django.db import models
from login.models import *
from django.utils import timezone

# Create your models here.
class Route(models.Model):
    schedule_code = models.IntegerField(primary_key=True)
    campus1 = models.CharField(max_length=100,default="")
    campus2 = models.CharField(max_length=100,default="")

    def __str__(self):
        return f"{self.schedule_code} {self.campus1} and {self.campus2}"
    
class Bus(models.Model):
    bus_id = models.AutoField(primary_key=True)
    bus_name = models.CharField(max_length=255,null=False)
    campus_id = models.ForeignKey(Campus,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.bus_id} {self.bus_name}"

class Bus_schedule(models.Model):
    departure = models.CharField(max_length=255,null=False)
    destination = models.CharField(max_length=255,null=False)
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    duration = models.IntegerField()
    bus_id = models.ForeignKey(Bus,on_delete=models.CASCADE)
    schedule_code = models.ForeignKey(Route,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.schedule_code} {self.departure} to {self.destination}"


class Bus_Stats(models.Model):
    viewed_at = models.DateTimeField(default=timezone.now)
    schedule_code = models.ForeignKey(Route,on_delete=models.CASCADE)
    student_id = models.ForeignKey(Student,on_delete=models.CASCADE,null=True,blank=True)