from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer, UserSerializer
from rest_framework.permissions import AllowAny

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            data = request.data
            serializer = UserSerializer(data=data)  

            if not serializer.is_valid():
                return Response({
                    'data': serializer.errors,
                    'message': 'Something went wrong..',
                }, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()
            # user = User.objects.get()
            # send_otp_via_email(user.email)

            return Response({
                'data': {},
                'message': 'User registered successfully.',
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print('e:',e)
            return Response({   
                'data': {},  
                'message': 'Something went wrong..',
            }, status=status.HTTP_400_BAD_REQUEST)
        


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = request.data
            serializer = LoginSerializer(data=data)

            if not serializer.is_valid():
                return Response({
                    'data': serializer.errors,
                    'message': 'Validation failed.',
                }, status=status.HTTP_400_BAD_REQUEST)

            res = serializer.get_jwt_token(serializer.validated_data)
            return Response({
                'data': res['data'],
                'message': res['message'],
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Unexpected Error: {e}")
            return Response({
                'data': {},
                'message': 'Something went wrong.',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

