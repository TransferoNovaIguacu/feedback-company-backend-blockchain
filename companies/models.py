from django.db import models
from users.models import User, UserType
from companies.validators import validate_cnpj
from django.utils import timezone
from django.core.exceptions import ValidationError
from validate_docbr import CNPJ

class Company(User):

    commercial_name = models.CharField(
        max_length=255,
        help_text="Nome fantasia da empresa.",
    )

    legal_name = models.CharField(
        max_length=255,
        help_text="Razão social da empresa.",
    )

    business_area = models.CharField(
        max_length=255,
        blank=True,
        help_text="Área de atuação da empresa.",
    )

    cnpj = models.CharField(
        max_length=14,
        unique=True,
        validators=[validate_cnpj],
        help_text="CNPJ da empresa (apenas números).",
    )

    website = models.URLField(
        max_length=200,
        blank=True,
        help_text="URL do site oficial da empresa.",
    )

    logo_url = models.URLField(
        blank=True,
        help_text="URL da logo da empresa.",
    )

    verified = models.BooleanField(
        default=False,
        help_text="Indica se a empresa foi verificada pela plataforma.",
    )

    tokens_balance = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        help_text="Saldo de tokens disponível para ações internas da empresa (off-chain).",
    )

    corporate_tax_id = models.CharField(
        max_length=20,
        blank=True,
        help_text="Inscrição estadual, municipal ou outro identificador fiscal.",
    )

    def __str__(self):
        return f"{self.commercial_name} (Company)"


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['-created_at']
        
    def clean(self):
        super().clean()
        if self.cnpj:
            self.cnpj = ''.join(filter(str.isdigit, self.cnpj))
            if not CNPJ().validate(self.cnpj):
                raise ValidationError({'cnpj': 'CNPJ inválido'})
        
    def save(self, *args, **kwargs):
        self.user_type = UserType.COMPANY
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def active_plan(self):
        return self.contracted_plans.filter(
            is_active=True,
            expiration_date__gte=timezone.now()
        ).first()

    @property
    def remaining_feedbacks(self):
        plan = self.active_plan
        return plan.remaining_feedbacks if plan else 0

    @property
    def remaining_quests(self):
        plan = self.active_plan
        return plan.remaining_quests if plan else 0
