from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from .models import CarePlan
from .serializers import CarePlanSerializer, GenerateCarePlanSerializer
from .services import create_careplan_and_enqueue, get_careplan_status_payload


class CarePlanViewSet(viewsets.ModelViewSet):
    queryset = CarePlan.objects.all().order_by('-created_at')
    serializer_class = CarePlanSerializer

    @action(detail=False, methods=["post"])
    def generate(self, request):
        serializer = GenerateCarePlanSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": "Patient information is required."}, status=status.HTTP_400_BAD_REQUEST)

        care_plan = create_careplan_and_enqueue(serializer.validated_data)

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


@api_view(["GET"])
def careplan_status(request, careplan_id):
    try:
        payload = get_careplan_status_payload(careplan_id)
    except CarePlan.DoesNotExist:
        return Response({"error": "Care plan not found."}, status=status.HTTP_404_NOT_FOUND)

    return Response(payload, status=status.HTTP_200_OK)


@api_view(["POST"])
def create_order(request):
    serializer = GenerateCarePlanSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"error": "Patient information is required."}, status=status.HTTP_400_BAD_REQUEST)

    care_plan = create_careplan_and_enqueue(serializer.validated_data)
    order = care_plan.order

    return Response(
        {"message": "Order received.", "order_id": order.id, "careplan_id": care_plan.id, "status": care_plan.status},
        status=status.HTTP_202_ACCEPTED,
    )
