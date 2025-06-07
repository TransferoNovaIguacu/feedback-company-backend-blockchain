from django.db import models
from django.contrib.auth import get_user_model
from companies.models import Company
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class Plan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    token_value = models.DecimalField(max_digits=20, decimal_places=2)
    feedbacks_available = models.PositiveIntegerField()
    quests_available = models.PositiveIntegerField()
    reward_percentage = models.DecimalField(max_digits=3, decimal_places=2, default=0.6)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class ContractedPlan(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='contracted_plans')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    purchase_date = models.DateTimeField(auto_now_add=True)
    remaining_feedbacks = models.PositiveIntegerField()
    remaining_quests = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    expiration_date = models.DateTimeField()

    def __str__(self):
        return f"{self.company.name} - {self.plan.name}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.remaining_feedbacks = self.plan.feedbacks_available
            self.remaining_quests = self.plan.quests_available
            if not self.expiration_date:
                self.expiration_date = timezone.now() + timedelta(days=30)  
        super().save(*args, **kwargs)

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expiration_date

    def decrement_feedback(self):
        if self.remaining_feedbacks > 0:
            self.remaining_feedbacks -= 1
            self.save()

    def decrement_quest(self):
        if self.remaining_quests > 0:
            self.remaining_quests -= 1
            self.save()

    class Meta:
        ordering = ['-purchase_date']