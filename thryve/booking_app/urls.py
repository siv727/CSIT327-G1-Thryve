from django.urls import path
from . import views

urlpatterns = [
    path('', views.bookings, name='bookings'),
    # New API endpoint for submitting the request
    path('request/', views.create_booking_request, name='create_booking_request_api'),
    # API endpoint for cancelling booking requests
    path('cancel/<int:booking_id>/', views.cancel_booking_request, name='cancel_booking_request'),
]