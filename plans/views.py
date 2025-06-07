from django.shortcuts import render

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Plan, ContractedPlan
from .serializers import PlanSerializer, ContractedPlanSerializer
from companies.models import Company
from django.utils import timezone
from datetime import timedelta

class PlanViewSet(viewsets.ModelViewSet):
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAuthenticated]  # Ou AllowAny para teste
    
    def get_queryset(self):
        # Exemplo: filtrar apenas planos ativos
        return Plan.objects.filter(is_active=True)

class ContractedPlanViewSet(viewsets.ModelViewSet):
    serializer_class = ContractedPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Empresas veem apenas seus próprios planos contratados
        if self.request.user.is_staff:
            return ContractedPlan.objects.all()
        return ContractedPlan.objects.filter(company__user=self.request.user)

    @action(detail=True, methods=['post'])
    def purchase(self, request, pk=None):
        # Lógica para contratar um plano
        plan = Plan.objects.get(pk=pk)
        company = Company.objects.get(user=request.user)
        
        # Define a data de expiração (ex: 30 dias a partir de agora)
        expiration_date = timezone.now() + timedelta(days=30)
        
        contracted_plan = ContractedPlan.objects.create(
            company=company,
            plan=plan,
            remaining_feedbacks=plan.feedbacks_available,
            remaining_quests=plan.quests_available,
            expiration_date=expiration_date
        )
        
        serializer = self.get_serializer(contracted_plan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)