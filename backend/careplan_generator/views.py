from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CarePlan, Doctor, Order, Patient
from .serializers import CarePlanSerializer
from .tasks import generate_careplan_task


class CarePlanViewSet(viewsets.ModelViewSet):
    queryset = CarePlan.objects.all().order_by('-created_at')
    serializer_class = CarePlanSerializer

    @action(detail=False, methods=["post"])
    def generate(self, request):
        patient_info = request.data.get("patient_info")
        if not patient_info:
            return Response({"error": "Patient information is required."}, status=status.HTTP_400_BAD_REQUEST)

        patient_name = request.data.get("patient_name") or "Unknown Patient"
        patient_email = request.data.get("patient_email")
        doctor_name = request.data.get("doctor_name")
        doctor_email = request.data.get("doctor_email")

        patient = Patient.objects.create(name=patient_name, email=patient_email)
        doctor = None
        if doctor_name or doctor_email:
            doctor = Doctor.objects.create(name=doctor_name or "Unknown Doctor", email=doctor_email)

        order = Order.objects.create(patient=patient, doctor=doctor, note=patient_info, status="PENDING")

        care_plan = CarePlan.objects.create(order=order, status="PENDING")
        generate_careplan_task.delay(care_plan.id)

        return Response(
            {"message": "Care plan received.", "careplan_id": care_plan.id, "status": care_plan.status},
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        try:
            care_plan = self.get_object()
            serializer = self.get_serializer(care_plan)
            return Response(serializer.data)
        except CarePlan.DoesNotExist:
            return Response({'error': 'Care plan not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        care_plan = self.get_object()
        serializer = self.get_serializer(care_plan)
        response = Response(serializer.data, status=status.HTTP_200_OK)
        response['Content-Disposition'] = f'attachment; filename="careplan_{care_plan.id}.json"'
        return response
