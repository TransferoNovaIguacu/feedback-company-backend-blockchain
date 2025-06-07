from rest_framework import serializers
from .models import Plan, ContractedPlan

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'

class ContractedPlanSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = ContractedPlan
        fields = '__all__'
        read_only_fields = ('purchase_date', 'remaining_feedbacks', 'remaining_quests')

    def get_is_expired(self, obj):
        return obj.is_expired()