from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.marketplace_home, name='home'),
    path('create/', views.create_listing, name='create_listing'),
]