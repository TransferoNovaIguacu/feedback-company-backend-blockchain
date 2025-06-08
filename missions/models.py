from django.db import models
from datetime import timedelta
from django.conf import settings
from plans.models import ContractedPlan
from users.models import User

class Mission(models.Model):
    MISSION_TYPES = [
        ('FEEDBACK', 'Feedback'),
        ('QUIZ', 'Quiz')
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('IN_PROGRESS', 'Em progresso'),
        ('COMPLETED', 'Concluída'),
        ('EXPIRED', 'Expirada')
    ]
    contracted_plan = models.ForeignKey(
        'plans.ContractedPlan',
        on_delete=models.CASCADE,
        related_name='missions'
    )
    mission_type = models.CharField(
        max_length=10,
        choices=MISSION_TYPES,
        default='FEEDBACK'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    url = models.URLField()
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    def __str__(self):
        return f"{self.title} ({self.mission_type})"

class Question(models.Model):
    mission = models.ForeignKey(
        Mission,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    options = models.JSONField(default=list)

    def __str__(self):
        return self.title

class MissionQueue(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='missions_in_progress'
    )
    mission = models.ForeignKey(
        Mission,
        on_delete=models.CASCADE
    )
    started_at = models.DateTimeField(auto_now_add=True)
    expires_in = models.DurationField(default=timedelta(minutes=30))

    def __str__(self):
        return f"{self.user.email} - {self.mission.title}"