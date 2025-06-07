import pytest
from django.core.exceptions import ValidationError
from companies.models import Company
from users.models import User

@pytest.mark.django_db
def test_create_company_valid():
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

    assert company.id is not None
    assert company.commercial_name == "Minha Empresa Ltda"

@pytest.mark.django_db
def test_create_company_invalid_cnpj():
    
    with pytest.raises(ValidationError):
        company = Company(
            email="teste@teste.com",
            password="testesenha@123",
            commercial_name="Empresa Invalida",
            legal_name="Empresa Invalida",
            cnpj="12345678",
            website="https://www.empresainvalida.com.br",
            logo_url="https://www.empresainvalida.com.br/logo.png",
            verified=False,
            tokens_balance=0.0,
            corporate_tax_id="9876543210",
        )
        company.full_clean()

@pytest.mark.django_db
def test_create_company_without_mandatory_fields():
    with pytest.raises(ValidationError):
        company = Company(
            email="teste@teste.com",
            password="testesenha@123",
            commercial_name="Empresa Sem Razão Social",
            legal_name="", 
            cnpj="99770423000158",
            website="",
            logo_url="",
            verified=False,
            tokens_balance=50.0,
            corporate_tax_id="1234567890",
        )
        company.full_clean()
        company.save()

    assert company.legal_name == ""

@pytest.mark.django_db
def test_create_company_default_values():

    company = Company.objects.create(
        email="teste@teste.com",
        password="testesenha@123",
        commercial_name="Empresa Default",
        legal_name="Empresa Default",
        cnpj="99770423000158",
    )

    assert company.tokens_balance == 0
    assert company.verified is False
    assert company.corporate_tax_id == ""

@pytest.mark.django_db
def test_create_company_invalid_cnpj_format():

    with pytest.raises(ValidationError):
        company = Company(
            email="teste@teste.com",
            password="testesenha@123",
            commercial_name="CNPJ Inválido",
            legal_name="CNPJ Inválido",
            cnpj="12345678000199",
            website="https://www.cnpjinválido.com",
            logo_url="https://www.cnpjinválido.com/logo.png",
            verified=False,
            tokens_balance=0.0,
            corporate_tax_id="000000000000",
        )
        company.full_clean()

@pytest.mark.django_db
def test_company_str_method():

    company = Company.objects.create(
        email="teste@teste.com",
        password="testesenha@123",
        commercial_name="Empresa de Teste",
        legal_name="Empresa de Teste Ltda",
        cnpj="12345678000195",
        website="https://www.empresa.com",
        logo_url="https://www.empresa.com/logo.png",
        verified=False,
        tokens_balance=100.0,
        corporate_tax_id="9876543210",
    )

    assert str(company) == "Empresa de Teste (Company)"

@pytest.mark.django_db
def test_create_company_with_optional_fields():

    company = Company.objects.create(
        email="teste@teste.com",
        password="testesenha@123",
        commercial_name="Empresa com Campos Opcionais",
        legal_name="Empresa com Campos Opcionais Ltda",
        cnpj="99770423000158",
        website="https://www.empresaopcional.com",
        logo_url="https://www.empresaopcional.com/logo.png",
        verified=True,
        tokens_balance=250.0,
        corporate_tax_id="38214124780213",
    )

    assert company.website == "https://www.empresaopcional.com"
    assert company.logo_url == "https://www.empresaopcional.com/logo.png"
    assert company.business_area == ""
