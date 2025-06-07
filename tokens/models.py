from decimal import Decimal
from venv import logger
from django.db import models
from django.conf import settings
from web3 import Web3

from web3integration.services import Web3IntegrationService

class TokenWallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    balance = models.DecimalField(max_digits=20, decimal_places=18, default=Decimal('0.0'))
    last_sync = models.DateTimeField(auto_now=True)

    def sync_with_blockchain(self):
        """Sincroniza o saldo local com a blockchain"""
        service = Web3IntegrationService()
        balance = service.check_balance(self.user.wallet_address)
        if balance is not None:
            self.balance = balance
            self.save()
            logger.info(f"🔄 Saldo sincronizado: {self.user.email} → {self.balance}")
        else:
            logger.warning(f"⚠️ Falha ao sincronizar {self.user.email}")

    def mint_tokens(self, amount):
        """Minta tokens via blockchain e atualiza saldo local"""
        service = Web3IntegrationService()
        tx_hash = service.batch_mint([self.user.wallet_address], [float(amount)])
        if tx_hash:
            self.balance += Decimal(str(amount))
            self.save()
            logger.info(f"✅ Tokens mintados: {amount} FBTK para {self.user.email}")
            return tx_hash
        else:
            logger.error("❌ Falha ao mintar tokens na blockchain")
            return None