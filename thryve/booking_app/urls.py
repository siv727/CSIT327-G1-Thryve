from django.urls import path
from . import views

urlpatterns = [
    path('', views.bookings, name='bookings'),
    # New API endpoint for submitting the request
    path('request/', views.create_booking_request, name='create_booking_request_api'),
    # API endpoints for booking actions
    path('cancel/<int:booking_id>/', views.cancel_booking_request, name='cancel_booking_request'),
    path('decline/<int:booking_id>/', views.decline_booking_request, name='decline_booking_request'),
    path('schedule/<int:booking_id>/', views.schedule_booking_request, name='schedule_booking_request'),
    path('complete/<int:booking_id>/', views.complete_booking_request, name='complete_booking_request'),
]