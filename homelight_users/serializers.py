from rest_framework import serializers
from .models import CustomUser, reviews, roles, technicians, customers
from django.contrib.auth import authenticate
from django.db.models import Avg, Count
from homelight_appointment.models import issue_type

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = roles
        fields = ['role_id', 'name']

class UserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    password = serializers.CharField()
    role_id = serializers.UUIDField()

    def create(self, validated_data):
        role = roles.objects.get(role_id=validated_data['role_id'])
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            role=role
        )
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
        return user



class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        phone = data.get("phone_number")
        password = data.get("password")
        user = authenticate(username=phone, password=password)
        if not user:
            raise serializers.ValidationError("Invalid phone number or password")
        return data
    
class TechnicianSerializer(serializers.ModelSerializer):
    class Meta:
        model = technicians
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = customers
        fields = '__all__'

class UserDisplaySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()

    def get_name(self, obj):
        role_id = self.context.get('role')
        print(f"Fetching name for user: {obj}, role: {role_id}")
        if str(role_id) == "00000000-0000-0000-0000-000000000001":
            technician = technicians.objects.filter(user_id=obj.id).first()
            print("Found technician:", technician)
            return technician.name if technician else None
        elif str(role_id) == "00000000-0000-0000-0000-000000000002":
            customer = customers.objects.filter(user_id=obj.id).first()
            print("Found customer:", customer)
            return customer.name if customer else None
        return None


    def get_photo(self, obj):
        role_id = self.context.get('role')
        if str(role_id) == "00000000-0000-0000-0000-000000000001":
            tech = technicians.objects.filter(user_id=obj).first()
            return tech.profile_picture_url.url if tech and tech.profile_picture_url else None
        elif str(role_id) == "00000000-0000-0000-0000-000000000002":
            cust = customers.objects.filter(user_id=obj).first()
            return cust.profile_picture_url.url if cust and cust.profile_picture_url else None
        return None

class ReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = reviews
        fields = [
            'review_id',
            'user_id',
            'reviewed_by',
            'rate',
            'review_text',
            'created_at'
        ]
        read_only_fields = [ 'created_at']
    def create(self, validated_data):
        reviews_rate = reviews.objects.create(**validated_data)
        return reviews_rate
    

class ReviewListSerializer(serializers.ModelSerializer):
    reviewed_by_name = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    class Meta:
        model = reviews
        fields = [
            'review_id',
            'user_id',
            'reviewed_by',
            'reviewed_by_name',  # just full name
            'rate',
            'review_text',
            'created_at',
            'avg_rating',
            'review_count'
        ]
        read_only_fields = ['created_at']

    def get_reviewed_by_name(self, obj):
        role_id = getattr(obj.reviewed_by, 'role_id', None)

        if role_id == "001":
            # Technician name
            try:
                technician = technicians.objects.get(user_id=obj.reviewed_by.id)
                return technician.name
            except technicians.DoesNotExist:
                return None
        else:
            # Customer name
            try:
                customer = customers.objects.get(user_id=obj.reviewed_by.id)
                return customer.name
            except customers.DoesNotExist:
                return None
    def get_avg_rating(self, obj):
        return reviews.objects.filter(user_id=obj.user_id).aggregate(avg=Avg('rate'))['avg'] or 0

    def get_review_count(self, obj):
        return reviews.objects.filter(user_id=obj.user_id).count()