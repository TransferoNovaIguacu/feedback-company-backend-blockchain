from .serializers import CommonUserRegisterSerializer, CommonUserProfileSerializer, LogoutSerializer, WalletAddressSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from companies.serializers import CompanyProfileSerializer
from django.db import DatabaseError
from django.core.exceptions import ObjectDoesNotExist
from dj_rest_auth.views import LoginView
from dj_rest_auth.registration.views import RegisterView
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError as DRFValidationError
from drf_spectacular.utils import extend_schema
import logging

logger = logging.getLogger(__name__)


class CustomLoginView(LoginView):
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        User = get_user_model()
        
        if not User.objects.filter(email=email).exists():
            return Response({'detail': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            return super().post(request, *args, **kwargs)
        except ValidationError as e:
            return Response({'detail': "Email ou senha inválidos"}, status=status.HTTP_400_BAD_REQUEST)
        except AuthenticationFailed as e:
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except ObjectDoesNotExist:
            return Response({'detail': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except DatabaseError:
            return Response({'detail': 'Erro no banco de dados.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'detail': f'Erro inesperado: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    def get_response(self):
        original_response = super().get_response()
        user = self.user
        data = original_response.data
        data['user_type'] = user.user_type
        data['email'] = user.email
        data['date_joined'] = user.date_joined
        data['is_active'] = user.is_active

        if hasattr(user, 'commonuser'):
            com = user.commonuser
            data['full_name'] = com.full_name
            data['total_tokens_earned'] = com.total_tokens_earned
            data['completed_missions'] = com.completed_missions
        elif hasattr(user, 'company'):
            comp = user.company
            data['commercial_name'] = comp.commercial_name
            data['verified'] = comp.verified
            data['tokens_balance'] = comp.tokens_balance

        return Response(data, status=status.HTTP_200_OK)

class CommonUserRegisterView(RegisterView):
    
    serializer_class = CommonUserRegisterSerializer
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save(request)

            return Response(
                {
                    "detail": "Usuário cadastrado com sucesso.",
                    "user_id": user.id,
                    "email": user.email
                },
                status=status.HTTP_201_CREATED
            )
        
        except DRFValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Erro inesperado: {e}", exc_info=True)
            return Response(
                {'detail': 'Erro interno do servidor.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
class UserProfileView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self, user):
        if hasattr(user, 'commonuser'):
            return CommonUserProfileSerializer
        elif hasattr(user, 'company'):
            return CompanyProfileSerializer
        return None

    def get(self, request):
        user = request.user

        if hasattr(user, 'commonuser'):
            instance = user.commonuser
            serializer_class = CommonUserProfileSerializer
        elif hasattr(user, 'company'):
            instance = user.company
            serializer_class = CompanyProfileSerializer
        else:
            return Response({'detail': 'Tipo de usuário inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = serializer_class(instance)
        return Response({
            'user_type': user.user_type,
            'email': user.email,
            **serializer.data
        })

    def patch(self, request):
        user = request.user

        if hasattr(user, 'commonuser'):
            instance = user.commonuser
            serializer_class = CommonUserProfileSerializer
        elif hasattr(user, 'company'):
            instance = user.company
            serializer_class = CompanyProfileSerializer
        else:
            return Response({'detail': 'Tipo de usuário inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = serializer_class(instance, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'user_type': user.user_type,
                'email': user.email,
                **serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
        request=LogoutSerializer,
        responses={205: None, 400: None, 500: None},
        description="Faz logout invalidando o refresh token."
    )
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token não fornecido."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response({"detail": "Token inválido ou já expirado."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"Erro ao processar logout: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"detail": "Logout realizado com sucesso."}, status=status.HTTP_200_OK)
    
class WalletAddressView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=WalletAddressSerializer,
        responses={200: WalletAddressSerializer},
        description="Adiciona/atualiza o endereço da carteira blockchain do usuário"
    )
    def put(self, request):
        user = request.user
        serializer = WalletAddressSerializer(user, data=request.data)
        
        if serializer.is_valid():
            had_previous_address = bool(user.wallet_address)
            
            serializer.save()
            
            action = "atualizada" if had_previous_address else "cadastrada"
            logger.info(
                f"Wallet address {action} | User: {user.id} | "
                f"New address: {user.wallet_address}"
            )
            
            return Response({
                "success": True,
                "message": f"Carteira {action} com sucesso",
                "wallet_address": user.wallet_address
            }, status=status.HTTP_200_OK)
        
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    
