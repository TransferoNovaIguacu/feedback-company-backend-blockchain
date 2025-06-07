from decimal import Decimal
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from tokens.models import TokenWallet
from web3integration.services import Web3IntegrationService
from rest_framework.views import APIView

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def token_balance(request):
    wallet, created = TokenWallet.objects.get_or_create(user=request.user)
    return Response({'balance': wallet.balance})

class MintTokensView(APIView):
    permission_classes = [IsAuthenticated]
    
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

class SyncBalanceView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        wallet = request.user.wallet
        balance = wallet.check_balance()
        return Response({"balance": balance})