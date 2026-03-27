from rest_framework import serializers
from .models import CarePlan, Doctor, Order, Patient


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = "__all__"


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class CarePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarePlan
        fields = "__all__"
        read_only_fields = ("care_plan_text", "status", "created_at", "updated_at")


class GenerateCarePlanSerializer(serializers.Serializer):
    patient_info = serializers.CharField(required=True, allow_blank=False)
    patient_name = serializers.CharField(required=False, allow_blank=True)
    patient_email = serializers.CharField(required=False, allow_blank=True)
    doctor_name = serializers.CharField(required=False, allow_blank=True)
    doctor_email = serializers.CharField(required=False, allow_blank=True)
