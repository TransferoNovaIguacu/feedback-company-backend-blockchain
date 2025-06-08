import logging
from decimal import Decimal
import os
from pathlib import Path
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from web3 import Web3
from tokens.models import TokenWallet
from web3integration.services import Web3IntegrationService
from rest_framework.views import APIView
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.core.exceptions import ObjectDoesNotExist
from tokens.models import TokenWallet
from tokens.serializers import AmountSerializer
from rest_framework.generics import GenericAPIView
import subprocess
from dotenv import load_dotenv
 
logger = logging.getLogger(__name__)

class MintTokensView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AmountSerializer
    
    def post(self, request):
        amount = Decimal(request.data.get('amount', '0.5'))
        wallet = request.user.wallet

        if not wallet:
            return Response({"error": "Endereço da carteira não definido"}, status=400)

        service = Web3IntegrationService()
        tx_hash = service.batch_mint([wallet], [float(amount)])
        
        if tx_hash:
            wallet.balance += amount
            wallet.save()
            return Response({
                "tx_hash": tx_hash,
                "balance": wallet.balance
            }, status=200)
        else:
            return Response({"error": "Falha ao mintar tokens"}, status=500)

class SyncBalanceView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AmountSerializer
    
    def get(self, request):
        wallet = request.user.wallet
        balance = wallet.check_balance()
        return Response({"balance": balance})

# Carteira Virtual
class TokenBalanceView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AmountSerializer

    def get(self, request):
        wallet, created = TokenWallet.objects.get_or_create(user=request.user)
        return Response({'balance': wallet.balance}, status=status.HTTP_200_OK)


@extend_schema(
    request=AmountSerializer,
    responses={200: AmountSerializer},
    description="Adiciona tokens à carteira do usuário."
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_tokens(request):
    serializer = AmountSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    amount = serializer.validated_data['amount']
    wallet, _ = TokenWallet.objects.get_or_create(user=request.user)
    wallet.add_tokens(amount)
    return Response({
        'message': f'{amount} tokens adicionados com sucesso.',
        'balance': wallet.balance
    }, status=status.HTTP_200_OK)


@extend_schema(
    request=AmountSerializer,
    responses={200: AmountSerializer},
    description="Remove tokens da carteira do usuário."
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_tokens(request):
    serializer = AmountSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    amount = serializer.validated_data['amount']
    wallet, _ = TokenWallet.objects.get_or_create(user=request.user)

    if wallet.remove_tokens(amount):
        return Response({
            'message': f'{amount} tokens removidos com sucesso.',
            'balance': wallet.balance
        }, status=status.HTTP_200_OK)

    return Response({'error': 'Saldo insuficiente para remover tokens.'}, status=status.HTTP_400_BAD_REQUEST)

class WithdrawTokensView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Validação dos dados de entrada
        serializer = AmountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        
        BASE_DIR = Path(__file__).resolve().parent.parent
        dotenv_path = BASE_DIR / 'web3integration' / '.env'
        load_dotenv(dotenv_path)
        MIN_WITHDRAWAL = Decimal(os.getenv('MIN_WITHDRAWAL'))
        
        amount = Decimal(str(serializer.validated_data['amount']))
        user = request.user
        
        # Verificações iniciais
        if not hasattr(user, 'wallet_address') or not user.wallet_address:
            return Response(
                {"error": "Endereço de carteira blockchain não configurado"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            wallet = TokenWallet.objects.get(user=user)
            
            if wallet.balance < amount:
                return Response(
                    {"error": "Saldo insuficiente na carteira virtual"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            if amount < MIN_WITHDRAWAL:
                return Response(
                    {"error": f"Saque minimo necessário: {MIN_WITHDRAWAL} FBTK"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            service = Web3IntegrationService()
            tx_hash = service.transfer(user.wallet_address, float(amount))
            
            if tx_hash:
                wallet.balance -= amount
                wallet.save()
                
                logger.info(
                    f"Withdrawal successful for user {user.id}. "
                    f"Amount: {amount}, TX Hash: {tx_hash}"
                )
                
                return Response({
                    "success": True,
                    "tx_hash": tx_hash,
                    "new_balance": str(wallet.balance),
                    "message": "Saque realizado com sucesso"
                }, status=status.HTTP_200_OK)
            else:
                raise Exception("Falha na transferência na blockchain")
                
        except Exception as e:
            logger.error(
                f"Withdrawal failed for user {user.id}. "
                f"Error: {str(e)}",
                exc_info=True
            )
            return Response(
                {"error": "Falha ao processar saque na blockchain"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
