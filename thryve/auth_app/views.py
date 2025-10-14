from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_control

from .forms import RegistrationForm, LoginForm
from django.contrib.auth import login, authenticate, logout


def register (request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            request.session['just_registered'] = True
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    just_registered = request.session.pop('just_registered', False)
    
    if request.user.is_authenticated and not just_registered:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request, request.POST)
        if form.is_valid():
            email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})

@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    
    return render(request, 'accounts/logout.html')

def landing(request):
    return render(request, 'landing/landing.html')

# Temporary view for home after login
@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request):
    return render(request, 'landing/home.html')

# Use this view for the marketplace UI (your current home.html)
# def marketplace(request):
#     return render(request, "home.html")

# (optional) keep a separate landing page
# def landing(request):
#     return render(request, "landing/landing.html")