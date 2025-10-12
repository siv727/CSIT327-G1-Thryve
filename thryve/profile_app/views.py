from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def business_profile_view(request):
    return render(request, 'profile_app/business_profile.html')
