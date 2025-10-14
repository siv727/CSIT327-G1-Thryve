from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProfileCustomizationForm
from .models import UserProfile

@login_required
def business_profile_view(request):
    return render(request, 'profile_app/business_profile.html')

@login_required
def profile_customization_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileCustomizationForm(request.POST, request.FILES, instance=profile)
        print(f"POST request received. FILES: {request.FILES}")
        print(f"Avatar in FILES: {'avatar' in request.FILES}")
        if 'avatar' in request.FILES:
            print(f"Avatar file: {request.FILES['avatar']}")
        if form.is_valid():
            print("Form is valid, saving...")
            saved_profile = form.save()
            print(f"Saved profile: {saved_profile}, avatar: {saved_profile.avatar}")
            print(f"Avatar URL: {saved_profile.avatar.url if saved_profile.avatar else 'None'}")
            return redirect('profile_customization')
        else:
            print(f"Form errors: {form.errors}")
            print(f"Non-field errors: {form.non_field_errors()}")
    else:
        form = ProfileCustomizationForm(instance=profile)
        print(f"GET request. Profile avatar: {profile.avatar}")

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
