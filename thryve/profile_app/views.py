from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProfileCustomizationForm

@login_required
def business_profile_view(request):
    return render(request, 'profile_app/business_profile.html')

@login_required
def profile_customization_view(request):
    if request.method == 'POST':
        form = ProfileCustomizationForm(request.POST, request.FILES)
        if form.is_valid():
            # TODO: save to your user/profile model
            return redirect('profile_customization')
    else:
        form = ProfileCustomizationForm()

    return render(request, 'profile_app/profile_customization.html', {'form': form})
