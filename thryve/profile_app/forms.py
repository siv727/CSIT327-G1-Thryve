# profile_app/forms.py
from django import forms

class ProfileCustomizationForm(forms.Form):
    display_name = forms.CharField(
        initial='Alex Johnson',
        widget=forms.TextInput(attrs={
            'id': 'id_display_name',
            'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-sky-300',
        })
    )
    tagline = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'id': 'id_tagline',
            'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-sky-300',
        })
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'id': 'id_bio',
            'rows': 6,
            'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-sky-300 resize-y',
        })
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'id': 'id_avatar', 'accept': 'image/*'})
    )

