from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CarePlan, Doctor, Order, Patient
from .serializers import CarePlanSerializer
from decouple import config
import anthropic # 导入 anthropic 库
import time # 用于模拟异步处理


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

        order = Order.objects.create(patient=patient, doctor=doctor, note=patient_info)

        care_plan = CarePlan.objects.create(order=order, status="PENDING")
        care_plan.status = "PROCESSING"
        care_plan.save()

        try:
            anthropic_api_key = config("ANTHROPIC_API_KEY")
            if not anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY is not configured.")

            client = anthropic.Anthropic(api_key=anthropic_api_key)

            prompt_template = (
                "Generate a detailed care plan based on the patient information below.\n\n"
                f"Patient information: {patient_info}\n\n"
                "Care plan:"
            )

            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt_template}],
            )
            generated_text = message.content[0].text if message.content else "No care plan generated."

            care_plan.care_plan_text = generated_text
            care_plan.status = "COMPLETED"
            care_plan.save()

            return Response(self.get_serializer(care_plan).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            care_plan.status = "FAILED"
            care_plan.care_plan_text = f"Failed to generate care plan: {str(e)}"
            care_plan.save()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
