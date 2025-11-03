from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import ListingForm
from .models import ListingImage

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
