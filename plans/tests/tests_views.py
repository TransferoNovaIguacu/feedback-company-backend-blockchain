# plans/tests/test_views.py
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from plans.models import Plan
from users.models import User, CommonUser
from companies.models import Company

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def admin_user():
    
    return User.objects.create_user(
        email='admin@test.com',
        password='adminpass123',
        is_staff=True,
        user_type='ADMIN'
    )

@pytest.fixture
def company_user():
    
    company = Company.objects.create(
        email="teste@teste.com",
        password="testesenha@123",
        commercial_name="Minha Empresa Ltda",
        legal_name="Minha Empresa Ltda",
        cnpj="99770423000158",
        website="https://www.minhaempresa.com.br",
        logo_url="https://www.minhaempresa.com.br/logo.png",
        verified=True,
        tokens_balance=100.0,
        corporate_tax_id="123456789012",
    )
    return company

@pytest.fixture
def common_user():
    
    common = CommonUser.objects.create(
        email='common@test.com',
        password='commonpass123',
        full_name="Usuário Comum",
        cpf='44463049091',
        total_tokens_earned=0,
        completed_missions=0
    )
    return common

@pytest.fixture
def create_plans():
    
    Plan.objects.create(
        name="Plano Básico",
        description="Plano inicial para pequenas empresas",
        token_value="100.00",
        feedbacks_available=50,
        quests_available=10,
        reward_percentage="0.60",
        is_active=True
    )
    Plan.objects.create(
        name="Plano Premium",
        description="Plano completo para grandes empresas",
        token_value="300.00",
        feedbacks_available=200,
        quests_available=50,
        reward_percentage="0.70",
        is_active=True
    )

@pytest.mark.django_db
def test_plan_list_admin(client, admin_user, create_plans):

    client.force_authenticate(user=admin_user)
    url = reverse('plan-list')
    response = client.get(url)
    
    assert response.status_code == 200
    assert len(response.data) == 2
    assert any(plan['name'] == "Plano Básico" for plan in response.data)
    assert any(plan['name'] == "Plano Premium" for plan in response.data)

@pytest.mark.django_db
def test_plan_list_format(client, admin_user, create_plans):
    
    client.force_authenticate(user=admin_user)
    url = reverse('plan-list')
    response = client.get(url)

    expected_keys = {
        'id',
        'name',
        'description',
        'token_value',
        'feedbacks_available',
        'quests_available',
        'reward_percentage',
        'is_active',
        'created_at',
    }

    for plan in response.data:
        assert expected_keys.issubset(plan.keys())


@pytest.mark.django_db
def test_plan_list_common_user(client, common_user, create_plans):
    
    client.force_authenticate(user=common_user)
    url = reverse('plan-list')
    response = client.get(url)
    
    assert response.status_code == 200
    assert len(response.data) == 2
    
@pytest.mark.django_db
def test_plan_list_company_user(client, company_user, create_plans):
    
    client.force_authenticate(user=company_user)
    url = reverse('plan-list')
    response = client.get(url)

    assert response.status_code == 200
    assert len(response.data) == 2
    assert any(plan['name'] == "Plano Básico" for plan in response.data)

@pytest.mark.django_db
def test_plan_list_anonymous_user(client, create_plans):
    
    url = reverse('plan-list')
    response = client.get(url)

    assert response.status_code == 401
