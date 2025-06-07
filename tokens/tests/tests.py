# tokens/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from tokens.models import TokenWallet

User = get_user_model()

class TokenWalletModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',  # Usando apenas email
            password='testpass123'
        )

    def test_wallet_creation_via_signal(self):
        """Testa se o signal cria uma carteira automaticamente para novo usuário"""
        self.assertTrue(TokenWallet.objects.filter(user=self.user).exists())
        wallet = TokenWallet.objects.get(user=self.user)
        self.assertEqual(wallet.balance, 0)

    def test_add_tokens_method(self):
        """Testa o método add_tokens do modelo"""
        wallet = TokenWallet.objects.get(user=self.user)
        wallet.add_tokens(100)
        self.assertEqual(wallet.balance, 100)

    def test_remove_tokens_method(self):
        """Testa o método remove_tokens do modelo"""
        wallet = TokenWallet.objects.get(user=self.user)
        wallet.add_tokens(100)
        
        # Testa remoção bem-sucedida
        result = wallet.remove_tokens(50)
        self.assertTrue(result)
        self.assertEqual(wallet.balance, 50)
        
        # Testa remoção com saldo insuficiente
        result = wallet.remove_tokens(100)
        self.assertFalse(result)
        self.assertEqual(wallet.balance, 50)


class TokenWalletViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='viewuser@example.com',
            password='viewpass123'
        )
        self.token_balance_url = reverse('token-balance')

    def test_token_balance_unauthenticated(self):
        """Testa acesso não autenticado à view"""
        response = self.client.get(self.token_balance_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_balance_authenticated(self):
        """Testa acesso autenticado à view"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(self.token_balance_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], 0)
        
        # Testa com saldo existente
        wallet = TokenWallet.objects.get(user=self.user)
        wallet.add_tokens(150)
        
        response = self.client.get(self.token_balance_url)
        self.assertEqual(response.data['balance'], 150)


class TokenWalletSignalTests(TestCase):
    def test_signal_on_user_creation(self):
        """Testa se o signal é acionado corretamente na criação de usuário"""
        initial_count = TokenWallet.objects.count()
        
        new_user = User.objects.create_user(
            email='signaluser@example.com',
            password='signalpass123'
        )
        
        self.assertEqual(TokenWallet.objects.count(), initial_count + 1)
        self.assertTrue(TokenWallet.objects.filter(user=new_user).exists())
        
        wallet = TokenWallet.objects.get(user=new_user)
        self.assertEqual(wallet.balance, 0)