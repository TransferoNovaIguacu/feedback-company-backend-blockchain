from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ContractedPlan
from missions.models import Mission

@receiver(post_save, sender=ContractedPlan)
def generate_missions(sender, instance, created, **kwargs):
    if created:
        # Lógica para gerar missões baseadas no plano contratado
        for i in range(instance.remaining_feedbacks):
            Mission.objects.create(
                mission_type='FEEDBACK',
                contracted_plan=instance,
                token_reward=instance.plan.token_value * instance.plan.reward_percentage,
            )
        
        for i in range(instance.remaining_quests):
            Mission.objects.create(
                mission_type='QUIZ',
                contracted_plan=instance,
                token_reward=instance.plan.token_value * instance.plan.reward_percentage,
            )