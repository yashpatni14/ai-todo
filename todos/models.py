from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    ai_priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    ai_score = models.FloatField(default=0.0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-ai_score', 'deadline']