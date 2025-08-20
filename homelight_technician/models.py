import uuid
from django.db import models

# Create your models here.
from homelight_users.models import technicians, customers, roles, CustomUser
from homelight_appointment.models import customer_requests,issue_type
from django.core.validators import MinValueValidator, MaxValueValidator

class technician_service_area(models.Model):
    area_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    technician_id=models.ForeignKey(technicians,on_delete=models.CASCADE)
    region=models.CharField(max_length=30)
    city=models.CharField(max_length=30)
    postal_code=models.CharField(max_length=30)
    country=models.CharField(max_length=30)
    class Meta:
        db_table='technician_service_area'
        

class service_gallery(models.Model):
    gallery_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    role=models.ForeignKey(roles,on_delete=models.CASCADE)
    gallery_url=models.ImageField(upload_to='gallery/', null=True, blank=True)
    issue_id=models.ForeignKey(issue_type,on_delete=models.CASCADE,related_name='galleries')
    
    class Meta:
        db_table='service_gallery'     
        
class technician_specialization(models.Model):
    specialization_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user =models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    issue=models.ForeignKey(issue_type,on_delete=models.CASCADE)
    tools_owned=models.TextField()
    specialization_details=models.TextField()
    years_of_experience=models.IntegerField()
    base_price=models.IntegerField()
    class Meta:
        db_table='technician_specialization'  

class DayOfWeek(models.TextChoices):
    MONDAY = 'mon', 'Monday'
    TUESDAY = 'tue', 'Tuesday'
    WEDNESDAY = 'wed', 'Wednesday'
    THURSDAY = 'thu', 'Thursday'
    FRIDAY = 'fri', 'Friday'
    SATURDAY = 'sat', 'Saturday'
    SUNDAY = 'sun', 'Sunday'
    
class technician_availability(models.Model):
    availability_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    technician_id=models.ForeignKey(technicians,on_delete=models.CASCADE)
    day_of_week=models.CharField(max_length=3,choices=DayOfWeek.choices,default=DayOfWeek.MONDAY)
    start_time=models.TimeField()
    end_time=models.TimeField()
    is_available=models.BooleanField(default=True)
    class Meta:
        db_table='technician_availability'     

class technician_workload(models.Model):
    workload_id=models.UUIDField(primary_key=True)
    technician_id=models.ForeignKey(technicians,on_delete=models.CASCADE)
    total_jobs=models.IntegerField()
    total_hours_worked=models.DecimalField(max_digits=5,decimal_places=2,default=0)
    last_updated=models.TimeField()
    class Meta:
        db_table='technician_workload'  
        
class technician_complaints(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Resolved', 'Resolved'),
        ('Dismissed', 'Dismissed'),
    ]
    complaint_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    technician_id=models.ForeignKey(technicians,on_delete=models.CASCADE)
    customer_id=models.ForeignKey(customers,on_delete=models.CASCADE)
    complaint_text=models.TextField()
    status=models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    reported_at=models.TimeField()
    class Meta:
        db_table='technician_complaints'
        
class technician_feedback(models.Model):
    feedback_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    technician_id=models.ForeignKey(technicians,on_delete=models.CASCADE)
    customer_id=models.ForeignKey(customers,on_delete=models.CASCADE)
    rating=models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    feedback_text=models.TextField()
    created_at=models.TimeField()
    class Meta:
        db_table='technician_feedback'  
        
class request_history(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Resolved', 'Resolved'),
        ('Dismissed', 'Dismissed'),
        ('In Progress', 'In Progress'),
    ]
    history_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_id=models.ForeignKey(customer_requests,on_delete=models.CASCADE)
    job_status=models.CharField(max_length=15,choices=STATUS_CHOICES,default='Pending')
    start_time=models.TimeField()
    end_time=models.TimeField()
    customer_feedback=models.CharField(max_length=300)
    rating=models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at=models.TimeField(auto_created=True)
    
    class Meta:
        db_table='request_history'    
        
class technician_performance(models.Model):
    performance_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    technician_id=models.ForeignKey(technicians,on_delete=models.CASCADE)
    rating_avg=models.FloatField()
    total_appointments=models.IntegerField()
    class Meta:
        db_table='technician_performance'
        
