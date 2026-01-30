from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CarePlanViewSet

router = DefaultRouter()
router.register(r'careplans', CarePlanViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
