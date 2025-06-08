import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from users.models import CommonUser 


@pytest.mark.django_db
class TestCommonUserRegister:

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('common_register')
        
    def test_register_success(self, capsys):
        payload = {
            "email": "test@example.com",
            "password1": "MinhaSenhaForte123",
            "password2": "MinhaSenhaForte123",
            "full_name": "Fulano da Silva",
            "cpf": "67909795068"
        }

        response = self.client.post(self.url, payload, format='json')
        print("✅ RESPOSTA DE SUCESSO:", response.status_code, response.json(), flush=True)

        assert response.status_code == status.HTTP_201_CREATED
        assert CommonUser.objects.filter(email="test@example.com").exists()

    def test_register_with_invalid_cpf(self, capsys):
        payload = {
            "email": "invalidcpf@example.com",
            "password1": "MinhaSenhaForte123",
            "password2": "MinhaSenhaForte123",
            "full_name": "Usuário Inválido",
            "cpf": "11111111111"
        }

        response = self.client.post(self.url, payload, format='json')
        print("❌ RESPOSTA CPF INVÁLIDO:", response.status_code, response.content.decode(), flush=True)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "cpf" in response.json()

    def test_register_with_existing_email(self, capsys):
        CommonUser.objects.create_user(
            email="duplicado@example.com",
            password="senhaqualquer",
            full_name="Usuário Antigo",
            cpf="67909795068",
            user_type="COMMON"
        )

        payload = {
            "email": "duplicado@example.com",
            "password1": "MinhaSenhaForte123",
            "password2": "MinhaSenhaForte123",
            "full_name": "Usuário Novo",
            "cpf": "67909795068"
        }

        response = self.client.post(self.url, payload, format='json')
        print("❌ RESPOSTA EMAIL DUPLICADO:", response.status_code, response.content.decode(), flush=True)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.json()

    def test_register_with_invalid_email_format(self, capsys):
        payload = {
            "email": "emailinvalido",
            "password1": "MinhaSenhaForte123",
            "password2": "MinhaSenhaForte123",
            "full_name": "Usuário",
            "cpf": "67909795068"
        }

        response = self.client.post(self.url, payload, format='json')
        print("❌ RESPOSTA EMAIL INVÁLIDO:", response.status_code, response.content.decode(), flush=True)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.json()
