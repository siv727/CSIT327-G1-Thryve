import re

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import CustomUser

class RegistrationForm(UserCreationForm):
    INVALID_NAME_PATTERN = r'[\'\"@_!#$%^&*()<>?/|}{~:]'
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'First Name',
        'class': 'w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 transition-colors',
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Last Name',
        'class': 'w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 transition-colors',
    }))
    company_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Company Name',
        'class': 'w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 transition-colors',
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Email Address',
        'class': 'w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 transition-colors',
    }))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Phone Number (XXX XXX XXXX)',
        'class': 'w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 transition-colors phone-input',
        'oninput': 'formatPhoneNumber(this)',
        'data-previous-value': '',
        'data-previous-cursor': '0',
    }))

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'company_name', 'email', 'phone_number', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize the built-in password fields
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Password',
            'class': 'w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 transition-colors',
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm Password',
            'class': 'w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 transition-colors',
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("User already exists")
        return email
    
    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name')
        if company_name and CustomUser.objects.filter(company_name=company_name).exists():
            raise forms.ValidationError("Company name already exists")
        return company_name

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            # Check minimum length
            if len(password) < 8:
                raise forms.ValidationError("Password must be at least 8 characters long.")

            # Check for uppercase letter
            if not any(char.isupper() for char in password):
                raise forms.ValidationError("Password must contain at least one uppercase letter.")

            # Check for lowercase letter
            if not any(char.islower() for char in password):
                raise forms.ValidationError("Password must contain at least one lowercase letter.")

            # Check for numeric digit
            if not any(char.isdigit() for char in password):
                raise forms.ValidationError("Password must contain at least one numeric digit.")

        return password

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Remove spaces for digit count
            digits_only = re.sub(r'\s+', '', phone_number)
            if not re.match(r'^\d{10}$', digits_only):
                raise forms.ValidationError("Phone number must contain exactly 10 digits.")
            # Check format XXX XXX XXXX
            if not re.match(r'^\d{3} \d{3} \d{4}$', phone_number):
                raise forms.ValidationError("Phone number must be in the format XXX XXX XXXX.")
        return phone_number

class LoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Email Address',
        'class': 'w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 transition-colors',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password',
        'class': 'w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 transition-colors',
    }))