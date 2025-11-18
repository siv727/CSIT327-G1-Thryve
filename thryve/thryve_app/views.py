from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .forms import ListingForm
from .models import ListingImage, Listing, Connection, ConnectionRequest

@login_required(login_url='login')
def my_listings(request):
    # Get listings created by the current user
    user_listings = Listing.objects.filter(user=request.user).prefetch_related('images').order_by('-created_at')

    return render(request, 'landing/home.html', {
        'listings': user_listings,
        'is_my_listings': True
    })

@login_required(login_url='login')
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.user = request.user
            try:
                listing.your_name = request.user.profile.display_name or f"{request.user.first_name} {request.user.last_name}"
            except:
                listing.your_name = f"{request.user.first_name} {request.user.last_name}"
            listing.company = request.user.company_name

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

            # Handle multiple image uploads
            images = request.FILES.getlist('images')
            if images:
                for i, image_file in enumerate(images[:5]):  # Limit to 5 images
                    ListingImage.objects.create(
                        listing=listing,
                        image=image_file,
                        is_main=(i == 0)  # First image is main
                    )

            # Check if this is an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Your listing has been created successfully!'})
            else:
                messages.success(request, 'Your listing has been created successfully!')
                return redirect('home')
        else:
            # Form is invalid
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return JSON error response for AJAX
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = [str(error) for error in error_list]
                return JsonResponse({'success': False, 'errors': errors})
            else:
                # Return with errors to display in modal for regular requests
                from thryve_app.models import Listing
                listings = Listing.objects.all().order_by('-created_at')
                return render(request, 'landing/home.html', {
                    'form': form,
                    'show_modal': True,
                    'listings': listings
                })
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

    if request.method == 'GET':
        # Handle AJAX GET request for modal data
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            listing_data = {
                'id': listing.id,
                'listing_type': listing.listing_type,
                'category': listing.category,
                'subcategory': listing.subcategory,
                'title': listing.title,
                'description': listing.description,
                'price': str(listing.price) if listing.price else '',
                'swap_for': listing.swap_for or '',
                'budget': str(listing.budget) if listing.budget else '',
                'location': listing.location,
                'images': [{'id': img.id, 'image': img.image.url, 'is_main': img.is_main} for img in listing.images.all()]
            }
            return JsonResponse({'success': True, 'listing': listing_data})
        else:
            form = ListingForm(instance=listing)
            # Prepare category value for the form
            category_value = listing.category
            if listing.subcategory:
                category_value = f"{listing.category}-{listing.subcategory}"
            return render(request, 'thryve_app/edit_listing.html', {
                'form': form,
                'listing': listing,
                'category_value': category_value
            })

    # Handle POST request for updating
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
            # Get current image count
            current_images_count = listing.images.count()
            for i, image_file in enumerate(images[:5 - current_images_count]):  # Limit to remaining slots
                ListingImage.objects.create(
                    listing=listing,
                    image=image_file,
                    is_main=(current_images_count == 0 and i == 0)  # First image is main if no images exist
                )

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Your listing has been updated successfully!'})
        else:
            messages.success(request, 'Your listing has been updated successfully!')
            return redirect('thryve_app:my_listings')
    else:
        # Form is invalid
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return JSON error response for AJAX
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = [str(error) for error in error_list]
            return JsonResponse({'success': False, 'errors': errors})
        else:
            # Prepare category value for the form
            category_value = listing.category
            if listing.subcategory:
                category_value = f"{listing.category}-{listing.subcategory}"
            return render(request, 'thryve_app/edit_listing.html', {
                'form': form,
                'listing': listing,
                'category_value': category_value
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
            # Check if request already exists
            existing_request = ConnectionRequest.objects.filter(
                sender=request.user,
                receiver=receiver,
                status='pending'
            ).exists()
            if existing_request:
                return JsonResponse({'success': False, 'message': 'Connection request already sent.'})
            # Check if already connected
            existing_connection = Connection.objects.filter(
                (Q(user1=request.user) & Q(user2=receiver)) |
                (Q(user1=receiver) & Q(user2=request.user))
            ).exists()
            if existing_connection:
                return JsonResponse({'success': False, 'message': 'Already connected.'})
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
