from django.db import IntegrityError
from rest_framework import serializers
from companies.models import Company
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.registration.views import RegisterView
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.utils import DataError
from validate_docbr import CNPJ
import logging

logger = logging.getLogger(__name__)


class CompanySerializer(serializers.ModelSerializer):
    
    def validate_cnpj(self, value):
        cnpj = ''.join(filter(str.isdigit, value))
        validator = CNPJ()
        if not validator.validate(cnpj):
            raise serializers.ValidationError("CNPJ inválido.")
        return cnpj
    
    class Meta:
        model = Company
        fields = [
            'id',
            'commercial_name',
            'legal_name',
            'business_area',
            'cnpj',
            'website',
            'logo_url',
            'verified',
            'tokens_balance',
            'corporate_tax_id'
        ]
        read_only_fields = ['id', 'verified', 'tokens_balance']
        
class CompanyRegisterSerializer(RegisterSerializer):
    
    username = None
    commercial_name = serializers.CharField()
    legal_name = serializers.CharField()
    business_area = serializers.CharField(required=False)
    cnpj = serializers.CharField(error_messages={
        'required': 'O campo CNPJ é obrigatório.',
        'invalid': 'CNPJ inválido.'
    })
    website = serializers.URLField(required=False)
    logo_url = serializers.URLField(required=False)
    corporate_tax_id = serializers.CharField(required=False)
    
    def validate_cnpj(self, value):
        cnpj = ''.join(filter(str.isdigit, value))
        if not CNPJ().validate(cnpj):
            raise serializers.ValidationError("CNPJ inválido.")
        return cnpj

    def save(self, request):
        try:
            company = Company.objects.create_user(
                email=self.validated_data['email'],
                password=self.validated_data['password1'],
                commercial_name=self.validated_data['commercial_name'],
                legal_name=self.validated_data['legal_name'],
                business_area=self.validated_data.get('business_area', ''),
                cnpj=self.validated_data['cnpj'],
                website=self.validated_data.get('website', ''),
                logo_url=self.validated_data.get('logo_url', ''),
                corporate_tax_id=self.validated_data.get('corporate_tax_id', ''),
                user_type = "COMPANY"
            )
            return company
        except IntegrityError as e:
                message = str(e).lower()
                if "unique constraint" in message or "unique" in message:
                    if "email" in message:
                        raise ValidationError({"email": ["Este e-mail já está em uso."]})
                    if "cnpj" in message:
                        raise ValidationError({"cnpj": ["Este CNPJ já está cadastrado."]})
                raise ValidationError({"detail": "Erro de integridade nos dados."})

        except DjangoValidationError as e:
            raise ValidationError(e.message_dict if hasattr(e, "message_dict") else {"detail": str(e)})

        except DataError:
                raise ValidationError({"detail": "Erro ao salvar dados: verifique os campos informados."})

        except Exception as e:
                logger.error(f"Erro inesperado no registro da empresa: {e}", exc_info=True)
                raise serializers.ValidationError({"detail": "Erro interno do servidor."})
    
class CompanyRegisterView(RegisterView):
    
    serializer_class = CompanyRegisterSerializer
    
class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'commercial_name', 'legal_name', 'business_area', 'cnpj', 'website',
            'logo_url', 'verified', 'tokens_balance', 'corporate_tax_id', 'wallet_address'
        ]
        read_only_fields = ['cnpj', 'verified', 'tokens_balance']
