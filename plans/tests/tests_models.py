from django.test import TestCase
from django.contrib.auth import get_user_model
from plans.models import Plan, ContractedPlan
from companies.models import Company
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone

User = get_user_model()

class CompanyPlanCycleTest(TestCase):
    def setUp(self):
        
        self.company = Company.objects.create_user(
            email="company@example.com",
            password="testpass123",
            commercial_name="Empresa Teste Ltda",
            legal_name="Empresa Teste Comércio e Serviços Ltda",
            business_area="Tecnologia",
            cnpj="12345678000190",
            tokens_balance=Decimal('1000.00')
        )
        

        self.basic_plan = Plan.objects.create(
            name="Plano Básico",
            description="Plano inicial",
            token_value=Decimal('100.00'),
            feedbacks_available=50,
            quests_available=20
        )
        
        self.premium_plan = Plan.objects.create(
            name="Plano Premium",
            description="Plano avançado",
            token_value=Decimal('300.00'),
            feedbacks_available=200,
            quests_available=100
        )
        
        self.inactive_plan = Plan.objects.create(
            name="Plano Inativo",
            description="Plano descontinuado",
            token_value=Decimal('200.00'),
            feedbacks_available=100,
            quests_available=50,
            is_active=False
        )

    def test_company_creation(self):
        
        self.assertEqual(self.company.commercial_name, "Empresa Teste Ltda")
        self.assertEqual(self.company.tokens_balance, Decimal('1000.00'))
        self.assertEqual(self.company.user_type, "COMPANY")

    def test_plan_creation(self):

        self.assertEqual(self.basic_plan.feedbacks_available, 50)
        self.assertTrue(self.basic_plan.is_active)
        self.assertFalse(self.inactive_plan.is_active)

    def test_contracted_plan_creation(self):

        contracted = ContractedPlan.objects.create(
            company=self.company,
            plan=self.basic_plan
        )
        
        # Verificar valores padrão
        self.assertEqual(contracted.remaining_feedbacks, 50)
        self.assertEqual(contracted.remaining_quests, 20)
        self.assertTrue(contracted.is_active)
        self.assertAlmostEqual(
            (contracted.expiration_date - timezone.now()).days,
            30,
            delta=1
        )
        
        # Verificar relacionamentos
        self.assertEqual(contracted.company, self.company)
        self.assertEqual(contracted.plan, self.basic_plan)

    def test_contracted_plan_with_custom_expiration(self):

        custom_date = timezone.now() + timezone.timedelta(days=60)
        contracted = ContractedPlan.objects.create(
            company=self.company,
            plan=self.premium_plan,
            expiration_date=custom_date
        )
        self.assertEqual(contracted.expiration_date, custom_date)

    def test_contracted_plan_with_inactive_plan(self):
        with self.assertRaises(ValidationError):
            contracted = ContractedPlan(
                company=self.company,
                plan=self.inactive_plan
            )
            contracted.full_clean()

    def test_decrement_feedbacks_and_quests(self):
        
        
        contracted = ContractedPlan.objects.create(
            company=self.company,
            plan=self.premium_plan
        )
        
        # Decrementar feedbacks
        initial_feedbacks = contracted.remaining_feedbacks
        contracted.decrement_feedback()
        self.assertEqual(contracted.remaining_feedbacks, initial_feedbacks - 1)
        
        # Decrementar quests
        initial_quests = contracted.remaining_quests
        contracted.decrement_quest()
        self.assertEqual(contracted.remaining_quests, initial_quests - 1)

    def test_company_active_plan_property(self):

        active_plan = ContractedPlan.objects.create(
            company=self.company,
            plan=self.basic_plan,
            expiration_date=timezone.now() + timezone.timedelta(days=30)
        )
        
        expired_plan = ContractedPlan.objects.create(
            company=self.company,
            plan=self.premium_plan,
            expiration_date=timezone.now() - timezone.timedelta(days=1),
            is_active=False
        )
        
        self.assertEqual(self.company.active_plan, active_plan)
        self.assertEqual(self.company.remaining_feedbacks, active_plan.remaining_feedbacks)
        self.assertEqual(self.company.remaining_quests, active_plan.remaining_quests)

    def test_company_without_active_plan(self):
        
        new_company = Company.objects.create_user(
            email="newcompany@example.com",
            password="testpass123",
            commercial_name="Nova Empresa",
            legal_name="Nova Empresa Ltda",
            cnpj="98765432000198"
        )
        
        self.assertIsNone(new_company.active_plan)
        self.assertEqual(new_company.remaining_feedbacks, 0)
        self.assertEqual(new_company.remaining_quests, 0)

    def test_print_contracted_plan_details(self):
        contracted = ContractedPlan.objects.create(
            company=self.company,
            plan=self.premium_plan
        )
        
        # Formatando os detalhes de forma mais legível
        details = f"""
        ============================================
        DETALHES DO PLANO CONTRATADO - TESTE
        ============================================
        Empresa: {contracted.company.commercial_name}
        Plano: {contracted.plan.name} (R$ {contracted.plan.token_value})
        Data de contratação: {contracted.purchase_date.strftime('%d/%m/%Y %H:%M')}
        Data de expiração: {contracted.expiration_date.strftime('%d/%m/%Y %H:%M')}
        Dias restantes: {(contracted.expiration_date - timezone.now()).days} dias
        --------------------------------------------
        Recursos disponíveis:
        - Feedbacks restantes: {contracted.remaining_feedbacks}
        - Quests restantes: {contracted.remaining_quests}
        --------------------------------------------
        Status: {'✅ Ativo' if contracted.is_active else '❌ Inativo'}
        ============================================
        """
        
        # Verificações do teste
        self.assertIn(self.company.commercial_name, details)
        self.assertIn(str(self.premium_plan.name), details)
        self.assertIn(str(contracted.remaining_feedbacks), details)
        
        # Imprimindo os detalhes formatados
        print("\n" + "="*80)
        print("SAÍDA DO TESTE: DETALHES DO PLANO CONTRATADO")
        print("="*80)
        print(details)
        print("="*80 + "\n")