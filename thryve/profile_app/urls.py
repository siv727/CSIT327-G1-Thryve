from django.urls import path
from . import views

urlpatterns = [
    path('profile/business/', views.business_profile_view, name='business_profile'),
    path('home/', views.business_profile_view, name='profile_home'),  # new alias
    path('customization/', views.profile_customization_view, name='profile_customization'),
]