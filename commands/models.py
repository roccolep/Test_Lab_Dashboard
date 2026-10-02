from django.db import models

# Create your models here.

PRIORITY_CHOICES = [
    (0, 'Low'),
    (1, 'Medium'),
    (2, 'High'),
] 

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
] 
class Command(models.Model):
    name = models.CharField(max_length=255)
    payload = models.JSONField(blank=True, null=True)
    priority = models.IntegerField(default=0, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=255, default='pending', choices=STATUS_CHOICES)
    reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return self.name