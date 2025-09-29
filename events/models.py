from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.name
    

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events')
    participants = models.ManyToManyField(User, related_name='rsvped_events', blank=True)
    asset = models.ImageField(upload_to='event_asset/',blank=True,null=True) 

    def __str__(self):
        return self.name

    @property
    def is_upcoming(self):
        return self.date >= timezone.now().date()
