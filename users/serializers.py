from dj_rest_auth.serializers import UserDetailsSerializer, LoginSerializer
from django.db import IntegrityError
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from dj_rest_auth.registration.serializers import RegisterSerializer
from users.models import CommonUser
from django.core.validators import MinLengthValidator

User = get_user_model()

class CustomUserDetailsSerializer(UserDetailsSerializer):
    
    class Meta(UserDetailsSerializer.Meta):
        model = User
        fields = ('pk', 'email', 'user_type', 'wallet_address')
        read_only_fields = ('email',)

class CustomRegisterSerializer(serializers.Serializer):
    
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("As senhas não coincidem.")
        try:
            validate_password(data['password1'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password1": list(e.messages)})
        return data

    def get_cleaned_data(self):
        return {
            'email': self.validated_data.get('email', ''),
            'password1': self.validated_data.get('password1', ''),
        }

    def save(self, request):
        user = User.objects.create_user(
            email=self.validated_data['email'],
            password=self.validated_data['password1']
        )
        return user
    
class CommonUserRegisterSerializer(RegisterSerializer):
    
    username = None
    full_name = serializers.CharField()
    cpf = serializers.CharField()

    def save(self, request):
        try:
            user = CommonUser(
                email=self.validated_data['email'],
                password=self.validated_data['password1'],
                full_name=self.validated_data['full_name'],
                cpf=self.validated_data['cpf'],
                user_type='COMMON'
            )
            user.set_password(self.validated_data['password1'])
            user.full_clean()
            user.save()
            return user
        
        except DjangoValidationError as e:
            raise DRFValidationError(e.message_dict)
        
        except IntegrityError as e:
            if 'email' in str(e).lower():
                raise DRFValidationError({'email': 'Este e-mail já está cadastrado.'})
            if 'cpf' in str(e).lower():
                raise DRFValidationError({'cpf': 'CPF já está cadastrado.'})
            raise DRFValidationError({'detail': 'Erro de integridade no banco.'})
    
class CommonUserProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CommonUser
        fields = ['full_name', 'cpf', 'wallet_address', 'total_tokens_earned', 'completed_missions']
        read_only_fields = ['cpf', 'total_tokens_earned', 'completed_missions']
        

class CustomLoginSerializer(LoginSerializer):
    
    username = None
    email = serializers.EmailField(required=True) 
    
class LogoutSerializer(serializers.Serializer):
    
    refresh = serializers.CharField()
    
    
class WalletAddressSerializer(serializers.ModelSerializer):
    wallet_address = serializers.CharField(
        max_length=42,
        required=True,
        validators=[MinLengthValidator(42)],
        help_text="Endereço da carteira blockchain (42 caracteres)"
    )

    class Meta:
        model = User
        fields = ['wallet_address']
        extra_kwargs = {
            'wallet_address': {
                'error_messages': {
                    'min_length': 'O endereço da carteira deve ter exatamente 42 caracteres',
                    'blank': 'O endereço da carteira é obrigatório'
                }
            }
        }

    def validate_wallet_address(self, value):
        value = value.strip()
        if not value.startswith('0x'):
            raise serializers.ValidationError("O endereço deve começar com '0x'")
        return value
