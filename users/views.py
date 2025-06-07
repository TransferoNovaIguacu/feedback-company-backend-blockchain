from .serializers import CommonUserRegisterSerializer, CommonUserProfileSerializer
from companies.serializers import CompanyProfileSerializer
from django.db import IntegrityError
from dj_rest_auth.views import LoginView
from rest_framework.views import APIView
from rest_framework.response import Response
from dj_rest_auth.registration.views import RegisterView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, permissions


class CustomLoginView(LoginView):
    
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

        return Response(data)

class CommonUserRegisterView(RegisterView):
    
    serializer_class = CommonUserRegisterSerializer
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError as e:
            if 'users_user.email' in str(e):
                return Response(
                    {'email': 'Esse e-mail já está cadastrado.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {'detail': 'Erro de integridade no banco de dados.'},
                status=status.HTTP_400_BAD_REQUEST
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
    
# class LogoutView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request):
#         refresh_token = request.data.get("refresh")
#         if not refresh_token:
#             return Response({"detail": "Refresh token não fornecido."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             token = RefreshToken(refresh_token)
#             if hasattr(token, "blacklist"):
#                 token.blacklist()
#         except TokenError:
#             return Response({"detail": "Token inválido ou já expirado."}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({"detail": f"Erro ao processar logout: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return Response({"detail": "Logout realizado com sucesso."}, status=status.HTTP_205_RESET_CONTENT)

    
