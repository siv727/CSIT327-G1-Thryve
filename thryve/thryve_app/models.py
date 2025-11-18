from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

def validate_listing_image_size(image):
    """Validate that uploaded image is under 5MB"""
    max_size = 5 * 1024 * 1024  # 5MB in bytes
    if image.size > max_size:
        raise ValidationError('Image file too large. Size should not exceed 5MB.')

def validate_listing_image_format(image):
    """Validate that uploaded file is an image"""
    valid_formats = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if hasattr(image, 'content_type') and image.content_type not in valid_formats:
        raise ValidationError('Unsupported file format. Please upload a JPEG, PNG, GIF, or WebP image.')

class Listing(models.Model):
    LISTING_TYPE_CHOICES = [
        ('sale', 'For Sale'),
        ('swap', 'For Swap'),
        ('buy', 'Looking to Buy'),
    ]

    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('furniture', 'Furniture'),
        ('tools_equipment', 'Tools & Equipment'),
        ('raw_materials', 'Raw Materials'),
        ('services', 'Services'),
        ('other', 'Other'),
    ]

    SUBCATEGORY_CHOICES = {
        'electronics': [
            ('computers', 'Computers'),
            ('phones', 'Phones'),
            ('tablets', 'Tablets'),
            ('audio_video', 'Audio/Video Equipment'),
            ('cameras', 'Cameras'),
            ('other_electronics', 'Other Electronics'),
        ],
        'furniture': [
            ('office_chairs', 'Office Chairs'),
            ('desks', 'Desks'),
            ('cabinets', 'Cabinets'),
            ('tables', 'Tables'),
            ('seating', 'Seating'),
            ('other_furniture', 'Other Furniture'),
        ],
        'tools_equipment': [
            ('power_tools', 'Power Tools'),
            ('hand_tools', 'Hand Tools'),
            ('machinery', 'Machinery'),
            ('safety_equipment', 'Safety Equipment'),
            ('measuring_tools', 'Measuring Tools'),
            ('other_tools', 'Other Tools & Equipment'),
        ],
        'raw_materials': [
            ('metals', 'Metals'),
            ('plastics', 'Plastics'),
            ('woods', 'Woods'),
            ('chemicals', 'Chemicals'),
            ('fabrics', 'Fabrics'),
            ('other_materials', 'Other Raw Materials'),
        ],
        'services': [
            ('consulting', 'Consulting'),
            ('maintenance', 'Maintenance'),
            ('installation', 'Installation'),
            ('training', 'Training'),
            ('design', 'Design'),
            ('other_services', 'Other Services'),
        ],
        'other': [
            ('miscellaneous', 'Miscellaneous'),
        ],
    }

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPE_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    subcategory = models.CharField(max_length=30, blank=True, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()

    def save(self, *args, **kwargs):
        # Sanitize HTML content to prevent XSS attacks
        if self.description:
            # Allow only safe tags and attributes
            allowed_tags = ['p', 'br', 'strong', 'em', 'b', 'i', 'ul', 'ol', 'li', 'a']
        super().save(*args, **kwargs)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    swap_for = models.TextField(null=True, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    your_name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)

    @property
    def main_image(self):
        """Return the main image for this listing"""
        return self.images.filter(is_main=True).first()

    def __str__(self):
        return self.title


class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='listings/',
        validators=[validate_listing_image_size, validate_listing_image_format],
        help_text='Upload a listing image (max 5MB, JPEG/PNG/GIF/WebP only)'
    )
    is_main = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_main', 'uploaded_at']

    def __str__(self):
        return f"Image for {self.listing.title}"

    def save(self, *args, **kwargs):
        # Ensure only one main image per listing
        if self.is_main:
            ListingImage.objects.filter(listing=self.listing, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)
