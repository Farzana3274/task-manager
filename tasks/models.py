from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateField()
    assigned_user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, related_name='created_tasks', on_delete=models.CASCADE)
    STATUS_CHOICES = [
        ('IN', 'Incomplete'),
        ('CO', 'Complete'),
    ]
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='IN')

    PRIORITY_CHOICES = [
        ('L', 'Low'),
        ('M', 'Medium'),
        ('H', 'High'),
    ]
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='M')

    def __str__(self):
        return self.title
