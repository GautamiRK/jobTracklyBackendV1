from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, JobApplicationSerializer
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import AllowAny
from .models import JobApplication, User

class UserRegistrationView(APIView):
    def get(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'User registered successfully',
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'username': user.username
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = []
    
    def get(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({
                'error': 'Please provide both email and password'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        user = authenticate(email=email, password=password)
        
        if user is None:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        if not user.is_active:
            return Response({
                'error': 'User account is disabled'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        # Create session for the user
        login(request, user)
        
        return Response({
            'message': 'Login successful',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'username': user.username
            }
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)

class CreateJobApplicationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Create a new job application for the authenticated user
        """
        print('Request data:', request.data)
        serializer = JobApplicationSerializer(data=request.data)
        if serializer.is_valid():
            application = serializer.save(user=request.user)
            return Response({
                'message': 'Job application created successfully',
                'application': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'error': 'Invalid data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class GetUserApplicationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get all job applications for the authenticated user
        """
        try:
            applications = JobApplication.objects.filter(user=request.user)
            serializer = JobApplicationSerializer(applications, many=True)
            return Response({
                'message': 'Applications retrieved successfully',
                'applications': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Failed to retrieve applications',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)