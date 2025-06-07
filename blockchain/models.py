from django.db import models
from django.conf import settings
from decimal import Decimal

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='userprofile'
    )
    wallet_address = models.CharField(
        max_length=42,
        blank=True,
        null=True,
        help_text="Endereço da carteira blockchain do usuário.",
        unique=False
    )
    blockchain_balance = models.DecimalField(
        max_digits=20,
        decimal_places=18,
        default=Decimal('0.0'),
        help_text="Saldo na blockchain"
    )
    virtual_balance = models.DecimalField(
        max_digits=20,
        decimal_places=18,
        default=Decimal('0.0'),
        help_text="Saldo local antes de mintar tokens"
    )

    def __str__(self):
        return f"{self.user.email} - {self.blockchain_balance} FBTK"

class RewardTransaction(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('PROCESSING', 'Processando'),
        ('SUCCESS', 'Sucesso'),
        ('FAILED', 'Falha')
    ]
    TX_TYPE_CHOICES = [
        ('REWARD', 'Recompensa'),
        ('WITHDRAW', 'Saque')
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    amount = models.DecimalField(
        max_digits=20,
        decimal_places=18,
        default=Decimal('0.0')
    )
    tx_hash = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    tx_type = models.CharField(
        max_length=10,
        choices=TX_TYPE_CHOICES,
        default='REWARD'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.amount} FBTK"