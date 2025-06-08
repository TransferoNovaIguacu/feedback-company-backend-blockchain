from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Plan, ContractedPlan
from .serializers import PlanSerializer, ContractedPlanSerializer
from companies.models import Company
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist

class PlanViewSet(viewsets.ModelViewSet):
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Plan.objects.filter(is_active=True)

    @action(detail=True, methods=['post'], url_path='purchase', url_name='plan-purchase')
    def purchase(self, request, pk=None):
        try:
            company = Company.objects.filter(pk=request.user.pk).first()

            if not company:
                return Response(
                    {
                        "error": "Apenas empresas podem comprar planos",
                        "solution": "Registre-se como empresa no endpoint /api/v1/auth/register/company/"
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            plan = self.get_object()

            if not plan.is_active:
                return Response(
                    {"error": "Este plano não está disponível para compra"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if company.contracted_plans.filter(
                is_active=True,
                expiration_date__gt=timezone.now()
            ).exists():
                return Response(
                    {"error": "Sua empresa já possui um plano ativo"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            contracted_plan = ContractedPlan.objects.create(
                company=company,
                plan=plan,
                remaining_feedbacks=plan.feedbacks_available,
                remaining_quests=plan.quests_available,
                expiration_date=timezone.now() + timedelta(days=30)
            )

            return Response(
                ContractedPlanSerializer(contracted_plan).data,
                status=status.HTTP_201_CREATED
            )

        except ObjectDoesNotExist:
            return Response(
                {"error": "Plano não encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    "error": "Erro na compra do plano",
                    "details": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class ContractedPlanViewSet(viewsets.ModelViewSet):
    serializer_class = ContractedPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return ContractedPlan.objects.all().select_related('company', 'plan')

        return ContractedPlan.objects.filter(
            company__pk=self.request.user.pk
        ).select_related('plan')


class PlanListView(generics.ListAPIView):
    queryset = Plan.objects.filter(is_active=True)
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response([
            {
                "id": plan["id"],
                "nome": plan["name"],
                "preco": float(plan["token_value"]),
                "descricao": plan["description"],
                "feedbacks": plan["feedbacks_available"],
                "missoes": plan["quests_available"],
                "recompensa": f"{float(plan['reward_percentage']) * 100}%"
            }
            for plan in serializer.data
        ])