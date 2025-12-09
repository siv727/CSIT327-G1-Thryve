# community_app/urls.py

from django.urls import path
from . import views

# IMPORTANT: This sets the namespace for URL lookups (e.g., community_app:community_feed)
app_name = 'community_app' 

urlpatterns = [
    # Maps /community/ to the community_feed view function
    path('', views.community_feed, name='community_feed'),
    
    # Other paths like /community/create/
    path('create/', views.create_community_post, name='create_community_post'),
    path('<int:post_id>/like/', views.toggle_post_like, name='toggle_post_like'),
    
    # --- NEW URL: Add Comment ---
    path('<int:post_id>/comment/', views.add_comment, name='add_comment'),
    # -----------------------------
]