from rest_framework import serializers
from companies.models import Company
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.registration.views import RegisterView
from validate_docbr import CNPJ


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
    cnpj = serializers.CharField()
    website = serializers.URLField(required=False)
    logo_url = serializers.URLField(required=False)
    corporate_tax_id = serializers.CharField(required=False)

    def save(self, request):
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
