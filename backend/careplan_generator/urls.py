from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CarePlanViewSet, careplan_status, create_order

router = DefaultRouter()
router.register(r'careplans', CarePlanViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('careplan/<int:careplan_id>/status/', careplan_status),
    path('orders/', create_order),
]
