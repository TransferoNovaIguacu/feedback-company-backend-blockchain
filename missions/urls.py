from django.urls import path
from missions.views import MissionViewSet, SubmitMissionView

urlpatterns = [
    path('missions/', MissionViewSet.as_view({'get': 'list'})),
    path('missions/<int:pk>/questionnaire/', MissionViewSet.as_view({'get': 'questionnaire'})),
    path('missions/submit/', SubmitMissionView.as_view(), name='submit_mission'),
]