from django.urls import path, include
from auth_app import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    # Temporary path for home after login
    path('home/', views.home1, name='home1'),
    
        # marketplace should be the home of the app
    path("", views.marketplace, name="marketplace"),

    # keep a distinct landing URL if you still need it
    path("landing/", views.landing, name="landing"),
]