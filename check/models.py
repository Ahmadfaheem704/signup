# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Subscription(models.Model):
    PLAN_CHOICES = [
        ('Bachelor', 'Bachelor'),
        ('Master', 'Master'),
    ]
    
    DURATION_CHOICES = [
        ('1 Hour', '1 Hour'),
        ('7 Days', '7 Days'),
        ('1 Month', '1 Month'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan_type = models.CharField(max_length=10, choices=PLAN_CHOICES)
    duration = models.CharField(max_length=10, choices=DURATION_CHOICES)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()

    def is_active(self):
        return self.end_date > timezone.now()

class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    video_url = models.URLField()
    plan_type = models.CharField(max_length=10, choices=Subscription.PLAN_CHOICES)

    def __str__(self):
        return self.title
