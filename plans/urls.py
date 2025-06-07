from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlanViewSet, ContractedPlanViewSet

router = DefaultRouter()
router.register(r'plans', PlanViewSet, basename='plan')
router.register(r'contracted-plans', ContractedPlanViewSet, basename='contractedplan')

urlpatterns = [
    path('', include(router.urls)),
]