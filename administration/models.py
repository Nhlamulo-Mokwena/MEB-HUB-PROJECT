from django.db import models
from login.models import Admin

# Create your models here.
class Admin_Action(models.Model):
  record_id = models.AutoField(primary_key=True)
  action_type = models.CharField(max_length=255,null=False)
  datetime = models.DateTimeField(auto_now=True)
  admin_id = models.ForeignKey(Admin,on_delete=models.CASCADE)
  
def __str__(self):
    return f"{self.record_id} {self.action_type} {self.datetime}"

