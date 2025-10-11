from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user_model

User = get_user_model()  # ✅ Use your custom user model

def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        company_name = request.POST.get('company_name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not email or not first_name or not last_name or not company_name or not password1 or not password2:
            return render(request, 'thryve_app/register.html', {'error': 'Please fill in all fields.'})

        if password1 != password2:
            return render(request, 'thryve_app/register.html', {'error': 'Passwords do not match.'})

        if User.objects.filter(email=email).exists():
            return render(request, 'thryve_app/register.html', {'error': 'Email already exists.'})

        user = User.objects.create_user(email=email, password=password1, first_name=first_name, last_name=last_name, company_name=company_name)
        login(request, user)
        return redirect('home')

    return render(request, 'thryve_app/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'thryve_app/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def home(request):
    return render(request, 'thryve_app/dashboard.html')