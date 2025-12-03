from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q

from thryve_app.models import Listing
from .models import Connection, ConnectionRequest


@login_required(login_url='login')
def dashboard(request):
    # Get user's recent bookings (placeholder data)
    recent_bookings = [
        {
            'item': 'Mousepad',
            'date': '10/20/2025 – 10/29/2025',
            'status': 'pending'
        }
    ]

    # Get user's active listings (real data)
    user_active_listings = Listing.objects.filter(user=request.user, is_available=True)
    active_listings = []
    for listing in user_active_listings:
        active_listings.append({
            'title': listing.title,
            'type': dict(Listing.LISTING_TYPE_CHOICES).get(listing.listing_type, listing.listing_type).title(),
            'other': listing.category_display,
            'status': 'available' if listing.is_available else 'unavailable',
        })

    # Get recent marketplace updates (placeholder data)
    marketplace_updates = [
        {
            'item': 'Tractor',
            'detail': 'Sale - $600'
        }
    ]

    # Activity summary counts (placeholder data)
    activity_summary = {
        'total_bookings': 1,
        'active_listings': user_active_listings.count(),
        'pending_booking_requests': 1,
        'connection_requests': 0
    }

    context = {
        'recent_bookings': recent_bookings,
        'active_listings': active_listings,
        'marketplace_updates': marketplace_updates,
        'activity_summary': activity_summary,
    }

    return render(request, 'thryve_app/dashboard.html', context)

@login_required(login_url='login')
def connections(request):
    # Get user's connections
    user_connections = Connection.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).select_related('user1', 'user2')

    # Get connection requests
    incoming_requests = ConnectionRequest.objects.filter(
        receiver=request.user,
        status='pending'
    ).select_related('sender')

    sent_requests = ConnectionRequest.objects.filter(
        sender=request.user,
        status='pending'
    ).select_related('receiver')

    # Count for tabs
    connections_count = user_connections.count()
    incoming_count = incoming_requests.count()
    sent_count = sent_requests.count()

    context = {
        'connections': user_connections,
        'incoming_requests': incoming_requests,
        'sent_requests': sent_requests,
        'connections_count': connections_count,
        'incoming_count': incoming_count,
        'sent_count': sent_count,
    }

    return render(request, 'thryve_app/connections.html', context)

@login_required(login_url='login')
def browse_businesses(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()

    # Get search query
    search_query = request.GET.get('q', '').strip()

    # Get all users except current user
    businesses = User.objects.exclude(id=request.user.id)

    # Get connected users
    connected_user_ids = set()
    for conn in Connection.objects.filter(Q(user1=request.user) | Q(user2=request.user)):
        if conn.user1 == request.user:
            connected_user_ids.add(conn.user2.id)
        else:
            connected_user_ids.add(conn.user1.id)

    # Get users with pending requests (sent or received)
    pending_user_ids = set()
    for req in ConnectionRequest.objects.filter(
        (Q(sender=request.user) | Q(receiver=request.user)) & Q(status='pending')
    ):
        if req.sender == request.user:
            pending_user_ids.add(req.receiver.id)
        else:
            pending_user_ids.add(req.sender.id)

    # Exclude connected and pending users
    exclude_ids = connected_user_ids.union(pending_user_ids)
    businesses = businesses.exclude(id__in=exclude_ids)

    # Apply search filter
    if search_query:
        businesses = businesses.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(company_name__icontains=search_query)
        )

    context = {
        'businesses': businesses,
        'search_query': search_query,
    }

    return render(request, 'thryve_app/browse_businesses.html', context)

@login_required(login_url='login')
def send_connection_request(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        receiver_id = request.POST.get('receiver_id')
        message = request.POST.get('message', '').strip()
        try:
            receiver = User.objects.get(id=receiver_id)
            # Check if already connected
            existing_connection = Connection.objects.filter(
                (Q(user1=request.user) & Q(user2=receiver)) |
                (Q(user1=receiver) & Q(user2=request.user))
            ).exists()
            if existing_connection:
                return JsonResponse({'success': False, 'message': 'Already connected.'})
            # Delete any existing request between these users to allow resending
            ConnectionRequest.objects.filter(
                (Q(sender=request.user) & Q(receiver=receiver)) |
                (Q(sender=receiver) & Q(receiver=request.user))
            ).delete()
            # Create request with optional message
            ConnectionRequest.objects.create(
                sender=request.user,
                receiver=receiver,
                message=message if message else None
            )
            return JsonResponse({'success': True, 'message': f'Connection request sent successfully to {receiver.get_full_name()}.', 'receiver_name': receiver.get_full_name()})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})

@login_required(login_url='login')
def accept_connection_request(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        request_id = request.POST.get('request_id')
        try:
            connection_request = ConnectionRequest.objects.get(
                id=request_id,
                receiver=request.user,
                status='pending'
            )
            # Create connection
            Connection.objects.create(
                user1=connection_request.sender,
                user2=connection_request.receiver
            )
            # Update request status
            connection_request.status = 'accepted'
            connection_request.save()

            return JsonResponse({
                'success': True,
                'message': f'Connection request from {connection_request.sender.get_full_name()} accepted.',
                'sender_name': connection_request.sender.get_full_name()
            })
        except ConnectionRequest.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Connection request not found.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})

@login_required(login_url='login')
def decline_connection_request(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        request_id = request.POST.get('request_id')
        try:
            connection_request = ConnectionRequest.objects.get(
                id=request_id,
                receiver=request.user,
                status='pending'
            )
            sender_name = connection_request.sender.get_full_name()
            # Delete the request entirely to allow future requests
            connection_request.delete()

            return JsonResponse({
                'success': True,
                'message': f'Connection request from {sender_name} declined.',
                'sender_name': sender_name
            })
        except ConnectionRequest.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Connection request not found.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})

@login_required(login_url='login')
def cancel_connection_request(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        request_id = request.POST.get('request_id')
        try:
            connection_request = ConnectionRequest.objects.get(
                id=request_id,
                sender=request.user,
                status='pending'
            )
            receiver_name = connection_request.receiver.get_full_name()
            # Delete the request entirely
            connection_request.delete()

            return JsonResponse({
                'success': True,
                'message': f'Connection request to {receiver_name} cancelled.',
                'receiver_name': receiver_name
            })
        except ConnectionRequest.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Connection request not found.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})

@login_required(login_url='login')
def remove_connection(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        connection_id = request.POST.get('connection_id')
        try:
            connection = Connection.objects.get(
                Q(id=connection_id) & (Q(user1=request.user) | Q(user2=request.user))
            )
            # Get the other user's name
            other_user = connection.user2 if connection.user1 == request.user else connection.user1
            other_user_name = other_user.get_full_name()
            # Delete the connection
            connection.delete()
            # Also delete any connection requests between these users
            ConnectionRequest.objects.filter(
                (Q(sender=request.user) & Q(receiver=other_user)) |
                (Q(sender=other_user) & Q(receiver=request.user))
            ).delete()

            return JsonResponse({
                'success': True,
                'message': f'Connection with {other_user_name} removed successfully.',
                'other_user_name': other_user_name
            })
        except Connection.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Connection not found.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})
