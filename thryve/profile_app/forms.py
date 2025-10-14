# profile_app/forms.py
from django import forms
from .models import UserProfile

class ProfileCustomizationForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['display_name', 'tagline', 'bio', 'avatar']
        widgets = {
            'display_name': forms.TextInput(attrs={
                'id': 'id_display_name',
                'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-sky-300',
            }),
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

