from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from .forms import ListingForm, validate_images_count, validate_image_file
from .models import ListingImage, Listing
from django.db.models import Q
from .forms import ListingForm
from .models import ListingImage, Listing, Connection, ConnectionRequest

LISTING_TYPES = [
    {'value': 'sale', 'label': 'For Sale'},
    {'value': 'swap', 'label': 'For Swap'},
    {'value': 'buy', 'label': 'Looking to Buy'},
]

@login_required(login_url='login')
def my_listings(request):
    # Get listings created by the current user
    user_listings = Listing.objects.filter(user=request.user).prefetch_related('images').order_by('-created_at')

    # Process listings data for easier template usage
    processed_listings = []
    for listing in user_listings:
        listing_data = {
            'obj': listing,  # Original listing object
            'id': listing.id,
            'title': listing.title,
            'description': listing.description,
            'location': listing.location,
            'your_name': listing.your_name,
            'company': listing.company,
            'listing_type': listing.listing_type,
            'category': listing.category,
            'subcategory': listing.subcategory,
            'category_display': listing.category_display,
            'subcategory_display': listing.subcategory_display,
            'formatted_price': listing.formatted_price,
            'formatted_budget': listing.formatted_budget,
            'formatted_date': listing.formatted_date,
            'price': listing.price,
            'budget': listing.budget,
            'swap_for': listing.swap_for,
            'date': listing.date,
            'main_image': listing.main_image,
            'images': listing.images.all(),
            'image_count': listing.image_count,
            'can_add_images': listing.can_add_images,
        }
        processed_listings.append(listing_data)

    return render(request, 'marketplace.html', {
        'listings': user_listings,  # Keep original for backward compatibility
        'processed_listings': processed_listings,
        'is_my_listings': True,
        'categories': Listing.get_categories_dict(),
        'listing_types': LISTING_TYPES,
    })

@login_required(login_url='login')
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)

        # Validate category field manually since it's not in the form
        category_value = request.POST.get('category', '').strip()
        if not category_value:
            form.add_error(None, 'Category is required.')

        if form.is_valid() and category_value:
            listing = form.save(commit=False)
            listing.user = request.user
            try:
                listing.your_name = request.user.profile.display_name or f"{request.user.first_name} {request.user.last_name}"
            except:
                listing.your_name = f"{request.user.first_name} {request.user.last_name}"
            listing.company = request.user.company_name

            # Parse category and subcategory from the POST data
            if '-' in category_value:
                main_category, subcategory = category_value.split('-', 1)
                listing.category = main_category
                listing.subcategory = subcategory
            else:
                listing.category = category_value
                listing.subcategory = None

            listing.save()

            # Handle multiple image uploads with validation
            images = request.FILES.getlist('images')
            if images:
                try:
                    # Validate image count
                    validate_images_count(images)

                    # Validate each image file
                    for image in images:
                        validate_image_file(image)

                    # If validation passes, save images
                    for i, image_file in enumerate(images[:5]):  # Limit to 5 images
                        ListingImage.objects.create(
                            listing=listing,
                            image=image_file,
                            is_main=(i == 0)  # First image is main
                        )
                except ValidationError as e:
                    # If validation fails, delete the listing and return error
                    listing.delete()
                    messages.error(request, str(e))
                    return redirect('home')

            messages.success(request, 'Your listing has been created successfully!')
            return redirect('home')
        else:
            # Form is invalid - store errors in session and redirect
            form_errors = form.errors.get_json_data()

            # Add category error if missing
            if not category_value:
                form_errors['category'] = [{'message': 'This field is required.', 'code': 'required'}]

            request.session['form_errors'] = form_errors
            request.session['form_data'] = request.POST.dict()
            request.session['show_create_modal'] = True
            return redirect('home')
    else:
        form = ListingForm()
    return render(request, 'thryve_app/create_listing.html', {'form': form})

@login_required(login_url='login')
def edit_listing(request, listing_id):
    try:
        listing = Listing.objects.get(id=listing_id, user=request.user)
    except Listing.DoesNotExist:
        messages.error(request, 'Listing not found.')
        return redirect('thryve_app:my_listings')

    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            listing = form.save(commit=False)

            # Parse category and subcategory from the POST data
            category_value = request.POST.get('category', '')
            if '-' in category_value:
                main_category, subcategory = category_value.split('-', 1)
                listing.category = main_category
                listing.subcategory = subcategory
            else:
                listing.category = category_value
                listing.subcategory = None

            listing.save()

            # Handle image reordering first (from POST data)
            image_order = request.POST.get('image_order', '')
            if image_order:
                image_ids = [int(id.strip()) for id in image_order.split(',') if id.strip()]
                for index, image_id in enumerate(image_ids):
                    try:
                        image_obj = ListingImage.objects.get(id=image_id, listing=listing)
                        image_obj.is_main = (index == 0)  # First image is main
                        image_obj.save()
                    except ListingImage.DoesNotExist:
                        pass  # Skip if image doesn't exist

            # Handle multiple image uploads (only add new ones, don't replace existing)
            images = request.FILES.getlist('images')
            if images:
                current_images_count = listing.images.count()

                try:
                    # Validate image count
                    validate_images_count(images, current_images_count)

                    # Validate each image file
                    for image in images:
                        validate_image_file(image)

                    # If validation passes, save images
                    for i, image_file in enumerate(images[:5 - current_images_count]):
                        ListingImage.objects.create(
                            listing=listing,
                            image=image_file,
                            is_main=(current_images_count == 0 and i == 0)
                        )
                except ValidationError as e:
                    messages.error(request, str(e))
                    return redirect('thryve_app:my_listings')

            messages.success(request, 'Your listing has been updated successfully!')
            return redirect('thryve_app:my_listings')
        else:
            # Form is invalid - show errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return redirect('thryve_app:my_listings')

    # GET request - render edit page
    form = ListingForm(instance=listing)
    category_value = listing.category
    if listing.subcategory:
        category_value = f"{listing.category}-{listing.subcategory}"

    return render(request, 'thryve_app/edit_listing.html', {
        'form': form,
        'listing': listing,
        'category_value': category_value,
        'categories': Listing.get_categories_dict(),
        'listing_types': LISTING_TYPES,
    })

@login_required(login_url='login')
def delete_listing(request, listing_id):
    try:
        listing = Listing.objects.get(id=listing_id, user=request.user)
        listing.delete()
        messages.success(request, 'Your listing has been deleted successfully!')
    except Listing.DoesNotExist:
        messages.error(request, 'Listing not found.')

    return redirect('thryve_app:my_listings')


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
