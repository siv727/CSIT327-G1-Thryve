from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_control

from django.db.models import Q

@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def marketplace(request):
    from thryve_app.forms import ListingForm
    from thryve_app.models import Listing
    from thryve_app.views import LISTING_TYPES

    # Check if there are form errors in session
    form_errors = request.session.pop('form_errors', None)
    form_data = request.session.pop('form_data', None)
    show_create_modal = request.session.pop('show_create_modal', False)

    if form_errors and form_data:
        # Reconstruct form with errors
        form = ListingForm(data=form_data)
        form.is_valid()  # Trigger validation to populate errors

        # Add custom category error if present
        if 'category' in form_errors:
            from django.forms.utils import ErrorList
            form.errors['category'] = ErrorList([form_errors['category'][0]['message']])
    else:
        form = ListingForm()

    search_query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', '').strip()
    type_filter = request.GET.get('type', '').strip()  # '', 'sale', 'swap', 'buy'

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
    })