import pytest
import logging
from rest_framework.test import APIClient
from users.models import CommonUser
from tokens.models import TokenWallet

logger = logging.getLogger(__name__)

@pytest.mark.django_db
class TestTokenWalletEndpoints:

    def setup_method(self):
        self.client = APIClient()
        self.user = CommonUser.objects.create_user(
            email="user@example.com",
            password="SenhaForte123",
            full_name="Usuário Teste",
            cpf="53560671000"
        )
        self.client.force_authenticate(user=self.user)
        TokenWallet.objects.get_or_create(user=self.user)

    def test_get_balance(self):
        response = self.client.get("/api/v1/fbtk/wallet/balance/")
        logger.info(f"[GET BALANCE] Status: {response.status_code} | Response: {response.data}")
        assert response.status_code == 200
        assert "balance" in response.data

    def test_add_tokens(self):
        response = self.client.post("/api/v1/fbtk/wallet/add/", {"amount": 50}, format="json")
        logger.info(f"[ADD TOKENS] Status: {response.status_code} | Response: {response.data}")
        assert response.status_code == 200
        assert response.data["balance"] == 50

    def test_remove_tokens_success(self):
        self.user.wallet.add_tokens(100)
        response = self.client.post("/api/v1/fbtk/wallet/remove/", {"amount": 30}, format="json")
        logger.info(f"[REMOVE TOKENS - SUCCESS] Status: {response.status_code} | Response: {response.data}")
        assert response.status_code == 200
        assert response.data["balance"] == 70

    def test_remove_tokens_insufficient_balance(self):
        response = self.client.post("/api/v1/fbtk/wallet/remove/", {"amount": 999}, format="json")
        logger.info(f"[REMOVE TOKENS - FAIL] Status: {response.status_code} | Response: {response.data}")
        assert response.status_code == 400
        assert "error" in response.data
