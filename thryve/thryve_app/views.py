from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ListingForm
from .models import ListingImage

@login_required(login_url='login')
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.user = request.user
            listing.your_name = request.user.email
            listing.company = request.user.company_name

            # Parse category and subcategory from the combined value
            category_value = form.cleaned_data['category']
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

            messages.success(request, 'Your listing has been created successfully!')
            return redirect('home')
        else:
            # Form is invalid, return with errors to display in modal
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
