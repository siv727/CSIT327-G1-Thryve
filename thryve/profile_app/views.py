# profile_app/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.cache import cache_control

from .forms import ProfileCustomizationForm, BusinessProfileForm, BusinessLogoForm
from .models import UserProfile, BusinessProfile

# cleaned single decorator usage and correct form handling
@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def business_profile_view(request):
    # ensure BusinessProfile exists for the logged-in user
    profile, created = BusinessProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = BusinessProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Business details updated.")
            return redirect('business_profile')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = BusinessProfileForm(instance=profile)

    return render(request, 'profile_app/business_profile.html', {
        'form': form,
        'profile': profile,
    })

@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def profile_customization_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileCustomizationForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect('profile_customization')
    else:
        form = ProfileCustomizationForm(instance=profile, user=request.user)

    # initial and avatar color logic here (kept as you had it)
    user = request.user
    initial = (user.first_name or str(user))[0].upper()
    color_classes = ['bg-red-400', 'bg-teal-400', 'bg-blue-400', 'bg-green-400',
                     'bg-yellow-400', 'bg-purple-400', 'bg-cyan-400', 'bg-amber-400',
                     'bg-violet-400', 'bg-sky-400']
    color_class = color_classes[ord(initial) % len(color_classes)]

    return render(request, 'profile_app/profile_customization.html', {
        'form': form,
        'user': user,
        'initial': initial,
        'avatar_color_class': color_class
    })


@login_required(login_url='login')
def business_logo(request):
    business_profile, _ = BusinessProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = BusinessLogoForm(request.POST, request.FILES, instance=business_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Logo uploaded.")
            return redirect('business_logo')
        else:
            messages.error(request, "Please fix the errors with the logo upload.")
    else:
        form = BusinessLogoForm(instance=business_profile)

    return render(request, 'profile_app/business_logo.html', {
        'business_profile': business_profile,
        'form': form,
    })
