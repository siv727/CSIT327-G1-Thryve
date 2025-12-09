# community_app/urls.py

from django.urls import path
from . import views

# IMPORTANT: This sets the namespace for URL lookups (e.g., community_app:community_feed)
app_name = 'community_app' 

urlpatterns = [
    # General Feed
    path('', views.community_feed, name='community_feed'),
    
    # Post Actions
    path('create/', views.create_community_post, name='create_community_post'),
    path('<int:post_id>/like/', views.toggle_post_like, name='toggle_post_like'),
    path('<int:post_id>/delete/', views.delete_community_post, name='delete_community_post'),

    # Comment Actions
    path('<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('<int:post_id>/comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
]