from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.marketplace_home, name='home'),
    path('my-listings/', views.my_listings, name='my_listings'),
    path('create/', views.create_listing, name='create_listing'),
    path('edit/<int:listing_id>/', views.edit_listing, name='edit_listing'),
    path('delete/<int:listing_id>/', views.delete_listing, name='delete_listing'),
]