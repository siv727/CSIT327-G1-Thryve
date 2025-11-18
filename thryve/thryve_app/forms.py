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
        fields = ['listing_type', 'title', 'description', 'price', 'swap_for', 'budget', 'location']
        widgets = {
            'listing_type': forms.Select(attrs={'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky placeholder:text-slate-400'}),
            'title': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky placeholder:text-slate-400', 'placeholder': 'Enter listing title'}),
            'description': forms.Textarea(attrs={'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky resize-none', 'rows': 4, 'placeholder': 'Describe your item or service'}),
            'price': forms.NumberInput(attrs={'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky placeholder:text-slate-400', 'placeholder': '0.00', 'step': '0.01'}),
            'location': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky placeholder:text-slate-400', 'placeholder': 'City, State/Country'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove category from form fields since we handle it with JavaScript
        if 'category' in self.fields:
            del self.fields['category']
        # Make specific fields required based on listing type
        self.fields['listing_type'].required = True
        self.fields['title'].required = True
        self.fields['description'].required = True
        self.fields['location'].required = True
        # Dynamic fields are handled in JavaScript validation
        self.fields['price'].required = False
        self.fields['swap_for'].required = False
        self.fields['budget'].required = False
        # self.fields['image'].required = False  # Removed since we removed the image field

    def clean(self):
        cleaned_data = super().clean()
        listing_type = cleaned_data.get('listing_type')

        # Validate category and subcategory from POST data
        if hasattr(self, 'data') and 'category' in self.data:
            category_value = self.data.get('category', '')
            if not category_value or category_value == '':
                raise forms.ValidationError("Please select a category")

            if '-' in category_value:
                main_category, subcategory = category_value.split('-', 1)
                # Validate that the main category is valid
                valid_categories = [choice[0] for choice in Listing.CATEGORY_CHOICES]
                if main_category not in valid_categories:
                    raise forms.ValidationError(f"Invalid category '{main_category}'")

                # Validate that the subcategory exists for this category
                valid_subcategories = Listing.SUBCATEGORY_CHOICES.get(main_category, [])
                valid_subcategory_values = [sub[0] for sub in valid_subcategories]
                if subcategory not in valid_subcategory_values:
                    raise forms.ValidationError(f"Invalid subcategory '{subcategory}' for category '{main_category}'")
            else:
                # Just a main category, validate it's valid
                valid_categories = [choice[0] for choice in Listing.CATEGORY_CHOICES]
                if category_value not in valid_categories:
                    raise forms.ValidationError(f"Invalid category '{category_value}'")

        return cleaned_data