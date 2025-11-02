from django import forms
from .models import Listing, ListingImage

class ListingForm(forms.ModelForm):
    swap_for = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky placeholder:text-slate-400',
            'placeholder': 'What are you looking to swap for?'
        })
    )
    budget = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky placeholder:text-slate-400',
            'placeholder': '0.00',
            'step': '0.01'
        })
    )

    # Remove images field from form - we'll handle it manually in the view

    class Meta:
        model = Listing
        fields = ['listing_type', 'category', 'title', 'description', 'price', 'swap_for', 'budget', 'location']
        widgets = {
            'listing_type': forms.Select(attrs={'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky placeholder:text-slate-400'}),
            'title': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky placeholder:text-slate-400', 'placeholder': 'Enter listing title'}),
            'description': forms.Textarea(attrs={'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky resize-none', 'rows': 4, 'placeholder': 'Describe your item or service'}),
            'price': forms.NumberInput(attrs={'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky placeholder:text-slate-400', 'placeholder': '0.00', 'step': '0.01'}),
            'location': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky placeholder:text-slate-400', 'placeholder': 'City, State/Country'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default category display
        self.fields['category'].empty_label = "Choose Category"
        # Make specific fields required based on listing type
        self.fields['listing_type'].required = True
        self.fields['category'].required = True
        self.fields['title'].required = True
        self.fields['description'].required = True
        self.fields['location'].required = True
        # Dynamic fields are handled in JavaScript validation
        self.fields['price'].required = False
        self.fields['swap_for'].required = False
        self.fields['budget'].required = False
        # self.fields['image'].required = False  # Removed since we removed the image field