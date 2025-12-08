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

    @classmethod
    def get_categories_dict(cls):
        """Returns structured categories data - single source of truth"""
        return {
            key: {
                'label': label,
                'subcategories': [
                    {'value': sub[0], 'label': sub[1]}
                    for sub in cls.SUBCATEGORY_CHOICES.get(key, [])
                ]
            }
            for key, label in cls.CATEGORY_CHOICES
        }

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
    date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)

    @property
    def main_image(self):
        """Return the main image for this listing"""
        return self.images.filter(is_main=True).first()

    @property
    def category_display(self):
        """Return the display label for the category"""
        return dict(self.CATEGORY_CHOICES).get(self.category, 'Other')

    @property
    def subcategory_display(self):
        """Return the display label for the subcategory"""
        if not self.subcategory or not self.category:
            return None
        
        subcategories = dict(self.SUBCATEGORY_CHOICES.get(self.category, []))
        return subcategories.get(self.subcategory, self.subcategory)

    @property
    def formatted_price(self):
        """Return formatted price with currency symbol"""
        if self.price:
            return f"₱{self.price:,.2f}"
        return None

    @property
    def formatted_budget(self):
        """Return formatted budget with currency symbol"""
        if self.budget:
            return f"₱{self.budget:,.2f}"
        return None

    @property
    def formatted_date(self):
        """Return formatted date as m/d/Y"""
        if self.date:
            return self.date.strftime('%m/%d/%Y')
        return None

    @property
    def image_count(self):
        """Return the number of images for this listing"""
        return self.images.count()

    @property
    def can_add_images(self):
        """Check if more images can be added (max 5)"""
        return self.image_count < 5

    @property
    def remaining_image_slots(self):
        """Return number of remaining image slots"""
        return max(0, 5 - self.image_count)

    def can_edit(self, user):
        """Check if user can edit this listing"""
        return self.user == user

    def can_delete(self, user):
        """Check if user can delete this listing"""
        return self.user == user

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


class ConnectionRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, null=True, help_text='Optional message with the connection request')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['sender', 'receiver']

    def __str__(self):
        return f"{self.sender} -> {self.receiver} ({self.status})"


class Connection(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='connections1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='connections2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user1', 'user2']

    def __str__(self):
        return f"{self.user1} <-> {self.user2}"
