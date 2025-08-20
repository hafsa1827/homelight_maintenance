from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model

from .models import  service_gallery
from homelight_users.serializers import UserDisplaySerializer
from homelight_users.models import technicians,CustomUser

from .models import technician_specialization
from homelight_appointment.models import issue_type
from homelight_users.models import reviews
from django.db.models import Avg, Count

class GallerySerializer(serializers.ModelSerializer):
    issue_name = serializers.CharField(source='issue_id.type_name', read_only=True)
    role = serializers.UUIDField(source='role.role_id', read_only=True)
    user = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = service_gallery
        fields = [
            'gallery_id',
            'gallery_url',
            'user_id',
            'role',
            'issue_id',
            'issue_name',
            'user',
            'avg_rating',
            'review_count'
        ]

    def get_user(self, obj):
        user = obj.user_id
        role_id = obj.role.role_id
        return UserDisplaySerializer(user, context={'role': str(role_id)}).data

    def get_avg_rating(self, obj):
        return reviews.objects.filter(user_id=obj.user_id).aggregate(avg=Avg('rate'))['avg'] or 0

    def get_review_count(self, obj):
        return reviews.objects.filter(user_id=obj.user_id).count()
    
    
class TechnicianSpecializationSerializer(serializers.ModelSerializer):
    issue = serializers.PrimaryKeyRelatedField(queryset=issue_type.objects.all())

    issue_name = serializers.SerializerMethodField()
    technician_name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = technician_specialization
        fields = [
            'specialization_id',
            'user',
            'technician_name',
            'phone',
            'profile_picture_url',
            'issue',
            'issue_name',
            'tools_owned',
            'specialization_details',
            'years_of_experience',
            'base_price',
        ]

    def get_issue_name(self, obj):
        return obj.issue.type_name

    def get_technician_name(self, obj):
        try:
            technician = technicians.objects.get(user_id=obj.user)
            return technician.name
        except technicians.DoesNotExist:
            return ''
        
    def get_phone(self, obj):
        try:
            technician = technicians.objects.get(user_id=obj.user)
            return technician.phone
        except technicians.DoesNotExist:
            return ''

    def get_profile_picture_url(self, obj):
        request = self.context.get('request')
        try:
            technician = technicians.objects.get(user_id=obj.user)
            photo = technician.profile_picture_url
            if photo and hasattr(photo, 'url'):
                return request.build_absolute_uri(photo.url) if request else photo.url
        except technicians.DoesNotExist:
            pass
        return ''
