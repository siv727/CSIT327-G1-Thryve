from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ProfileCustomizationForm
from .models import UserProfile
from .forms import BusinessProfileForm
from .models import BusinessProfile

@login_required
def business_profile_view(request):
    # ensure a BusinessProfile exists for this user
    profile, created = BusinessProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = BusinessProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Business details updated.")
            return redirect('business_profile')   # or whatever your URL name is
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = BusinessProfileForm(instance=profile)

    return render(request, 'profile_app/business_profile.html', {
        'form': form,
        'profile': profile,
    })
@login_required
def profile_customization_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileCustomizationForm(request.POST, request.FILES, instance=profile, user=request.user)
        print(f"POST request received. FILES: {request.FILES}")
        print(f"POST data: {request.POST}")
        print(f"Avatar in FILES: {'avatar' in request.FILES}")
        if 'avatar' in request.FILES:
            print(f"Avatar file: {request.FILES['avatar']}")
        if form.is_valid():
            print("Form is valid, saving...")
            saved_profile = form.save()
            print(f"Saved profile: {saved_profile}, avatar: {saved_profile.avatar}")
            print(f"Display name: {saved_profile.display_name}")
            print(f"Tagline: {saved_profile.tagline}")
            print(f"Bio: {saved_profile.bio}")
            print(f"Avatar URL: {saved_profile.avatar.url if saved_profile.avatar else 'None'}")
            return redirect('profile_customization')
        else:
            print(f"Form errors: {form.errors}")
            print(f"Non-field errors: {form.non_field_errors()}")
    else:
        form = ProfileCustomizationForm(instance=profile, user=request.user)
        print(f"GET request. Profile display_name: {profile.display_name}, tagline: {profile.tagline}, bio: {profile.bio}, avatar: {profile.avatar}")

    # Get user's initial and assign a color class for default avatar
    user = request.user
    initial = (user.first_name or str(user))[0].upper()
    color_classes = ['bg-red-400', 'bg-teal-400', 'bg-blue-400', 'bg-green-400', 'bg-yellow-400', 'bg-purple-400', 'bg-cyan-400', 'bg-amber-400', 'bg-violet-400', 'bg-sky-400']
    color_class = color_classes[ord(initial) % len(color_classes)]

    return render(request, 'profile_app/profile_customization.html', {
        'form': form,
        'user': user,
        'initial': initial,
        'avatar_color_class': color_class
    })
