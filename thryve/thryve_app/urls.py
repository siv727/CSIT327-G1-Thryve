from django.urls import path
from . import views

app_name = 'thryve_app'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create-listing/', views.create_listing, name='create_listing'),
    path('my-listings/', views.my_listings, name='my_listings'),
    path('edit-listing/<int:listing_id>/', views.edit_listing, name='edit_listing'),
    path('delete-listing/<int:listing_id>/', views.delete_listing, name='delete_listing'),
    path('connections/', views.connections, name='connections'),
    path('browse-businesses/', views.browse_businesses, name='browse_businesses'),
    path('send-connection-request/', views.send_connection_request, name='send_connection_request'),
    path('accept-connection-request/', views.accept_connection_request, name='accept_connection_request'),
    path('decline-connection-request/', views.decline_connection_request, name='decline_connection_request'),
    path('cancel-connection-request/', views.cancel_connection_request, name='cancel_connection_request'),
]