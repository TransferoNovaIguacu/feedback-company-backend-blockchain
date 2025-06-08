from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ContractedPlan
from missions.models import Mission

@receiver(post_save, sender=ContractedPlan)
def generate_missions(sender, instance, created, **kwargs):
    if created:
        plan = instance.plan
        company = instance.company
        expiration_date = instance.expiration_date

        # Gera missões do tipo Feedback
        for i in range(plan.feedbacks_available):
            Mission.objects.create(
                contracted_plan=instance,
                mission_type='FEEDBACK',
                title=f"Feedback {i+1} - {company.commercial_name}",
                description="Avaliação de produto",
                url=f"/feedback/{i+1}",
                status='PENDING'
            )

        # Gera missões do tipo Quiz
        for i in range(plan.quests_available):
            Mission.objects.create(
                contracted_plan=instance,
                mission_type='QUIZ',
                title=f"Quiz {i+1} - {company.commercial_name}",
                description="Desafio de conhecimento sobre o produto",
                url=f"/quiz/{i+1}",
                status='PENDING'
            )