from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import models
from thryve_app.models import Listing
from .models import BookingRequest

@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def bookings(request):
    # Get search query
    search_query = request.GET.get('q', '').strip()

    # Get booking requests sent by the user
    sent_requests = BookingRequest.objects.filter(sender=request.user).select_related('listing', 'receiver').order_by('-created_at')

    # Get booking requests received by the user
    received_requests = BookingRequest.objects.filter(receiver=request.user).select_related('listing', 'sender').order_by('-created_at')

    # Apply search filtering if query exists
    if search_query:
        # Filter sent requests by multiple fields
        sent_requests = sent_requests.filter(
            models.Q(listing__title__icontains=search_query) |
            models.Q(receiver__company_name__icontains=search_query) |
            models.Q(status__icontains=search_query) |
            models.Q(listing__listing_type__icontains=search_query) |
            models.Q(listing__category__icontains=search_query) |
            models.Q(proposed_start_date__icontains=search_query) |
            models.Q(proposed_end_date__icontains=search_query) |
            models.Q(created_at__date__icontains=search_query)
        )

        # Filter received requests by multiple fields
        received_requests = received_requests.filter(
            models.Q(listing__title__icontains=search_query) |
            models.Q(sender__company_name__icontains=search_query) |
            models.Q(status__icontains=search_query) |
            models.Q(listing__listing_type__icontains=search_query) |
            models.Q(listing__category__icontains=search_query) |
            models.Q(proposed_start_date__icontains=search_query) |
            models.Q(proposed_end_date__icontains=search_query) |
            models.Q(created_at__date__icontains=search_query)
        )

    context = {
        'sent_requests': sent_requests,
        'received_requests': received_requests,
        'sent_count': sent_requests.count(),
        'received_count': received_requests.count(),
        'search_query': search_query,
    }

    return render(request, 'bookings.html', context)

@login_required(login_url='login')
@require_POST
def create_booking_request(request):
    """Handles POST requests from the 'Book Now' modal via AJAX."""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)

    # 1. Extract and Validate Required Data
    listing_id = request.POST.get('listing_id')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    message = request.POST.get('message', '').strip()

    try:
        # Fetch Listing and identify the Receiver (Listing owner)
        listing = Listing.objects.get(id=listing_id)
        receiver = listing.user
        sender = request.user

        # Check if user is booking their own listing
        if sender == receiver:
            return JsonResponse({'success': False, 'message': 'You cannot request a booking on your own listing.'}, status=403)

        # Check for existing pending request
        if BookingRequest.objects.filter(listing=listing, sender=sender, status='pending').exists():
             return JsonResponse({'success': False, 'message': 'You already have a pending transaction proposal for this item.'}, status=409)

        # 2. Create the Booking Request
        BookingRequest.objects.create(
            listing=listing,
            sender=sender,
            receiver=receiver,
            proposed_start_date=start_date, # Django handles date string conversion
            proposed_end_date=end_date,
            message=message
        )

        # NOTE: Notification logic (e.g., email to receiver) should be implemented here later.

        return JsonResponse({
            'success': True,
            'message': f"Transaction proposal sent successfully to {receiver.company_name} for {listing.title}.",
            'listing_type': listing.listing_type # Useful for frontend confirmation
        })

    except Listing.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Listing not found.'}, status=404)
    except Exception as e:
        # Catch validation errors (e.g., bad date format) or other database errors
        return JsonResponse({'success': False, 'message': f'An internal error occurred: {str(e)}'}, status=500)

@login_required(login_url='login')
@require_POST
def cancel_booking_request(request, booking_id):
    """Handles POST requests to cancel a booking request."""
    try:
        booking = BookingRequest.objects.get(id=booking_id, sender=request.user)

        # Only allow cancelling pending requests
        if booking.status != 'pending':
            return JsonResponse({'success': False, 'message': 'Only pending booking requests can be cancelled.'}, status=400)

        booking.status = 'cancelled'
        booking.save()

        return JsonResponse({
            'success': True,
            'message': 'Booking request cancelled successfully.',
            'new_status': 'cancelled',
            'status_display': booking.get_status_display()
        })

    except BookingRequest.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Booking request not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'An internal error occurred: {str(e)}'}, status=500)