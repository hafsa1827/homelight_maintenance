from django.contrib import admin
from django.urls import path,include
from .views import GetReview,LogoutView,SaveReview,UserRegistrationView,LoginView,RoleListView,UpdateProfileView,user_profile,UserProfileView,GetTechnicianByUserView

urlpatterns = [
    path('', UserRegistrationView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('reviews', GetReview.as_view(), name='reviews'),
    path('review', SaveReview.as_view(), name='review'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('roles', RoleListView.as_view(), name='roles'),
    path('update_profile', UpdateProfileView.as_view(), name='update_profile'),
     path('profile/<str:user_id>', user_profile),
    path('user_view/<str:user_id>/<str:role>/', UserProfileView.as_view(), name='user_view'),
    path('technician/<str:user_id>/', GetTechnicianByUserView.as_view(), name='technician'),
     
]