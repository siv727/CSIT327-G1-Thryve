from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from .forms import ListingForm, validate_images_count, validate_image_file
from .models import ListingImage, Listing

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

    return render(request, 'landing/home.html', {
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
            # Form is invalid - show errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
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
