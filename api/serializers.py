from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name','last_name','username','email','password','is_verified']

    def create(self,validated_data):
        user = User.objects.create(
        first_name = validated_data['first_name'],
        last_name = validated_data['last_name'],
        email = validated_data['email'],
        username = validated_data['username'],
        )

        user.set_password(validated_data['password'])
        user.save()
        return user
    


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        # Use the authenticate function
        user = authenticate(request=self.context.get('request'), username=email, password=password)
        
        if not user:
            raise serializers.ValidationError('Invalid email or password.')

        if not user.is_active:
            raise serializers.ValidationError('User account is inactive.')

        if not user.is_verified:  # Assuming `is_verified` is a custom field
            raise serializers.ValidationError('User account is not verified.')

        data['user'] = user
        return data

    def get_jwt_token(self, data):
        user = data['user']
        refresh = RefreshToken.for_user(user)
        return {
            'message': 'Login successful.',
            'data': {
                'token': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                },
                'user': {
                    'email': user.email,
                    'name': user.get_full_name() if hasattr(user, 'get_full_name') else user.username,
                }
            }
        }
