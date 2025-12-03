from django.urls import path, include
from auth_app import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),

    # keep a distinct landing URL if you still need it
    # path("landing/", views.landing, name="landing"),
]