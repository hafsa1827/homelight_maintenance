import uuid
from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import GallerySerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .models import service_gallery, technician_specialization
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from homelight_users.models import CustomUser, roles, technicians
from homelight_appointment.models    import issue_type
from django.shortcuts import get_object_or_404
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import GallerySerializer, TechnicianSpecializationSerializer

class GalleryListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({"error": "Missing user_id"}, status=status.HTTP_400_BAD_REQUEST)

        galleries = service_gallery.objects.filter(user_id=user_id)
        serializer = GallerySerializer(galleries, many=True)
        return Response(serializer.data)
    
class GalleryListByUserId(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        issue_id = request.query_params.get('issue_id')

        if not user_id:
            return Response({"error": "Missing user_id"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user_id_int = int(user_id)  # تحويل user_id إلى int
        except ValueError:
            return Response({"error": "Invalid user_id"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            issue_uuid = uuid.UUID(issue_id)
        except (ValueError, TypeError):
            return Response({"error": "Invalid issue_id"}, status=status.HTTP_400_BAD_REQUEST)
        galleries = service_gallery.objects.filter(user_id=user_id_int, issue_id=issue_uuid)
        serializer = GallerySerializer(galleries, many=True)
        return Response(serializer.data)
    

class GalleryIssueListView(APIView):
    
    def post(self, request):
        issue_ids = request.data.get('issue_ids', [])
        if not issue_ids:
            return Response({"detail": "No issue_ids provided."}, status=400)
        try:
            valid_ids = [uuid.UUID(i) for i in issue_ids]
        except ValueError:
            return Response({"detail": "Invalid UUID in issue_ids"}, status=400)
        galleries = service_gallery.objects.filter(issue_id__in=valid_ids)
        serializer = GallerySerializer(galleries, many=True, context={'request': request})

        return Response(serializer.data)


class UpdateGalleryView(APIView):
    
    def post(self, request):
        user_id = request.data.get('user_id')
        role_id = request.data.get('role')
        gallery_url = request.FILES.get('gallery_url')
        issue_id = request.POST.get('issue_id')

        if not user_id or not role_id or not issue_id:
            return Response({"error": "Missing user_id or role or issue"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(CustomUser, pk=user_id)
        issue = get_object_or_404(issue_type, pk=issue_id)
        role = get_object_or_404(roles, pk=role_id)

        if not gallery_url:
            return Response({"error": "Missing image file"}, status=status.HTTP_400_BAD_REQUEST)

        gallery = service_gallery.objects.create(
            user_id=user,
            issue_id=issue,
            role=role,
            gallery_url=gallery_url
        )

        serializer = GallerySerializer(gallery)        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
class SaveSpecializationView(APIView):
    def post(self, request):
        serializer = TechnicianSpecializationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class TechnicianSpecializationView(APIView):
    def get(self, request, user_id):
        try:
            technician = CustomUser.objects.get(id=user_id)
            specializations = technician_specialization.objects.filter(user=technician)
            serializer = TechnicianSpecializationSerializer(specializations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except technicians.DoesNotExist:
            return Response({'error': 'Technician not found'}, status=status.HTTP_404_NOT_FOUND)
        
class TechnicianSpecializationViewwithIssueId(APIView):
    def get(self, request, issue_id):
        try:
            issue = issue_type.objects.get(type_id=issue_id)
            specializations = technician_specialization.objects.filter(issue=issue)
            serializer = TechnicianSpecializationSerializer(specializations, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except issue.DoesNotExist:
            return Response({'error': 'Issue not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
class TechnicianSpecializationViewwithUserId(APIView):
    def get(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            specializations = technician_specialization.objects.filter(user=user)
            serializer = TechnicianSpecializationSerializer(specializations, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except user.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)