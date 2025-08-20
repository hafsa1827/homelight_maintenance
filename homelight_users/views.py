import uuid
from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ReviewListSerializer, ReviewsSerializer, UserSerializer,LoginSerializer,RoleSerializer,TechnicianSerializer, CustomerSerializer,UserDisplaySerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .models import CustomUser, reviews, roles, customers, technicians
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout

class RoleListView(APIView):
    def get(self, request):
        role = roles.objects.all()
        serializer = RoleSerializer(role, many=True)
        return Response(serializer.data)
    

    
class UserRegistrationView(APIView):
    def get(self, request):
        return Response({"message": "GET request successful"})

    def post(self, request):
        serializer =UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User registered successfully",
                "user": {
                    
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "password": user.password,
                }
            }, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)  # Add this line
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')

        if not phone_number or not password:
            return Response({'error': 'Missing phone_number or password'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=phone_number, password=password)

        if user is not None:
            login(request, user)
            return Response({
                "id": user.id,
                "phone_number": user.phone_number,
                "email": user.email,
                "role": str(user.role.role_id),
                "message": "Login successful"
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        

@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

class UpdateProfileView(APIView):
    
    def post(self, request):
        user_id = request.data.get('user_id')
        role = request.data.get('role')
        image = request.FILES.get('profile_picture_url')

        if not user_id or not role:
            return Response({"error": "Missing user_id or role"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = None

        # Merge data and files for serializer
        data = request.data.copy()
        if image:
            data['profile_picture_url'] = image

        if role == '00000000-0000-0000-0000-000000000001':
            profile, created = technicians.objects.get_or_create(user_id=user)
            serializer = TechnicianSerializer(profile, data=data, partial=True)
        elif role == '00000000-0000-0000-0000-000000000002':
            profile, created = customers.objects.get_or_create(user_id=user)
            serializer = CustomerSerializer(profile, data=data, partial=True)
        else:
            return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.save()
            action = "created" if created else "updated"
            return Response({"success": f"Profile {action} successfully."})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
def user_profile(request, user_id):
    if request.method == 'GET':
        try:
            profile = technicians.objects.get(user_id=user_id)
            serializer = TechnicianSerializer(profile)
        except technicians.DoesNotExist:
            try:
                profile = customers.objects.get(user_id=user_id)
                serializer = CustomerSerializer(profile)
            except customers.DoesNotExist:
                return Response({'detail': 'User not found'}, status=404)
        return Response(serializer.data)

    if request.method == 'PUT':
        try:
            profile = technicians.objects.get(user_id=user_id)
            serializer = TechnicianSerializer(profile, data=request.data, partial=True)
        except technicians.DoesNotExist:
            try:
                profile = customers.objects.get(user_id=user_id)
                serializer = CustomerSerializer(profile, data=request.data, partial=True)
            except customers.DoesNotExist:
                return Response({'detail': 'User not found'}, status=404)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
class UserProfileView(APIView):
    def get(self, request, user_id,role):
        try:
            user = CustomUser.objects.get(id=user_id)
            role = roles.objects.get(role_id=role)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserDisplaySerializer(user, context={'role': str(role.role_id)})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class GetTechnicianByUserView(APIView):
    def get(self, request, user_id):
        try:
            technician = technicians.objects.get(user_id=user_id)
            serializer = TechnicianSerializer(technician)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except technicians.DoesNotExist:
            return Response({'error': 'Technician not found'}, status=status.HTTP_404_NOT_FOUND)
        
class SaveReview(APIView):
    def post(self, request):
        serializer = ReviewsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class GetReview(APIView):
    def get(self, request):
        user_id = request.GET.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            review = reviews.objects.filter(user_id=user_id)
            serializer = ReviewListSerializer(review, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except reviews.DoesNotExist:
            return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
