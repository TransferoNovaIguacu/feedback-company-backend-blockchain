from datetime import timezone
from django.conf import settings
from blockchain.models import RewardTransaction, UserProfile
from blockchain.services import BlockchainService
from web3 import Web3
from decimal import Decimal
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

def process_reward_batch():
    try:
        service = BlockchainService()
        if not service.contract:
            logger.error("❌ Contrato não carregado")
            return None

        pending_rewards = RewardTransaction.objects.filter(status='PENDING', tx_type='REWARD', user__userprofile__wallet_address__isnull=False).select_related('user__userprofile')
        
        if not pending_rewards.exists():
            logger.info("Nenhuma recompensa pendente")
            return None

        rewards_by_wallet = {}
        tx_ids = []

        for reward in pending_rewards:
            raw_wallet = reward.user.userprofile.wallet_address.strip()
            if not Web3.is_address(raw_wallet):
                logger.warning(f"[WARNING] Endereço inválido: {raw_wallet}")
                continue
            checksum_addr = Web3.to_checksum_address(raw_wallet)
            rewards_by_wallet[checksum_addr] = rewards_by_wallet.get(checksum_addr, Decimal(0)) + reward.amount
            tx_ids.append(reward.id)

        valid_wallets = []
        valid_amounts = []

        for wallet, total in rewards_by_wallet.items():
            if Web3.is_address(wallet):
                valid_wallets.append(wallet)
                valid_amounts.append(float(total))

        if not valid_wallets:
            logger.info("Nenhum endereço válido após validação final. Abortando.")
            return None

        tx_hash = service.batch_mint(valid_wallets, valid_amounts)
        if not tx_hash:
            logger.error("❌ batch_mint retornou None. Verifique os logs de batch_mint.")
            return None

        RewardTransaction.objects.filter(id__in=tx_ids).update(
            status='PROCESSING',
            tx_hash=tx_hash,
            processed_at=timezone.now())

        for checksum_addr, amt in zip(valid_wallets, valid_amounts):
            profile = UserProfile.objects.filter(wallet_address=checksum_addr).first()
            if profile:
                profile.virtual_balance -= Decimal(str(amt))
                profile.blockchain_balance += Decimal(str(amt))
                profile.save(update_fields=['virtual_balance', 'blockchain_balance'])
                logger.info(f"✅ Saldo atualizado para {checksum_addr}: {profile.blockchain_balance} FBTK")
            else:
                logger.warning(f"❌ Perfil não encontrado para {checksum_addr}")

        return tx_hash
    except Exception as e:
        logger.error(f"❌ Erro ao processar recompensas: {e}")
        return None