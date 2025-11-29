from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SystemStatusView, BatchUploadView, MaxFlowCalculationView, 
    KnapsackCalculationView, TransportFlowViewSet, ResourceViewSet,ResourceUploadView
)

router = DefaultRouter()
router.register(r'flows', TransportFlowViewSet, basename='transportflow')
router.register(r'resources', ResourceViewSet, basename='resource')

urlpatterns = [
    path('api/status/', SystemStatusView.as_view()),
    path('api/upload/', BatchUploadView.as_view()),
    path('api/upload/resources/', ResourceUploadView.as_view(), name='api_upload_resources'),
    path('api/calculate-flow/', MaxFlowCalculationView.as_view()),
    path('api/calculate-knapsack/', KnapsackCalculationView.as_view()),
    path('api/', include(router.urls)),
]