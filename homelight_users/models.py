from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, email, phone_number, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, phone_number, password, **extra_fields)



class roles(models.Model):
    role_id=models.UUIDField(primary_key=True)
    STATUS_CHOICES = [
        ('Admin', 'Admin'),
        ('Technician', 'Technician'),
        ('Customer', 'Customer'),
    ]
    name= models.CharField(max_length=10, choices=STATUS_CHOICES, default='Technician')

    class Meta:
        db_table = 'roles'
class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True, db_index=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    role=models.ForeignKey(roles, on_delete=models.SET_NULL,null=True, blank=True,to_field='role_id')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class RolePermission(models.Model):
    role = models.ForeignKey(roles, on_delete=models.CASCADE)
    permission = models.ForeignKey('auth.Permission', on_delete=models.CASCADE)
    class Meta:
        db_table = 'role_permission'

class technicians(models.Model):
    technician_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id=models.ForeignKey('CustomUser',on_delete=models.CASCADE)
    profile_picture_url = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    name=models.CharField(max_length=30)
    email=models.CharField(max_length=30)
    phone=models.CharField(max_length=15)
    address=models.CharField(max_length=100)
    # review_rate=models.CharField(max_length=100)
    # review_rate=models.FloatField(default=0.0)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'technicians'
        
class reviews(models.Model):
    review_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id=models.ForeignKey('CustomUser',on_delete=models.CASCADE)
    reviewed_by = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='reviews_made')
    review_text=models.CharField(max_length=30)
    rate=models.IntegerField(default=0.0)
    created_at= models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'reviews'
    
class customers(models.Model):
    customer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id=models.ForeignKey('CustomUser',on_delete=models.CASCADE)
    profile_picture_url = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    name=models.CharField(max_length=30)
    email=models.CharField(max_length=30)
    phone=models.CharField(max_length=15)
    address=models.TextField()
    # subscription_plan=models.CharField(max_length=100)
    # total_bookings=models.IntegerField(default=0)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at=  models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'customers'
        
class password_resets(models.Model):
    reset_id=models.UUIDField(primary_key=True)
    user_id=models.ForeignKey('CustomUser',on_delete=models.CASCADE)
    reset_token=models.CharField(max_length=200)
    expires_at=models.TimeField()
    used=models.BooleanField()
    
    class Meta:
        db_table = 'password_resets'

class notifications(models.Model):
    notification_id=models.UUIDField(primary_key=True)
    recipient_id=models.ForeignKey('CustomUser',on_delete=models.CASCADE)
    message=models.CharField(max_length=200)
    STATUS_CHOICES = [
        ('Read', 'Read'),
        ('UnRead', 'UnRead'),]
    status=models.CharField(max_length=10, choices=STATUS_CHOICES, default='UnRead')
    created_at=models.TimeField(auto_now_add=True)
    class Meta:
        db_table = 'notifications'

class user_activity_logs(models.Model):
    log_id=models.UUIDField(primary_key=True)
    user_id=models.ForeignKey('CustomUser',on_delete=models.CASCADE)
    action=models.TextField()
    timestamp=models.TimeField(auto_now_add=True)
    class Meta:
        db_table = 'user_activity_logs'
