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

    # Get user's initial and assign a color class for default avatar
    user = request.user
    initial = (user.first_name or user.username)[0].upper()
    color_classes = ['bg-red-400', 'bg-teal-400', 'bg-blue-400', 'bg-green-400', 'bg-yellow-400', 'bg-purple-400', 'bg-cyan-400', 'bg-amber-400', 'bg-violet-400', 'bg-sky-400']
    color_class = color_classes[ord(initial) % len(color_classes)]

    return render(request, 'profile_app/profile_customization.html', {
        'form': form,
        'user': user,
        'initial': initial,
        'avatar_color_class': color_class
    })
