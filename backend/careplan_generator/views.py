from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CarePlan
from .serializers import CarePlanSerializer
from decouple import config
import anthropic # 导入 anthropic 库
import time # 用于模拟异步处理


class CarePlanViewSet(viewsets.ModelViewSet):
    queryset = CarePlan.objects.all().order_by('-created_at')
    serializer_class = CarePlanSerializer

    @action(detail=False, methods=['post'])
    def generate(self, request):
        patient_info = request.data.get('patient_info')
        if not patient_info:
            return Response({'error': 'Patient information is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. 创建 CarePlan 实例并设置为 PENDING 状态
        care_plan = CarePlan.objects.create(patient_info=patient_info, status='PENDING')
        serializer = self.get_serializer(care_plan)

        # 2. 模拟 LLM 处理过程 (实际会是异步，这里简化)
        # 我们可以返回 PENDING 状态，然后在一个单独的进程或线程中更新它
        # 为了 MVP 简单起见，我们在这里同步处理并更新状态

        # 模拟 processing 状态
        care_plan.status = 'PROCESSING'
        care_plan.save()

        try:
            anthropic_api_key = config('ANTHROPIC_API_KEY')
            if not anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY is not configured.")

            client = anthropic.Anthropic(api_key=anthropic_api_key)

            # 这是一个简化的提示，你可以根据需求修改
            prompt_template = f"请根据以下患者信息生成一份详细的护理计划：\n\n患者信息：{patient_info}\n\n护理计划："

            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt_template}
                ]
            )
            generated_text = message.content[0].text if message.content else "No care plan generated."

            care_plan.care_plan_text = generated_text
            care_plan.status = 'COMPLETED'
            care_plan.save()

            return Response(self.get_serializer(care_plan).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            care_plan.status = 'FAILED'
            care_plan.care_plan_text = f"Failed to generate care plan: {str(e)}"
            care_plan.save()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
