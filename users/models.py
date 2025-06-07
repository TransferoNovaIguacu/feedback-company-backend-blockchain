from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from validate_docbr import CPF


class UserManager(BaseUserManager):
    
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('O email precisa ser informado.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser precisa ter is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser precisa ter is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class UserType(models.TextChoices):
    COMMON = "COMMON", "Common User"
    COMPANY = "COMPANY", "Company"
    STAFF = "STAFF", "Staff"
    ANALYST = "ANALYST", "Analyst"
    ADMIN = "ADMIN", "Admin"


class User(AbstractBaseUser, PermissionsMixin):
    
    username = None
    email = models.EmailField(_('email address'), unique=True)
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.COMMON,
        help_text="Tipo de usuário (define comportamento e permissões)."
    )

    wallet_address = models.CharField(
        max_length=42,
        blank=True,
        null=True,
        help_text="Endereço da carteira blockchain do usuário."
    )

    blocked_tokens = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Tokens bloqueados temporariamente (ex: em análise de saque)."
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
class CommonUser(User):
    full_name = models.CharField(max_length=255,help_text="Nome completo do usuário")
    total_tokens_earned = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    completed_missions = models.IntegerField(default=0)
    cpf = models.CharField(max_length=14, unique=True, help_text="CPF do usuário (somente números)")
    
    def clean(self):
        super().clean()
        cpf_validator = CPF()
        if not cpf_validator.validate(self.cpf):
            raise ValidationError({'cpf': 'CPF inválido'})
    
    def save(self, *args, **kwargs):
        if self.cpf:
            self.cpf = ''.join(filter(str.isdigit, self.cpf))
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.full_name} ({self.cpf})"
