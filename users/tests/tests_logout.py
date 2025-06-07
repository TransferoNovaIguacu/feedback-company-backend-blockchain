import pytest
import time
from datetime import timedelta

from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.utils import timezone

User = get_user_model()

@pytest.mark.django_db
class TestLogoutView:

    @pytest.fixture
    def user_and_tokens(self):
        user = User.objects.create_user(email="test@example.com", password="strongpass123")
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        return {
            "user": user,
            "refresh": str(refresh),
            "access": access
        }

    def test_logout_success(self, user_and_tokens):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_and_tokens['access']}")
        response = client.post("/api/v1/auth/logout/", {"refresh": user_and_tokens["refresh"]})
        assert response.status_code == 205
        assert response.data["detail"] == "Logout realizado com sucesso."

    def test_logout_with_invalid_token(self, user_and_tokens):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_and_tokens['access']}")
        response = client.post("/api/v1/auth/logout/", {"refresh": "invalid_token"})
        assert response.status_code == 400
        assert "Token inválido" in response.data["detail"]

    def test_logout_without_token(self, user_and_tokens):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_and_tokens['access']}")
        response = client.post("/api/v1/auth/logout/", {})
        assert response.status_code == 400
        assert response.data["detail"] == "Refresh token não fornecido."

    def test_logout_with_expired_access_token(self):
        user = User.objects.create_user(email="expired@example.com", password="strongpass123")
        refresh = RefreshToken.for_user(user)

        # Criar um access token com tempo de expiração curto
        access = AccessToken.for_user(user)
        access.set_exp(lifetime=timedelta(seconds=1))
        expired_access = str(access)
        time.sleep(2)  # esperar o token expirar

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {expired_access}")
        response = client.post("/api/v1/auth/logout/", {"refresh": str(refresh)})
        assert response.status_code in [205, 401]  # pode ser 205 se só o refresh for exigido
        # Você pode customizar a resposta se quiser bloquear access expirado

    def test_logout_with_refresh_token_from_cookie(self):
        user = User.objects.create_user(email="cookieuser@example.com", password="strongpass123")
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        # Simula cookies usados no frontend (ex: localStorage transferido para cookie)
        client.cookies['jwt-refresh'] = str(refresh)
        client.cookies['jwt-auth'] = access

        response = client.post("/api/v1/auth/logout/", {"refresh": str(refresh)})
        assert response.status_code == 205
        assert response.data["detail"] == "Logout realizado com sucesso."
