from datetime import timedelta
import uuid
from django.db import models
from homelight_users.models import technicians, customers, CustomUser
from django.utils.timezone import now

class calenders(models.Model):
    calender_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date= models.DateTimeField(auto_now_add=True)
    activity= models.CharField(max_length=100)
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    class Meta:
        db_table='calenders'
        
class issue_type(models.Model):
    type_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type_name=models.CharField(max_length=30)
    issue_icon=models.CharField(max_length=30)
    class Meta:
        db_table='issue_type'
        
        
class technician_services(models.Model):
    STATUS_CHOICES = [
        ('Rejected', 'Rejected'),
        ('Accepted', 'Accepted'),
        ('Select', 'Select'),
    ]
    service_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    technician_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    request_id = models.ForeignKey('customer_requests', on_delete=models.CASCADE, related_name='technician_services_set')
    custom_price=models.DecimalField(max_digits=5,decimal_places=2,default=0)
    estimated_duration = models.DurationField(default=timedelta(minutes=30))
    notes=models.CharField(max_length=500)
    audio_url=models.FileField(upload_to='audio_services/', null=True, blank=True)
    status=models.CharField(max_length=20, choices=STATUS_CHOICES, default='Select')
    reason=models.CharField(max_length=100, blank=True,null=True)
    
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table='technician_services'
        
class customer_requests(models.Model):
    STATUS_CHOICES = [
        ('EVCPLUS', 'EVCPLUS'),
        ('MARCHENT', 'MARCHENT'),
        ('CREDITCARD', 'CREDITCARD'),
    ]
    STATUS_CHOICES_2 = [
        ('Pending', 'Pending'),
        ('Resolved', 'Resolved'),
        ('Dismissed', 'Dismissed'),
        ('In Progress', 'In Progress'),
    ]
    service_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    issue_type=models.ForeignKey('issue_type',on_delete=models.CASCADE)
    issue_description=models.CharField(max_length=500)
    payment_method=models.CharField(max_length=20, choices=STATUS_CHOICES, default='EVCPLUS')
    ar_support_enabled=models.BooleanField(default=False)
    requested_date=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=20, choices=STATUS_CHOICES_2 , default='Pending')
    class Meta:
        db_table='customer_requests'

class request_gallery(models.Model):
    gallery_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gallery_url= models.FileField(upload_to='gallery/', null=True, blank=True)
    audio_url=models.FileField(upload_to='audio_descriptions/', null=True, blank=True)
    request_id=models.ForeignKey('customer_requests',on_delete=models.CASCADE)
    class Meta:
        db_table='request_gallery'
        
        
class troubleshooting_history(models.Model):
    trouble_shoot_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_id = models.ForeignKey('technician_services', on_delete=models.CASCADE, related_name='troubleshooting_history_set')
    resolution_text=models.TextField()
    resolved_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table='troubleshooting_history'
        
class troubleshooting_gallery(models.Model):
    gallery_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gallery_url= models.FileField(upload_to='trouble_gallery/', null=True, blank=True)
    audio_url=models.FileField(upload_to='trouble_audio/', null=True, blank=True)
    trouble_id=models.ForeignKey('troubleshooting_history',on_delete=models.CASCADE, related_name='gallery_items' )
    class Meta:
        db_table='troubleshooting_gallery'
        
class technician_service_history(models.Model):
    STATUS_CHOICES = [
        ('Rejected', 'Rejected'),
        ('Accepted', 'Accepted'),
        ('Select', 'Select'),
    ]
    service_id=models.UUIDField()
    technician_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    request_id = models.ForeignKey('customer_requests', on_delete=models.CASCADE)
    custom_price=models.DecimalField(max_digits=5,decimal_places=2,default=0)
    estimated_duration = models.DurationField(default=timedelta(minutes=30))
    notes=models.CharField(max_length=500)
    audio_url=models.FileField(upload_to='audio_services/', null=True, blank=True)
    status=models.CharField(max_length=20, choices=STATUS_CHOICES, default='Select')
    reason=models.CharField(max_length=100, blank=True,null=True)
    
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table='technician_service_history'
        
class payment_transactions(models.Model):
    STATUS_CHOICES = [
        ('EVCPLUS', 'EVCPLUS'),
        ('MARCHENT', 'MARCHENT'),
        ('CREDITCARD', 'CREDITCARD'),
    ]
    payment_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_id=models.ForeignKey('invoices',on_delete=models.CASCADE)
    amount_paid=models.DecimalField(max_digits=5,decimal_places=2,default=0)
    number_details=models.CharField(max_length=100, blank=True,null=True)
    payment_method=models.CharField(max_length=20, choices=STATUS_CHOICES, default='EVCPLUS')
    transaction_date=models.DateTimeField(default=now)
    class Meta:
        db_table='payment_transactions'

class invoices(models.Model):
    STATUS_CHOICES_2 = [
        ('UNPAID', 'UNPAID'),
        ('PAID', 'PAID'),
        ('OVERDUE', 'OVERDUE'),
        ('REFUND', 'REFUND'),
        ('WAITINGVARIFICATION', 'WAITINGVARIFICATION'),
    ]
    invoice_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_id=models.ForeignKey('technician_services',on_delete=models.CASCADE)
    total_amount=models.DecimalField(max_digits=5,decimal_places=2,default=0)
    status=models.CharField(max_length=20, choices=STATUS_CHOICES_2 , default='OVERDUE')    
    invoice_date = models.DateTimeField(default=now)
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE)


    class Meta:
        db_table='invoices'
        
class invoice_history(models.Model):
    STATUS_CHOICES_2 = [
        ('UNPAID', 'UNPAID'),
        ('PAID', 'PAID'),
        ('OVERDUE', 'OVERDUE'),
        ('REFUND', 'REFUND'),
        ('REFUNDED', 'REFUNDED'),
        ('WAITINGVARIFICATION', 'WAITINGVARIFICATION'),
    ]
    invoice_id=models.UUIDField()
    request_id=models.ForeignKey('technician_services',on_delete=models.CASCADE)
    total_amount=models.DecimalField(max_digits=5,decimal_places=2,default=0)
    status=models.CharField(max_length=20, choices=STATUS_CHOICES_2 , default='OVERDUE')    
    invoice_date = models.DateTimeField(default=now)
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    class Meta:
        db_table='invoice_history'
        
class customer_service_bookmarks(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Deleted', 'Deleted'),
    ]
    bookmark_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service_id=models.ForeignKey('technician_services',on_delete=models.CASCADE)
    status=models.CharField(max_length=20, choices=STATUS_CHOICES , default='UNPAID')    
    created_at=models.TimeField(auto_created=True)
    updated_at=models.TimeField(auto_created=True)
    class Meta:
        db_table='customer_service_bookmarks'