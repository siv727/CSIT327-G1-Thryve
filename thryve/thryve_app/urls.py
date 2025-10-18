from django.urls import path
from . import views

app_name = 'thryve_app'

urlpatterns = [
    path('create-listing/', views.create_listing, name='create_listing'),
]