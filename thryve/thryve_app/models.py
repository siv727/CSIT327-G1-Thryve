from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

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
        ('other', 'Other'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPE_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    swap_for = models.TextField(null=True, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    your_name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    image = models.ImageField(
        upload_to='listings/',
        blank=True,
        null=True,
        validators=[validate_listing_image_size, validate_listing_image_format],
        help_text='Upload a listing image (max 5MB, JPEG/PNG/GIF/WebP only)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.title
