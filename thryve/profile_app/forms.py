# profile_app/forms.py
from django import forms
from django.core.exceptions import ValidationError
import re
from .models import UserProfile

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
                'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-sky-300',
            }),
            'bio': forms.Textarea(attrs={
                'id': 'id_bio',
                'rows': 6,
                'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-sky-300 resize-y',
            }),
            'avatar': forms.FileInput(attrs={
                'id': 'id_avatar',
                'accept': 'image/jpeg,image/png,image/gif,image/webp'
            })
        }

