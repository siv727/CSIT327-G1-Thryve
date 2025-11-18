from django.urls import path
from . import views

urlpatterns = [
    path('', views.bookings, name='bookings'),
]
