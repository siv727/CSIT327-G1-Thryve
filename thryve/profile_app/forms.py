# profile_app/forms.py
from django import forms
from django.core.exceptions import ValidationError
import re
from .models import UserProfile
from .models import BusinessProfile

class BusinessProfileForm(forms.ModelForm):
    class Meta:
        model = BusinessProfile
        fields = [
            'company_name', 'industry', 'description',
            'street_address', 'city', 'state',
            'zip_code', 'country', 'website_url',
            'contact_phone', 'contact_email'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'w-full border border-line rounded-lg bg-white px-3 py-2.5 outline-none focus:ring-2 focus:ring-brand-500/30',
                'placeholder': 'MarketConnect Pro Solutions'
            }),
            'industry': forms.TextInput(attrs={
                'class': 'w-full border border-line rounded-lg bg-white px-3 py-2.5 outline-none focus:ring-2 focus:ring-brand-500/30',
                'placeholder': 'Select industry'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full border border-line rounded-lg bg-white px-3 py-2.5 outline-none resize-y focus:ring-2 focus:ring-brand-500/30',
                'rows': 4,
                'placeholder': 'Describe your company, what you do, and your value proposition.'
            }),
            'street_address': forms.TextInput(attrs={
                'class': 'w-full border border-line rounded-lg bg-white px-3 py-2.5 outline-none focus:ring-2 focus:ring-brand-500/30',
                'placeholder': '123 Main Street'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full border border-line rounded-lg bg-white px-3 py-2.5 outline-none focus:ring-2 focus:ring-brand-500/30',
                'placeholder': 'Anytown'
            }),
            'state': forms.TextInput(attrs={
                'class': 'w-full border border-line rounded-lg bg-white px-3 py-2.5 outline-none focus:ring-2 focus:ring-brand-500/30',
                'placeholder': 'CA'
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'w-full border border-line rounded-lg bg-white px-3 py-2.5 outline-none focus:ring-2 focus:ring-brand-500/30',
                'placeholder': '90210'
            }),
            'country': forms.TextInput(attrs={
                'class': 'w-full border border-line rounded-lg bg-white px-3 py-2.5 outline-none focus:ring-2 focus:ring-brand-500/30',
                'placeholder': 'USA'
            }),
            'website_url': forms.URLInput(attrs={
                'class': 'w-full outline-none',
                'placeholder': 'www.marketconnectpro.com'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'w-full border border-line rounded-lg bg-white px-3 py-2.5 outline-none focus:ring-2 focus:ring-brand-500/30',
                'placeholder': '+1 (555) 123-4567'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'w-full border border-line rounded-lg bg-white px-3 py-2.5 outline-none focus:ring-2 focus:ring-brand-500/30',
                'placeholder': 'contact@company.com'
            }),
        }

def validate_display_name(value):
    """Validate that display name contains at least one letter and allows common characters."""
    stripped_name = value.strip()
    if stripped_name == "":
        raise ValidationError("Please enter a display name.")

    # Must contain at least one letter
    if not re.search(r'[a-zA-Z]', stripped_name):
        raise ValidationError("Display name must contain at least one letter.")

    # Allow letters, numbers, spaces, and common punctuation
    # Reject only clearly problematic characters
    INVALID_CHARS = r'[@_!#$%^&*()<>?/|}{~:]'
    if re.search(INVALID_CHARS, stripped_name):
        raise ValidationError("Display name contains invalid characters.")

class ProfileCustomizationForm(forms.ModelForm):
    display_name = forms.CharField(
        validators=[validate_display_name],
        widget=forms.TextInput(attrs={
            'id': 'id_display_name',
            'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-sky-300',
        })
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Set default display name from user's first name only
        if self.user and not self.instance.display_name:
            self.initial['display_name'] = self.user.first_name

    class Meta:
        model = UserProfile
        fields = ['display_name', 'tagline', 'bio', 'avatar']
        widgets = {
            'tagline': forms.TextInput(attrs={
                'id': 'id_tagline',
                'placeholder': 'Describe yourself in a few words',
                'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-sky-300',
            }),
            'bio': forms.Textarea(attrs={
                'id': 'id_bio',
                'rows': 6,
                'placeholder': 'Tell others about yourself, your experience, and what you do...',
                'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-sky-300 resize-y',
            }),
            'avatar': forms.FileInput(attrs={
                'id': 'id_avatar',
                'accept': 'image/jpeg,image/png,image/gif,image/webp'
            })
        }
class BusinessLogoForm(forms.ModelForm):
    class Meta:
        model = BusinessProfile
        fields = ['logo']
        widgets = {
            'logo': forms.ClearableFileInput(attrs={'accept': 'image/*'})
        }