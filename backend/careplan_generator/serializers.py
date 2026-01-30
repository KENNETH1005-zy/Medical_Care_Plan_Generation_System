from rest_framework import serializers
from .models import CarePlan

class CarePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarePlan
        fields = '__all__'
        read_only_fields = ('care_plan_text', 'status', 'created_at', 'updated_at')
