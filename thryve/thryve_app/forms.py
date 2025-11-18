from django import forms
from django.core.exceptions import ValidationError
from .models import Listing, ListingImage

def validate_images_count(files, existing_count=0):
    """Validate that total image count doesn't exceed 5"""
    total_count = len(files) + existing_count
    if total_count > 5:
        raise ValidationError(f'Maximum 5 images allowed. You have {existing_count} existing images and are trying to add {len(files)} more.')
    return True

def validate_image_file(image):
    """Validate individual image file"""
    # Check file size (5MB max)
    max_size = 5 * 1024 * 1024  # 5MB
    if image.size > max_size:
        raise ValidationError(f'Image "{image.name}" is too large. Maximum size is 5MB.')
    
    # Check file format
    valid_formats = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if hasattr(image, 'content_type'):
        if image.content_type not in valid_formats:
            raise ValidationError(f'Unsupported format for "{image.name}". Please upload JPEG, PNG, GIF, or WebP images.')
    
    return True

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
        fields = ['listing_type', 'title', 'description', 'price', 'swap_for', 'budget', 'location', 'date']
        widgets = {
            'listing_type': forms.Select(attrs={'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky placeholder:text-slate-400'}),
            'title': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky placeholder:text-slate-400', 'placeholder': 'Enter listing title'}),
            'description': forms.Textarea(attrs={'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky resize-none', 'rows': 4, 'placeholder': 'Describe your item or service'}),
            'price': forms.NumberInput(attrs={'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky placeholder:text-slate-400', 'placeholder': '0.00', 'step': '0.01'}),
            'location': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky placeholder:text-slate-400', 'placeholder': 'City, State/Country'}),
            'date': forms.DateInput(attrs={'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky placeholder:text-slate-400', 'type': 'date'}),
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
        self.fields['date'].required = True
        # Dynamic fields are handled in JavaScript validation
        self.fields['price'].required = False
        self.fields['swap_for'].required = False
        self.fields['budget'].required = False
        # self.fields['image'].required = False  # Removed since we removed the image field

    def clean_description(self):
        """Validate and sanitize description"""
        description = self.cleaned_data.get('description')
        if description:
            # Remove excessive whitespace
            description = ' '.join(description.split())
            # Limit length
            if len(description) > 5000:
                raise forms.ValidationError('Description too long (max 5000 characters)')
            # Basic sanitization (full sanitization happens in model save)
            if len(description.strip()) < 10:
                raise forms.ValidationError('Description is too short (minimum 10 characters)')
        return description

    def clean_date(self):
        """Validate date field"""
        date = self.cleaned_data.get('date')
        if date:
            from datetime import date as dt_date
            if date < dt_date.today():
                raise forms.ValidationError('Date cannot be in the past')
        return date

    def clean_location(self):
        """Validate location field"""
        location = self.cleaned_data.get('location')
        if location:
            # Basic length validation
            if len(location) < 3:
                raise forms.ValidationError('Location too short (minimum 3 characters)')
            if len(location) > 100:
                raise forms.ValidationError('Location too long (max 100 characters)')
        return location

    def clean(self):
        cleaned_data = super().clean()
        listing_type = cleaned_data.get('listing_type')

        # Validate required fields based on listing type
        if listing_type == 'sale':
            price = cleaned_data.get('price')
            if not price:
                raise forms.ValidationError({'price': 'Price is required for sale listings'})
            if price < 0:
                raise forms.ValidationError({'price': 'Price cannot be negative'})
            if price > 999999.99:
                raise forms.ValidationError({'price': 'Price too high (max ₱999,999.99)'})
        
        if listing_type == 'swap':
            swap_for = cleaned_data.get('swap_for')
            if not swap_for or len(swap_for.strip()) == 0:
                raise forms.ValidationError({'swap_for': 'Swap details are required for swap listings'})
            if len(swap_for) < 5:
                raise forms.ValidationError({'swap_for': 'Please provide more details (minimum 5 characters)'})
        
        if listing_type == 'buy':
            budget = cleaned_data.get('budget')
            if not budget:
                raise forms.ValidationError({'budget': 'Budget is required for buy listings'})
            if budget < 0:
                raise forms.ValidationError({'budget': 'Budget cannot be negative'})
            if budget > 999999.99:
                raise forms.ValidationError({'budget': 'Budget too high (max ₱999,999.99)'})

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