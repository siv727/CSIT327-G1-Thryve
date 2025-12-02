from django import forms
from django.core.exceptions import ValidationError
from thryve_app.models import Listing


def validate_images_count(files, existing_count=0):
    total_count = len(files) + existing_count
    if total_count > 5:
        raise ValidationError(
            f'Maximum 5 images allowed. You have {existing_count} existing images and are trying to add {len(files)} more.')
    return True


def validate_image_file(image):
    max_size = 5 * 1024 * 1024  # 5MB
    if image.size > max_size:
        raise ValidationError(f'Image "{image.name}" is too large. Maximum size is 5MB.')

    valid_formats = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if hasattr(image, 'content_type'):
        if image.content_type not in valid_formats:
            raise ValidationError(
                f'Unsupported format for "{image.name}". Please upload JPEG, PNG, GIF, or WebP images.')
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

    class Meta:
        model = Listing
        fields = ['listing_type', 'title', 'description', 'price', 'swap_for', 'budget', 'location', 'date']
        widgets = {
            'listing_type': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky placeholder:text-slate-400'}),
            'title': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky placeholder:text-slate-400',
                'placeholder': 'Enter listing title'}),
            'description': forms.Textarea(attrs={
                'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky resize-none',
                'rows': 4, 'placeholder': 'Describe your item or service'}),
            'price': forms.NumberInput(attrs={
                'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky placeholder:text-slate-400',
                'placeholder': '0.00', 'step': '0.01'}),
            'location': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky placeholder:text-slate-400',
                'placeholder': 'City, State/Country'}),
            'date': forms.DateInput(attrs={
                'class': 'w-full rounded-lg border border-slate-200 px-3 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-brand-sky placeholder:text-slate-400',
                'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'category' in self.fields:
            del self.fields['category']
        self.fields['listing_type'].required = True
        self.fields['title'].required = True
        self.fields['description'].required = True
        self.fields['location'].required = True
        self.fields['date'].required = True

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description:
            description = ' '.join(description.split())
            if len(description) > 5000:
                raise forms.ValidationError('Description too long (max 5000 characters)')
            if len(description.strip()) < 10:
                raise forms.ValidationError('Description is too short (minimum 10 characters)')
        return description

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date:
            from datetime import date as dt_date
            if date < dt_date.today():
                raise forms.ValidationError('Date cannot be in the past')
        return date

    def clean(self):
        cleaned_data = super().clean()
        listing_type = cleaned_data.get('listing_type')

        if listing_type == 'sale':
            price = cleaned_data.get('price')
            if not price:
                raise forms.ValidationError({'price': 'Price is required for sale listings'})
            if price < 0:
                raise forms.ValidationError({'price': 'Price cannot be negative'})

        if listing_type == 'swap':
            swap_for = cleaned_data.get('swap_for')
            if not swap_for or len(swap_for.strip()) == 0:
                raise forms.ValidationError({'swap_for': 'Swap details are required for swap listings'})

        if listing_type == 'buy':
            budget = cleaned_data.get('budget')
            if not budget:
                raise forms.ValidationError({'budget': 'Budget is required for buy listings'})
            if budget < 0:
                raise forms.ValidationError({'budget': 'Budget cannot be negative'})

        if hasattr(self, 'data') and 'category' in self.data:
            category_value = self.data.get('category', '')
            if not category_value:
                raise forms.ValidationError("Please select a category")

        return cleaned_data