from web3 import Web3
from web3.exceptions import TransactionNotFound
from django.conf import settings
import logging
import json
from pathlib import Path
from decimal import Decimal

logger = logging.getLogger(__name__)

class BlockchainService:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.WEB3_HTTP_PROVIDER_URL))
        logger.info("[BlockchainService] Usando HTTPProvider")

        if not self.w3.is_connected():
            logger.error("❌ Falha ao conectar com o provider Ethereum")
            raise ConnectionError("Não foi possível conectar ao provider Ethereum")

        self.account = self.w3.eth.account.from_key(settings.PRIVATE_KEY)
        self.admin_address = self.account.address

        if hasattr(settings, 'CONTRACT_ADDRESS') and Web3.is_address(settings.CONTRACT_ADDRESS):
            if not self._load_contract():
                logger.warning("⚠️ Contrato não carregado")
        else:
            logger.warning("⚠️ CONTRACT_ADDRESS não definido ou inválido")

    def _load_contract(self):
        try:
            current_dir = Path(__file__).resolve().parent
            contract_json_path = current_dir / 'artifacts' / 'contracts' / 'FeedbackToken.sol' / 'FeedbackToken.json'
            
            with open(contract_json_path, 'r') as f:
                contract_data = json.load(f)
                abi = contract_data['abi']

            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(settings.CONTRACT_ADDRESS),
                abi=abi
            )
            return True
        except FileNotFoundError:
            logger.error("❌ Arquivo FeedbackToken.json não encontrado")
            self.contract = None
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao carregar contrato: {e}")
            self.contract = None
            return False

    def batch_mint(self, recipients, amounts):
        try:
            checksum_recipients = [Web3.to_checksum_address(addr) for addr in recipients]
            wei_amounts = [int(amt * 10**18) for amt in amounts]

            nonce = self.w3.eth.get_transaction_count(self.admin_address)
            latest_block = self.w3.eth.get_block('latest')
            base_fee = latest_block.get('baseFeePerGas')

            if base_fee is not None:
                max_priority_fee = int(2e9)
                max_fee_per_gas = base_fee + max_priority_fee
                transaction_params = {
                    'type': 2,
                    'maxPriorityFeePerGas': max_priority_fee,
                    'maxFeePerGas': max_fee_per_gas,
                    'gas': 5000000,
                    'chainId': settings.CHAIN_ID,
                    'nonce': nonce
                }
            else:
                gas_price = int(2e9)
                transaction_params = {
                    'gas': 5000000,
                    'gasPrice': gas_price,
                    'chainId': settings.CHAIN_ID,
                    'nonce': nonce
                }

            tx = self.contract.functions.batchMint(checksum_recipients, wei_amounts).build_transaction(transaction_params)
            signed_tx = self.w3.eth.account.sign_transaction(tx, settings.PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            logger.info(f"🔗 Transação batchMint enviada: {tx_hash.hex()}")
            return tx_hash.hex()
        except Exception as e:
            logger.error(f"❌ Erro ao mintar tokens: {e}")
            return None

    def check_balance(self, address):
        try:
            checksum_addr = Web3.to_checksum_address(address)
            balance = self.contract.functions.balanceOf(checksum_addr).call()
            return Decimal(str(balance / 10**18))
        except Exception as e:
            logger.error(f"❌ Erro ao verificar saldo: {e}")
            return Decimal('0')