from homelight_technician.models import service_gallery
from rest_framework import serializers
from django.contrib.auth import authenticate
import subprocess
import os
from django.core.files.base import ContentFile
from tempfile import NamedTemporaryFile
from .models import calenders, invoice_history, issue_type,technician_service_history,customer_requests,payment_transactions,invoices,request_gallery,technician_services, troubleshooting_gallery,troubleshooting_history
from homelight_users.models import CustomUser,roles,customers,technicians
from homelight_technician.serializers import GallerySerializer
from homelight_technician.models import technician_specialization
from homelight_users.models import reviews
from django.db.models import Avg, Count


def convert_m4a_to_mp3_django(file_field):
    if file_field and file_field.name.endswith('.m4a'):
        with NamedTemporaryFile(delete=False, suffix=".m4a") as temp_input:
            temp_input.write(file_field.read())
            temp_input_path = temp_input.name

        temp_output_path = temp_input_path.replace('.m4a', '.mp3')

        subprocess.run([
            'ffmpeg',
            '-y',
            '-i', temp_input_path,
            temp_output_path
        ], check=True)

        with open(temp_output_path, 'rb') as f:
            content = f.read()
            new_filename = os.path.splitext(file_field.name)[0] + '.mp3'
            mp3_file = ContentFile(content, name=new_filename)

        os.remove(temp_input_path)
        os.remove(temp_output_path)

        return mp3_file

    return file_field

class TechnicianStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = technician_services
        fields = ['status','reason']
        
class TechnicianHistoryStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = technician_service_history
        fields = ['status','reason']
        
class IssueTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = issue_type
        fields = ['type_id', 'type_name','issue_icon']
        
class IssueTechnicianSerializer(serializers.ModelSerializer):
    issue_name = serializers.CharField(source='issue.type_name', read_only=True)
    class Meta:
        model = technician_specialization
        fields = ['issue', 'issue_name']

class CustomerRequestSerializer(serializers.ModelSerializer):
    gallery_url = serializers.ImageField(write_only=True, required=False)
    audio_url = serializers.FileField(write_only=True, required=False)
    payment_method = serializers.CharField(required=False)
    status = serializers.CharField(required=False)
    ar_support_enabled = serializers.BooleanField(required=False)
    requested_date = serializers.DateTimeField(required=False)
    technician_id = serializers.CharField(write_only=True, required=False)
    tools_owned = serializers.CharField(write_only=True, required=False)
    basePrice = serializers.CharField(write_only=True, required=False)
    specialization_details = serializers.CharField(write_only=True, required=False)
    issue_name = serializers.CharField(source='issue_type.type_name', read_only=True)

    class Meta:
        model = customer_requests
        fields = [
            'service_id',
            'customer_id',
            'issue_type',
            'issue_description',
            'payment_method',
            'ar_support_enabled',
            'requested_date',
            'status',
            'gallery_url',
            'audio_url',
            'issue_name',
            'technician_id',
            'tools_owned',
            'specialization_details',
            'basePrice',
        ]

    def create(self, validated_data):
        gallery_url = validated_data.pop('gallery_url', None)
        audio_url = validated_data.pop('audio_url', None)
        technician_id = validated_data.pop('technician_id', None)
        tools_owned = validated_data.pop('tools_owned', '')
        specialization_details = validated_data.pop('specialization_details', '')
        basePrice = validated_data.pop('basePrice', '')

        # Create the main request
        request_instance = customer_requests.objects.create(**validated_data)

        # Access files from request context
        request_obj = self.context['request']
        gallery_files = request_obj.FILES.getlist('gallery_url')
        audio_file = request_obj.FILES.get('audio_url')

        if audio_file:
            audio_file = convert_m4a_to_mp3_django(audio_file)
        
        for file in gallery_files:
            request_gallery.objects.create(
                request_id=request_instance,
                gallery_url=file,
                audio_url=audio_file
                
            )

        # Save technician service if technician_id exists
        if technician_id:
            notes_text = f"{tools_owned}\n {specialization_details}"
            tech=technician_services.objects.create(
                technician_id=CustomUser.objects.get(id=technician_id),
                request_id=request_instance,
                notes=notes_text,
                custom_price=basePrice,
                status="Accepted"
            )
            technician_service_history.objects.create(
                service_id=tech.service_id,
                technician_id=tech.technician_id,
                request_id=tech.request_id,
                custom_price=tech.custom_price,
                estimated_duration=tech.estimated_duration,
                notes=tech.notes,
                audio_url=tech.audio_url,
                status=tech.status,
                reason=tech.reason,
                created_at=tech.created_at
            )

        return request_instance

class CustomerRequestListSerializer(serializers.ModelSerializer):
    media_urls  = serializers.SerializerMethodField()
    media_url  = serializers.SerializerMethodField()
    issue_name = serializers.CharField(source='issue_type.type_name', read_only=True)
    customer_information = serializers.SerializerMethodField()
    technician_status = serializers.SerializerMethodField()
    technician_price = serializers.SerializerMethodField()
    tech_service_id =  serializers.SerializerMethodField()
    class Meta:
        model = customer_requests
        fields = [
            'service_id',
            'customer_id',
            'issue_type',
            'issue_description',
            'payment_method',
            'ar_support_enabled',
            'requested_date',
            'status',
            'media_urls',
            'media_url',
            'issue_name',
            'customer_information',
            'technician_status',
            'technician_price',
            'tech_service_id'
        ]

    def get_media_url(self, obj):
        gallery = request_gallery.objects.filter(request_id=obj.service_id).first()
        if not gallery:
            return {"gallery_url": None, "audio_url": None}
        
        request = self.context.get('request')
        build_url = lambda file: request.build_absolute_uri(file.url) if request and file else (file.url if file else None)

        return {
            "gallery_url": build_url(gallery.gallery_url),
            "audio_url": build_url(gallery.audio_url)
        }
    def get_media_urls(self, obj):
        gallery = request_gallery.objects.filter(request_id=obj.service_id)
        if not gallery:
            return {"gallery_url": None, "audio_url": None}
        
        request = self.context.get('request')
        build_url = lambda file: request.build_absolute_uri(file.url) if request and file else (file.url if file else None)

        return {
            "gallery_urls": [build_url(g.gallery_url) for g in gallery if g.gallery_url],
            "audio_url": build_url(gallery.first().audio_url) if gallery.exists() else None,
        }
    def get_customer_information(self, obj):
        try:
            request = self.context.get('request')
            customer = customers.objects.get(user_id=obj.customer_id)

            profile_picture = customer.profile_picture_url
            picture_url = None

            if profile_picture:
                if request:
                    picture_url = request.build_absolute_uri(profile_picture.url)
                else:
                    picture_url = profile_picture.url

            return {
                "full_name": customer.name,
                "phone_number": customer.phone,
                "email": customer.email,
                "address": customer.address,
                "picture": picture_url,
                "custom_id":str(customer.user_id)
                
            }
        except customers.DoesNotExist:
            return None
    def get_technician_status(self, obj):
        service = technician_services.objects.filter(request_id=obj.service_id).first()
        return service.status if service else None
    def get_technician_price(self, obj):
        service = technician_services.objects.filter(request_id=obj.service_id).first()
        return service.custom_price if service else None 
    def get_tech_service_id(self, obj):
        service = technician_services.objects.filter(request_id=obj.service_id).first()
        return service.service_id if service else None     
        
class TechnicianServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = technician_services
        fields = [
            'service_id',
            'technician_id',
            'request_id',
            'custom_price',
            'estimated_duration',
            'notes',
            'status',
            'created_at'
        ]
        read_only_fields = ['service_id', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        audio_file = None

        if request and request.FILES.get('audio_url'):
            audio_file = convert_m4a_to_mp3_django(request.FILES.get('audio_url'))
        existing_service=technician_services.objects.filter(request_id=validated_data['request_id'])
        if existing_service:
            existing_service=technician_services.objects.get(request_id=validated_data['request_id'])
            technician_service_history.objects.create(
                service_id=existing_service.service_id,
                technician_id=existing_service.technician_id,
                request_id=existing_service.request_id,
                custom_price=existing_service.custom_price,
                estimated_duration=existing_service.estimated_duration,
                notes=existing_service.notes,
                audio_url=existing_service.audio_url,
                status=existing_service.status,
                reason=existing_service.reason,
                created_at=existing_service.created_at
            )
            existing_service.delete()
        technician_service = technician_services.objects.create(**validated_data)
        
        if audio_file:
            technician_service.audio_url.save('converted_audio.mp3', audio_file)
            
        request_obj = technician_service.request_id
        request_obj.status = 'In Progress'
        request_obj.save()
        return technician_service

class RequestListSerializer(serializers.ModelSerializer):
    media_urls  = serializers.SerializerMethodField()
    issue_name = serializers.CharField(source='request_id.issue_type.type_name', read_only=True)
    status = serializers.CharField(source='request_id.status', read_only=True)
    issue_description = serializers.CharField(source='request_id.issue_description', read_only=True)
    requested_date = serializers.CharField(source='request_id.requested_date', read_only=True)
    class Meta:
        model = technician_services
        fields = [
            'service_id',
            'technician_id',
            'request_id',
            'reason',
            'custom_price',
            'estimated_duration',
            'issue_description',
            'requested_date',
            'notes',
            'audio_url',
            'media_urls',
            'status',
            'issue_name',
        ]
    def get_media_urls(self, obj):
        gallery = request_gallery.objects.filter(request_id=obj.request_id).first()
        if not gallery:
            return {"gallery_url": None, "audio_url": None}
        request = self.context.get('request')
        build_url = lambda file: request.build_absolute_uri(file.url) if request and file else (file.url if file else None)

        return {
            "gallery_url": build_url(gallery.gallery_url),
            "audio_url": build_url(gallery.audio_url),
        }
        
class TroubleshootingGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = troubleshooting_gallery
        fields = ['gallery_url', 'audio_url']

class TechnicianTroubleShootingCreatingSerializer(serializers.ModelSerializer):
    status = serializers.CharField(write_only=True)
    invoiceStatus = serializers.CharField(write_only=True)

    class Meta:
        model = troubleshooting_history
        fields = [
            'trouble_shoot_id',
            'resolution_text',
            'request_id', 
            'resolved_at',
            'status',
            'invoiceStatus'
        ]
        read_only_fields = ['trouble_shoot_id', 'resolved_at']

    def create(self, validated_data):
        request = self.context.get('request')  # Get request context
        status_value = validated_data.pop('status')
        invoiceStatus = validated_data.pop('invoiceStatus')
        technician_service = validated_data['request_id']
        
        # Create troubleshooting history object
        trouble_obj = troubleshooting_history.objects.create(**validated_data)
        customer_request = technician_service.request_id
        
        customer_request.status = status_value
        customer_request.save()
        tech = technician_services.objects.get(request_id=technician_service.request_id,status="Accepted")
        
        update_invoice = invoices.objects.filter(request_id=tech)
        if update_invoice:
            if invoiceStatus == "REFUND":
                update_invoice = invoices.objects.get(request_id=technician_service)
                invoice_history.objects.create(
                    invoice_id=update_invoice.invoice_id,
                    request_id=update_invoice.request_id,
                    total_amount=update_invoice.total_amount,
                    status=update_invoice.status,
                    invoice_date=update_invoice.invoice_date,
                    user_id=update_invoice.user_id,
                    )
                update_invoice.delete()
            elif invoiceStatus == "UNPAID":
                update_invoice = invoices.objects.get(request_id=technician_service)
                update_invoice.status = invoiceStatus
                update_invoice.save()
                invoice_history.objects.create(
                    invoice_id=update_invoice.invoice_id,
                    request_id=update_invoice.request_id,
                    total_amount=update_invoice.total_amount,
                    status=update_invoice.status,
                    invoice_date=update_invoice.invoice_date,
                    user_id=update_invoice.user_id,
                    )
        else:
            print("No invoice found for this request.")
       

        # Save gallery files
        request_obj = self.context['request']
        gallery_files = request_obj.FILES.getlist('gallery_files')
        audio_file = request_obj.FILES.get('audio_file')

        if audio_file:
            audio_file = convert_m4a_to_mp3_django(audio_file)
        
        for file in gallery_files:
            troubleshooting_gallery.objects.create(
                trouble_id=trouble_obj,
                gallery_url=file,
                audio_url=audio_file
                
            )
        return trouble_obj

class TroubleshootingHistorySerializer(serializers.ModelSerializer):
    gallery_items = TroubleshootingGallerySerializer(many=True, read_only=True)

    class Meta:
        model = troubleshooting_history
        fields = [
            'trouble_shoot_id',
            'resolution_text',
            'resolved_at',
            'gallery_items',  
        ]
    
class TechnicianTroubleShootingSerializer(serializers.ModelSerializer):
    media_urls = serializers.SerializerMethodField()
    issue_name = serializers.CharField(source='request_id.issue_type.type_name', read_only=True)
    issue_description = serializers.CharField(source='request_id.issue_description', read_only=True)
    requested_date = serializers.DateTimeField(source='request_id.requested_date', read_only=True)
    status = serializers.CharField(source='request_id.status', read_only=True)
    customer_id = serializers.CharField(source='request_id.customer_id', read_only=True)
    payment_method = serializers.CharField(source='request_id.payment_method', read_only=True)
    ar_support_enabled = serializers.BooleanField(source='request_id.ar_support_enabled', read_only=True)
    customer_information = serializers.SerializerMethodField()
    troubleshooting_history = TroubleshootingHistorySerializer(
        source='troubleshooting_history_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = technician_services
        fields = [
            'service_id',
            'custom_price',
            'estimated_duration',
            'notes',
            'audio_url',
            'created_at',

            # fields from customer_requests
            'customer_id',
            'issue_description',
            'payment_method',
            'ar_support_enabled',
            'requested_date',
            'status',
            'issue_name',
            'media_urls',

            'troubleshooting_history',
            'customer_information'
        ]

    def get_media_urls(self, obj):
        request = self.context.get('request')
        galleries = request_gallery.objects.filter(request_id=obj.request_id.service_id)

        def build_url(file):
            return request.build_absolute_uri(file.url) if request and file else (file.url if file else None)

        return {
            "gallery_urls": [build_url(g.gallery_url) for g in galleries if g.gallery_url],
            "audio_url": build_url(galleries.first().audio_url) if galleries.exists() else None,
        }
    def get_customer_information(self, obj):
        try:
            request = self.context.get('request')

            # Get the CustomUser who is the customer for this request
            customer_user = obj.request_id.customer_id  

            # Get the customer profile (from customers table)
            customer = customers.objects.get(user_id=customer_user)

            profile_picture = getattr(customer, 'profile_picture_url', None)
            picture_url = (
                request.build_absolute_uri(profile_picture.url)
                if profile_picture and request
                else (profile_picture.url if profile_picture else None)
            )

            return {
                "full_name": customer.name,
                "phone_number": customer.phone,
                "email": customer.email,
                "address": customer.address,
                "picture": picture_url,
                "custom_id": str(customer_user.id)  # Ensure JSON-safe
            }
        except customers.DoesNotExist:
            return None

class TechnicianServiceListSerializer(serializers.ModelSerializer):
    troubleshooting = TroubleshootingHistorySerializer(
        source='troubleshooting_history_set', many=True, read_only=True
    )
    technician_information = serializers.SerializerMethodField()

    class Meta:
        model = technician_services
        fields = [
            'service_id',
            'request_id',
            'technician_id',
            'custom_price',
            'estimated_duration',
            'notes',
            'audio_url',
            'created_at',
            'troubleshooting', 
            'technician_information'
        ]
    def get_technician_information(self, obj):
        try:
            request = self.context.get('request')
            technician = technicians.objects.get(user_id=obj.technician_id)

            profile_picture = technician.profile_picture_url
            picture_url = None

            if profile_picture:
                if request:
                    picture_url = request.build_absolute_uri(profile_picture.url)
                else:
                    picture_url = profile_picture.url

            return {
                "full_name": technician.name,
                "phone_number": technician.phone,
                "email": technician.email,
                "address": technician.address,
                "picture": picture_url,
            }
        except technicians.DoesNotExist:
            return None
    
class TechnicianDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = technicians
        fields = [
            'technician_id',
            'name',
            'email',
            'phone',
            'address',
            'profile_picture_url',
        ]

class TroubleshootingCustomerRequestListSerializer(serializers.ModelSerializer):
    media_urls = serializers.SerializerMethodField()
    issue_name = serializers.CharField(source='request_id.issue_type.type_name', read_only=True)
    issue_description = serializers.CharField(source='request_id.issue_description', read_only=True)
    customer_id = serializers.CharField(source='request_id.customer_id', read_only=True)
    issue_type = serializers.CharField(source='request_id.issue_type_id', read_only=True)
    status = serializers.CharField(source='request_id.status', read_only=True)
    requested_date = serializers.DateTimeField(source='request_id.requested_date', read_only=True)

    technician_details = serializers.SerializerMethodField()
    troubleshooting_history = TroubleshootingHistorySerializer(
        source='troubleshooting_history_set', many=True, read_only=True
    )

    class Meta:
        model = technician_services
        fields = [
            'service_id',
            'technician_id',
            'technician_details',
            'request_id',
            'custom_price',
            'estimated_duration',
            'notes',
            'audio_url',
            'created_at',

            # from customer_requests
            'customer_id',
            'issue_type',
            'issue_name',
            'issue_description',
            'status',
            'requested_date',

            # media
            'media_urls',

            # history
            'troubleshooting_history',
        ]

    def get_media_urls(self, obj):
        galleries = request_gallery.objects.filter(request_id=obj.request_id)
        request = self.context.get('request')

        def build_url(file):
            return request.build_absolute_uri(file.url) if request and file else (file.url if file else None)

        return {
            "gallery_urls": [build_url(g.gallery_url) for g in galleries if g.gallery_url],
            "audio_url": build_url(galleries.first().audio_url) if galleries.exists() else None,
        }

    def get_technician_details(self, obj):
        try:
            tech = technicians.objects.get(user_id=obj.technician_id)
            return TechnicianDetailsSerializer(tech).data
        except technicians.DoesNotExist:
            return None
class CustomerTroubleShootingListSerializer(serializers.ModelSerializer):
    troubleshooting = TroubleshootingHistorySerializer(
        source='troubleshooting_history_set', many=True, read_only=True
    )
    issue_description = serializers.CharField(source='request_id.issue_description', read_only=True)
    requested_date = serializers.DateTimeField(source='request_id.requested_date', read_only=True)
    request_status = serializers.CharField(source='request_id.status', read_only=True)
    issue_name = serializers.CharField(source='request_id.issue_type.type_name', read_only=True)

    technician_id = serializers.UUIDField(source='technician_id.id', read_only=True)

    media_urls = serializers.SerializerMethodField()
    customer_information = serializers.SerializerMethodField()

    class Meta:
        model = technician_services
        fields = [
            'service_id',
            'technician_id',
            'custom_price',
            'estimated_duration',
            'notes',
            'audio_url',
            'created_at',
            'troubleshooting', 
            'issue_name',
            'issue_description',
            'requested_date',
            'request_status',
            'media_urls',
            'customer_information',
        ]
        
    def get_media_urls(self, obj):
        gallery = request_gallery.objects.filter(request_id=obj.request_id)
        request = self.context.get('request')

        build_url = lambda file: request.build_absolute_uri(file.url) if request and file else (file.url if file else None)

        return {
            "gallery_urls": [build_url(g.gallery_url) for g in gallery if g.gallery_url],
            "audio_url": build_url(gallery.first().audio_url) if gallery.exists() else None,
        }

    def get_customer_information(self, obj):
        try:
            request = self.context.get('request')

            # Get the CustomUser who is the customer for this request
            customer_user = obj.request_id.customer_id  

            # Get the customer profile (from customers table)
            customer = customers.objects.get(user_id=customer_user)

            profile_picture = getattr(customer, 'profile_picture_url', None)
            picture_url = (
                request.build_absolute_uri(profile_picture.url)
                if profile_picture and request
                else (profile_picture.url if profile_picture else None)
            )

            return {
                "full_name": customer.name,
                "phone_number": customer.phone,
                "email": customer.email,
                "address": customer.address,
                "picture": picture_url,
                "custom_id": str(customer_user.id)  # Ensure JSON-safe
            }
        except customers.DoesNotExist:
            return None



        
class TroubleShootingUpdatingSerializer(serializers.ModelSerializer): 
    status = serializers.CharField(write_only=True)

    class Meta:
        model = troubleshooting_history
        fields = [
            'trouble_shoot_id',
            'resolution_text',
            'request_id', 
            'resolved_at',
            'status',
        ]
        read_only_fields = ['trouble_shoot_id', 'resolved_at']

    def update(self, instance, validated_data):
        request = self.context.get('request')
        status = validated_data.pop('status', None)

        instance.resolution_text = validated_data.get('resolution_text', instance.resolution_text)
        instance.save()

        if status is not None:
            technician_service = instance.request_id  # already technician_services instance
            customer_request = technician_service.request_id  # likely a CustomerRequest instance
            customer_request.status = status
            customer_request.save()
            update_invoice = invoices.objects.filter(request_id=technician_service)
            if update_invoice:
                update_invoice = invoices.objects.get(request_id=technician_service)
                if update_invoice.status == "PAID":
                    update_invoice.status = "REFUND"
                    update_invoice.save()
                    invoice_history.objects.create(
                    invoice_id=update_invoice.invoice_id,
                    request_id=update_invoice.request_id,
                    total_amount=update_invoice.total_amount,
                    status=update_invoice.status,
                    invoice_date=update_invoice.invoice_date,
                    user_id=update_invoice.user_id,
                    )
                elif update_invoice.status == "UNPAID":
                    invoice_history.objects.create(
                    invoice_id=update_invoice.invoice_id,
                    request_id=update_invoice.request_id,
                    total_amount=update_invoice.total_amount,
                    status=update_invoice.status,
                    invoice_date=update_invoice.invoice_date,
                    user_id=update_invoice.user_id,
                    )
                    update_invoice.delete()
            else:
                print("No invoice found for this request.")

        troubleshooting_gallery.objects.filter(trouble_id=instance).delete()
        gallery_files = request.FILES.getlist('gallery_files')
        audio_file = request.FILES.get('audio_file')

        if audio_file:
            audio_file = convert_m4a_to_mp3_django(audio_file)
        
        for file in gallery_files:
            troubleshooting_gallery.objects.create(
                trouble_id=instance,
                gallery_url=file,
                audio_url=audio_file
                
            )
        return instance

class InvoiceListSerializer(serializers.ModelSerializer):
    media_urls = serializers.SerializerMethodField()
    requested_date = serializers.CharField(source='request_id.request_id.requested_date', read_only=True)
    customer_information = serializers.SerializerMethodField()
    technician_information = serializers.SerializerMethodField()
    estimated_duration= serializers.CharField(source='request_id.estimated_duration', read_only=True)
    notes= serializers.CharField(source='request_id.notes', read_only=True)
    audio_url= serializers.CharField(source='request_id.audio_url', read_only=True)
    status_request= serializers.CharField(source='request_id.status', read_only=True)
    issue_name= serializers.CharField(source='request_id.request_id.issue_type.type_name', read_only=True)
    issue_description= serializers.CharField(source='request_id.request_id.issue_description', read_only=True)
    class Meta:
        model = invoices
        fields = [
            'invoice_id',
            'request_id',
            'total_amount',
            'issue_description',
            'requested_date',
            'issue_name',            
            'estimated_duration',
            'notes',
            'status',
            'status_request',
            'invoice_date',
            'audio_url',
            'media_urls',
            'technician_information',
            'customer_information',
        ]

    def get_media_urls(self, obj):
        gallery = request_gallery.objects.filter(request_id=obj.request_id.request_id)
        if not gallery:
            return {"gallery_url": None, "audio_url": None}
        
        request = self.context.get('request')
        build_url = lambda file: request.build_absolute_uri(file.url) if request and file else (file.url if file else None)

        return {
            "gallery_urls": [build_url(g.gallery_url) for g in gallery if g.gallery_url],
            "audio_url": build_url(gallery.first().audio_url) if gallery.exists() else None,
        }
    def get_customer_information(self, obj):
        try:
            print(obj.request_id)
            customer = customers.objects.get(user_id=obj.request_id.request_id.customer_id)
            request = self.context.get('request')

            def get_picture_url(file):
                if not file:
                    return None
                try:
                    return request.build_absolute_uri(file.url) if request else file.url
                except Exception:
                    return None

            return {
                "full_name": customer.name,
                "phone_number": customer.phone,
                "email": customer.email,
                "address": customer.address,
                "picture": get_picture_url(customer.profile_picture_url),
                "custom_id":str(customer.user_id)
                
            }
        except Exception:
            return None


    def get_technician_information(self, obj):
        try:
            print(obj.request_id)
            customer = technicians.objects.get(user_id=obj.request_id.technician_id)
            request = self.context.get('request')

            def get_picture_url(file):
                if not file:
                    return None
                try:
                    return request.build_absolute_uri(file.url) if request else file.url
                except Exception:
                    return None

            return {
                "full_name": customer.name,
                "phone_number": customer.phone,
                "email": customer.email,
                "address": customer.address,
                "picture": get_picture_url(customer.profile_picture_url),
            }
        except Exception:
            return None

class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = payment_transactions
        fields = [
            'payment_id',
            'invoice_id',
            'amount_paid',
            'number_details',
            'payment_method',
            'transaction_date',
            ]

    def create(self, validated_data):
        payment = super().create(validated_data)

        # Update invoice status to PAID
        invoice = payment.invoice_id
        if invoice.status == "UNPAID":
            invoice.status = 'WAITINGVARIFICATION'
        elif invoice.status == "REFUND":
            invoice.status = 'REFUNDED'
            
        invoice.save()

        return payment


class InvoiceStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = invoices
        fields = ['status']
        read_only_fields = []

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        invoice_history.objects.create(
                    invoice_id=instance.invoice_id,
                    request_id=instance.request_id,
                    total_amount=instance.total_amount,
                    status=instance.status,
                    invoice_date=instance.invoice_date,
                    user_id=instance.user_id,
                    )
        return instance

class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = calenders
        fields = '__all__'