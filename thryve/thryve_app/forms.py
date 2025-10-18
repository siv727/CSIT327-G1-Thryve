from django import forms
from .models import Listing

class ListingForm(forms.ModelForm):
    swap_for = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky',
            'placeholder': 'What are you looking to swap for?'
        })
    )
    budget = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky',
            'placeholder': '0.00',
            'step': '0.01'
        })
    )

    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'id': 'id_image',
            'accept': 'image/jpeg,image/png,image/gif,image/webp'
        })
    )

    class Meta:
        model = Listing
        fields = ['listing_type', 'category', 'title', 'description', 'price', 'swap_for', 'budget', 'your_name', 'company', 'location', 'image']
        widgets = {
            'listing_type': forms.Select(attrs={'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky'}),
            'category': forms.Select(attrs={'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky'}),
            'title': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky', 'placeholder': 'Enter listing title'}),
            'description': forms.Textarea(attrs={'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky resize-none', 'rows': 4, 'placeholder': 'Describe your item or service'}),
            'price': forms.NumberInput(attrs={'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky', 'placeholder': '0.00', 'step': '0.01'}),
            'your_name': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky', 'placeholder': 'Your full name'}),
            'company': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky', 'placeholder': 'Company name'}),
            'location': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky', 'placeholder': 'City, State/Country'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default category display
        self.fields['category'].empty_label = None  # Remove empty label so "Other" is selected by default
        # Make all fields required
        for field in self.fields.values():
            field.required = True