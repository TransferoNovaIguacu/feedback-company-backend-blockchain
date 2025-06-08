# Passo 1: Importações necessárias
from decimal import Decimal
from django.utils import timezone
from companies.models import Company
from plans.models import Plan, ContractedPlan
from missions.models import Mission, MissionQueue
from users.models import CommonUser
from blockchain.models import UserProfile, RewardTransaction
from blockchain.utils.rewards import process_reward_batch
from web3 import Web3

# Passo 2: Cria empresa com CNPJ válido
company, created = Company.objects.get_or_create(
    email="empresa@example.com",
    defaults={
        'password': 'empresapass',
        'commercial_name': 'Empresa Teste',
        'legal_name': 'Empresa LTDA',
        'cnpj': '11222333000181',  # CNPJ válido
        'website': 'https://empresa.com', 
        'logo_url': 'https://empresa.com/logo.png', 
        'tokens_balance': Decimal('0')
    }
)
if not created:
    company.set_password('empresapass')
    company.save()

print("✅ Empresa criada:", company.email)

# Passo 3: Cria plano
plan, created = Plan.objects.get_or_create(
    name="Plano Básico",
    defaults={
        'description': 'Plano com 5 feedbacks e 3 quizzes',
        'token_value': Decimal('10.0'),
        'feedbacks_available': 5,
        'quests_available': 3,
        'reward_percentage': Decimal('0.6')
    }
)
if not created:
    plan.description = 'Plano com 5 feedbacks e 3 quizzes'
    plan.save()
print("✅ Plano criado:", plan.name)

# Passo 4: Contrata plano → gera missões automaticamente
contracted_plan, _ = ContractedPlan.objects.get_or_create(
    company=company,
    plan=plan,
    defaults={
        'purchase_date': timezone.now(),
        'expiration_date': timezone.now() + timezone.timedelta(days=30),
        'remaining_feedbacks': plan.feedbacks_available,
        'remaining_quests': plan.quests_available
    }
)
print("✅ Plano contratado:", contracted_plan.plan.name)

# Passo 5: Confere se missões foram criadas
missions = Mission.objects.filter(contracted_plan=contracted_plan)
print("✅ Missões criadas:", missions.count())

# Passo 6: Adiciona perguntas às missões (opcional)
for mission in missions:
    mission.description = f"Pergunta {mission.id} - Avaliação de produto"
    mission.save()
    print(f"✅ Pergunta adicionada à missão {mission.id}")

# Passo 7: Cria usuário comum com wallet_address
common_user, created = CommonUser.objects.get_or_create(
    email="user@example.com",
    defaults={
        'password': 'userpass',
        'full_name': 'Usuário Comum',
        'cpf': '12345678901'
    }
)
if not created:
    common_user.set_password('userpass')
    common_user.save()
print("✅ Usuário comum criado:", common_user.email)

# Passo 8: Cria perfil blockchain para usuário comum
profile, _ = UserProfile.objects.get_or_create(user=common_user)
profile.wallet_address = "0xf5b054B8518e9D7f4085feaeD4cBbC642b080ada"
profile.save()
print("✅ Wallet address definido:", profile.wallet_address)

# Passo 9: Usuário seleciona uma missão
mission = missions.first()
MissionQueue.objects.create(
    user=common_user,
    mission=mission
)
print("✅ Usuário adicionado à fila de missão")

# Passo 10: Conclui missão e gera recompensa
RewardTransaction.objects.create(
    user=common_user,
    amount=Decimal('1.0'),
    tx_type='REWARD',
    status='PENDING'
)
print("✅ Recompensa pendente criada")

# Passo 11: Processa recompensa imediatamente (sem Celery)
tx_hash = process_reward_batch()
print("✅ Transação enviada:", tx_hash)

# Passo 12: Valida se o saldo foi atualizado
profile.refresh_from_db()
print("✅ Saldo atualizado:", profile.blockchain_balance)