from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ListingForm

@login_required(login_url='login')
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.user = request.user
            listing.save()
            messages.success(request, 'Your listing has been created successfully!')
            return redirect('home')
    else:
        form = ListingForm()
    return render(request, 'thryve_app/create_listing.html', {'form': form})
