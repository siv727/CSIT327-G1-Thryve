from django.urls import path
from . import views

urlpatterns = [
    path('profile/business/', views.business_profile_view, name='business_profile'),
    # For what ang new alias? - Ervin
    path('home/', views.business_profile_view, name='profile_home'),  # new alias
    path('customization/', views.profile_customization_view, name='profile_customization'),
    path('logo/', views.business_logo, name='business_logo'),
]