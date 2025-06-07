from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CompanySerializer, CompanyRegisterSerializer
from companies.models import Company
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from dj_rest_auth.registration.views import RegisterView


class InitialView(APIView):
    
    def get(self, request):
        return Response({"message": "Endpoint working!"})
    
class CompanyViewSet(viewsets.ModelViewSet):
    
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    
class CompanyRegisterView(RegisterView):
    
    serializer_class = CompanyRegisterSerializer