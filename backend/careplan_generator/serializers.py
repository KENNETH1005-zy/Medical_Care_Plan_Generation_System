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
