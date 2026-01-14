from django.db import models

from login.models import Admin


# Create your models here.
class CampusLocation(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True, null=True)  # store Cloudinary image URL here
    icon = models.CharField(max_length=50, default='building')
    latitude = models.FloatField()
    longitude = models.FloatField()
    admin_id = models.ForeignKey(Admin, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

