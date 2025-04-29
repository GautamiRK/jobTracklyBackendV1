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
    authentication_classes = []  # Disable SessionAuthentication
    permission_classes = [AllowAny]  # Allow any user to access this view

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'User registered successfully',
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    authentication_classes = []  # Disable SessionAuthentication
    permission_classes = [AllowAny]
    
    def post(self, request):
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
    authentication_classes = []  # Disable SessionAuthentication
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Create or update a job application for the user
        """
        application_id = request.data.get('id')
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({
                'error': 'User ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # If application_id is provided, try to update existing application
        if application_id:
            try:
                application = JobApplication.objects.get(id=application_id, user=user)
                serializer = JobApplicationSerializer(application, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({
                        'message': 'Job application updated successfully',
                    }, status=status.HTTP_200_OK)
                return Response({
                    'error': 'Invalid data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            except JobApplication.DoesNotExist:
                return Response({
                    'error': 'Job application not found'
                }, status=status.HTTP_404_NOT_FOUND)

        # If no application_id, create new application
        serializer = JobApplicationSerializer(data=request.data)
        if serializer.is_valid():
            application = serializer.save(user=user)
            return Response({
                'message': 'Job application created successfully',
            }, status=status.HTTP_201_CREATED)
        return Response({
            'error': 'Invalid data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class GetUserApplicationsView(APIView):
    authentication_classes = []  # Disable SessionAuthentication
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Get all job applications for the authenticated user
        """
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({
                'error': 'User ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            applications = JobApplication.objects.filter(user=user)
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