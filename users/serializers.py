from dj_rest_auth.serializers import UserDetailsSerializer, LoginSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from dj_rest_auth.registration.serializers import RegisterSerializer
from users.models import CommonUser

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
        user = CommonUser.objects.create_user(
            email=self.validated_data['email'],
            password=self.validated_data['password1'],
            full_name=self.validated_data['full_name'],
            cpf=self.validated_data['cpf'],
            user_type='COMMON'
        )
        return user
    
class CommonUserProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CommonUser
        fields = ['full_name', 'cpf', 'wallet_address', 'total_tokens_earned', 'completed_missions']
        read_only_fields = ['cpf', 'total_tokens_earned', 'completed_missions']
        

class CustomLoginSerializer(LoginSerializer):
    
    username = None
    email = serializers.EmailField(required=True) 
