from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
from statistics import mean

from login.models import Campus, RegisteredStudent, Student  # Adjust as needed


class ScheduleCode(models.Model):
    schedule_code = models.IntegerField(primary_key=True)
    campus1 = models.CharField(max_length=100, default="")
    campus2 = models.CharField(max_length=100, default="")
    distance_km = models.FloatField(null=True, blank=True)  # Added for speed calculation

    def __str__(self):
        return f"{self.schedule_code} {self.campus1} and {self.campus2}"


class Bus(models.Model):
    bus_id = models.AutoField(primary_key=True)
    bus_name = models.CharField(max_length=255, null=False)
    campus_id = models.ForeignKey(Campus, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.bus_id} {self.bus_name}"


class Bus_schedule(models.Model):
    departure = models.CharField(max_length=255, null=False)
    destination = models.CharField(max_length=255, null=False)
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    duration = models.IntegerField()  # in minutes (automatically calculated)
    bus_id = models.ForeignKey(Bus, on_delete=models.CASCADE)
    schedule_code = models.ForeignKey(ScheduleCode, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.schedule_code} {self.departure} to {self.destination}"

    def save(self, *args, **kwargs):
        # Auto-calculate duration in minutes
        dep_dt = datetime.combine(datetime.today(), self.departure_time)
        arr_dt = datetime.combine(datetime.today(), self.arrival_time)

        # Handle overnight trips
        if arr_dt < dep_dt:
            arr_dt += timedelta(days=1)

        self.duration = int((arr_dt - dep_dt).total_seconds() / 60)
        super().save(*args, **kwargs)

    @property
    def duration_minutes(self):
        return self.duration

    @property
    def speed_kmph(self):
        """
        Dynamically calculates average speed if distance is set.
        """
        if self.schedule_code.distance_km and self.duration:
            hours = self.duration / 60
            return round(self.schedule_code.distance_km / hours, 2)
        return None

    @property
    def estimated_average_delay_minutes(self):
        """
        Calculates average delay based on actual arrival logs.
        """
        related_stats = Bus_Stats.objects.filter(
            schedule_code=self.schedule_code,
            actual_arrival_time__isnull=False
        )

        delays = []
        for stat in related_stats:
            scheduled = datetime.combine(datetime.today(), self.arrival_time)
            actual = datetime.combine(datetime.today(), stat.actual_arrival_time)
            delta_minutes = (actual - scheduled).total_seconds() / 60
            delays.append(delta_minutes)

        return round(mean(delays), 2) if delays else 0

    @property
    def views_count(self):
        return Bus_Stats.objects.filter(schedule_code=self.schedule_code).count()


class Bus_Stats(models.Model):
    viewed_at = models.DateTimeField(default=timezone.now)
    schedule_code = models.ForeignKey(ScheduleCode, on_delete=models.CASCADE)
    actual_arrival_time = models.TimeField(null=True, blank=True)  # New field for logging actual arrival

    def __str__(self):
        return f"Viewed at {self.viewed_at} for {self.schedule_code}"
