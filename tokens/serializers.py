from rest_framework import serializers

class AmountSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=36, decimal_places=18)
