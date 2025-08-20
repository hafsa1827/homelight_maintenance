from django.urls import path,include
from .views import GalleryListByUserId,GalleryListView,TechnicianSpecializationViewwithUserId,UpdateGalleryView,GalleryIssueListView,SaveSpecializationView,TechnicianSpecializationView,TechnicianSpecializationViewwithIssueId

urlpatterns = [
    
    path('gallery', GalleryListView.as_view(), name='gallery'),
    path('gallery_byissue', GalleryListByUserId.as_view(), name='gallery_byissue'),
    path('gallerywithissue', GalleryIssueListView.as_view(), name='gallerywithissue'),
    path('save_gallery', UpdateGalleryView.as_view(), name='save_gallery'),
    path('save_specialization', SaveSpecializationView.as_view(), name='save_specialization'),
    path('specializations/<str:user_id>/', TechnicianSpecializationView.as_view(), name='specializations'),
    path('specializations_user/<str:user_id>/', TechnicianSpecializationViewwithUserId.as_view(), name='specializations_user'),
    path('specialize_issue/<uuid:issue_id>/', TechnicianSpecializationViewwithIssueId.as_view(), name='specialize_issue'),

]