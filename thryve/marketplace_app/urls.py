from django.urls import path, include
from marketplace_app import views
urlpatterns = [
    path('', views.marketplace, name='marketplace'),
]