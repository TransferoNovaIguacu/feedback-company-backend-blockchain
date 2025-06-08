from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from .serializers import CompanyRegisterSerializer
from dj_rest_auth.registration.views import RegisterView
import logging

logger = logging.getLogger(__name__)

class CompanyRegisterView(RegisterView):
    serializer_class = CompanyRegisterSerializer

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return Response(response.data, status=status.HTTP_201_CREATED)

        except DRFValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Erro inesperado: {e}", exc_info=True)
            return Response({'detail': 'Erro interno do servidor.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
