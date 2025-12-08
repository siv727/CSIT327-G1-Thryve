from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from thryve_app.models import Listing
from .models import BookingRequest

@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def bookings(request):
    return render(request, 'bookings.html')

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
            'message': f"Transaction proposal sent successfully to {receiver.company} for {listing.title}.",
            'listing_type': listing.listing_type # Useful for frontend confirmation
        })

    except Listing.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Listing not found.'}, status=404)
    except Exception as e:
        # Catch validation errors (e.g., bad date format) or other database errors
        return JsonResponse({'success': False, 'message': f'An internal error occurred: {str(e)}'}, status=500)