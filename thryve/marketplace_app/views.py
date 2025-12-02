from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.views.decorators.cache import cache_control

from .forms import ListingForm, validate_images_count, validate_image_file
from thryve_app.models import Listing, ListingImage

LISTING_TYPES = [
    {'value': 'sale', 'label': 'For Sale'},
    {'value': 'swap', 'label': 'For Swap'},
    {'value': 'buy', 'label': 'Looking to Buy'},
]


@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def marketplace_home(request):
    """
    Main marketplace view. Handles searching, filtering, and displaying listings.
    Previously 'home' in auth_app.
    """
    # Check if there are form errors in session (passed from create_listing)
    form_errors = request.session.pop('form_errors', None)
    form_data = request.session.pop('form_data', None)
    show_create_modal = request.session.pop('show_create_modal', False)

    if form_errors and form_data:
        form = ListingForm(data=form_data)
        form.is_valid()  # Trigger validation to populate errors
        if 'category' in form_errors:
            from django.forms.utils import ErrorList
            form.errors['category'] = ErrorList([form_errors['category'][0]['message']])
    else:
        form = ListingForm()

    search_query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', '').strip()
    type_filter = request.GET.get('type', '').strip()

    listings_qs = Listing.objects.prefetch_related('images').all()

    if search_query:
        listings_qs = listings_qs.filter(Q(title__icontains=search_query))

    if category_filter:
        listings_qs = listings_qs.filter(category=category_filter)

    if type_filter in ['sale', 'swap', 'buy']:
        listings_qs = listings_qs.filter(listing_type=type_filter)

    listings = listings_qs.order_by('-created_at')

    return render(request, 'marketplace.html', {
        'form': form,
        'listings': listings,
        'categories': Listing.get_categories_dict(),
        'listing_types': LISTING_TYPES,
        'search_query': search_query,
        'category_filter': category_filter,
        'type_filter': type_filter,
        'show_create_modal': show_create_modal,
        'is_my_listings': False,
    })


@login_required(login_url='login')
def my_listings(request):
    """View for managing current user's listings."""
    user_listings = Listing.objects.filter(user=request.user).prefetch_related('images').order_by('-created_at')

    # We reuse the home template but with specific context
    return render(request, 'marketplace.html', {
        'listings': user_listings,
        'is_my_listings': True,
        'categories': Listing.get_categories_dict(),
        'listing_types': LISTING_TYPES,
        'form': ListingForm(),  # Empty form for the modal
    })


@login_required(login_url='login')
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
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

            if '-' in category_value:
                main_category, subcategory = category_value.split('-', 1)
                listing.category = main_category
                listing.subcategory = subcategory
            else:
                listing.category = category_value
                listing.subcategory = None

            listing.save()

            images = request.FILES.getlist('images')
            if images:
                try:
                    validate_images_count(images)
                    for image in images:
                        validate_image_file(image)

                    for i, image_file in enumerate(images[:5]):
                        ListingImage.objects.create(
                            listing=listing,
                            image=image_file,
                            is_main=(i == 0)
                        )
                except ValidationError as e:
                    listing.delete()
                    messages.error(request, str(e))
                    return redirect('marketplace:home')

            messages.success(request, 'Your listing has been created successfully!')
            return redirect('marketplace:home')
        else:
            # Handle invalid form by storing data in session and redirecting
            form_errors = form.errors.get_json_data()
            if not category_value:
                form_errors['category'] = [{'message': 'This field is required.', 'code': 'required'}]

            request.session['form_errors'] = form_errors
            request.session['form_data'] = request.POST.dict()
            request.session['show_create_modal'] = True
            return redirect('marketplace:home')

    return redirect('marketplace:home')


@login_required(login_url='login')
def edit_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, user=request.user)

    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            listing = form.save(commit=False)

            category_value = request.POST.get('category', '')
            if '-' in category_value:
                main_category, subcategory = category_value.split('-', 1)
                listing.category = main_category
                listing.subcategory = subcategory
            else:
                listing.category = category_value
                listing.subcategory = None

            listing.save()

            # Handle Image Reordering
            image_order = request.POST.get('image_order', '')
            if image_order:
                image_ids = [int(id.strip()) for id in image_order.split(',') if id.strip()]
                for index, img_id in enumerate(image_ids):
                    try:
                        image_obj = ListingImage.objects.get(id=img_id, listing=listing)
                        image_obj.is_main = (index == 0)
                        image_obj.save()
                    except ListingImage.DoesNotExist:
                        pass

            # Handle New Images
            images = request.FILES.getlist('images')
            if images:
                current_images_count = listing.images.count()
                try:
                    validate_images_count(images, current_images_count)
                    for image in images:
                        validate_image_file(image)

                    for i, image_file in enumerate(images[:5 - current_images_count]):
                        ListingImage.objects.create(
                            listing=listing,
                            image=image_file,
                            is_main=(current_images_count == 0 and i == 0)
                        )
                except ValidationError as e:
                    messages.error(request, str(e))
                    return redirect('marketplace:my_listings')

            messages.success(request, 'Your listing has been updated successfully!')
            return redirect('marketplace:my_listings')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return redirect('marketplace:my_listings')

    # GET request
    form = ListingForm(instance=listing)
    category_value = listing.category
    if listing.subcategory:
        category_value = f"{listing.category}-{listing.subcategory}"

    return render(request, 'edit_listing.html', {
        'form': form,
        'listing': listing,
        'category_value': category_value,
        'categories': Listing.get_categories_dict(),
        'listing_types': LISTING_TYPES,
    })


@login_required(login_url='login')
def delete_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, user=request.user)
    if request.method == 'POST':
        listing.delete()
        messages.success(request, 'Your listing has been deleted successfully!')
    return redirect('marketplace:my_listings')