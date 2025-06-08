from rest_framework import serializers
from .models import Mission, Question, MissionQueue

class QuestionSerializer(serializers.ModelSerializer):
    options = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = Question
        fields = ['id', 'title', 'description', 'options']

class MissionSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Mission
        fields = ['id', 'title', 'url', 'description', 'mission_type', 'token_reward', 'questions', 'status']
        read_only_fields = ['id', 'token_reward', 'status']
class MissionSubmitSerializer(serializers.Serializer):
    mission_id = serializers.IntegerField()
    answers = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )

    def validate(self, data):
        mission_id = data.get('mission_id')
        answers = data.get('answers', [])

        try:
            mission = Mission.objects.get(id=mission_id, status='IN_PROGRESS')
        except Mission.DoesNotExist:
            raise serializers.ValidationError("Missão não encontrada ou não está em andamento.")

        if len(answers) != mission.questions.count():
            raise serializers.ValidationError("Número de respostas inválido.")

        for answer in answers:
            question_id = answer.get('id')
            reply = answer.get('reply')
            try:
                question = mission.questions.get(id=question_id)
                if reply not in question.options:
                    raise serializers.ValidationError(f"Resposta '{reply}' inválida.")
            except question.DoesNotExist:
                raise serializers.ValidationError(f"Pergunta {question_id} não existe.")
        return data