from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Mission, MissionQueue
from .serializers import MissionSerializer, MissionSubmitSerializer
from plans.models import ContractedPlan
from blockchain.utils.rewards import process_reward_batch
from rest_framework.views import APIView

class MissionViewSet(viewsets.ModelViewSet):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def questionnaire(self, request, pk=None):
        """Retorna o questionário da missão"""
        mission = self.get_object()
        questions = mission.questions.all()
        return Response({
            'id': mission.id,
            'titulo': mission.title,
            'url': mission.url,
            'description': mission.description,
            'questions': [
                {
                    'id': q.id,
                    'title': q.title,
                    'description': q.description,
                    'options': q.options
                } for q in questions
            ]
        })

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Lista missões disponíveis para o usuário comum"""
        missions = Mission.objects.filter(status='PENDING')
        serializer = self.get_serializer(missions, many=True)
        return Response(serializer.data)
class SubmitMissionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MissionSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mission_id = serializer.validated_data['mission_id']
        answers = serializer.validated_data['answers']

        try:
            mission = Mission.objects.get(id=mission_id)
            mission_queue = MissionQueue.objects.get(user=request.user, mission=mission)
        except (Mission.DoesNotExist, MissionQueue.DoesNotExist):
            return Response({"error": "Missão não encontrada ou não está em andamento"}, status=404)

        mission.status = 'COMPLETED'
        mission.save()

        # ✅ Gera recompensa
        from blockchain.models import RewardTransaction
        RewardTransaction.objects.create(
            user=request.user,
            amount=mission.token_reward,
            tx_type='REWARD',
            status='PENDING'
        )

        from blockchain.utils.rewards import process_reward_batch
        process_reward_batch() 

        mission_queue.delete()
        return Response({"success": "Missão concluída", "tokens_earned": mission.token_reward})