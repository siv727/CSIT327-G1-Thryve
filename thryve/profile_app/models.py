from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class BusinessProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True, null=True)
    street_address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    website_url = models.URLField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    contact_email = models.EmailField(blank=True)
    logo = models.ImageField(
        upload_to='business_logo/',
        blank=True,
        null=True,
        max_length=200,
        help_text='Upload business logo (recommended <5MB)'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}'s business profile"


def validate_image_size(image):
    """Validate that uploaded image is under 5MB"""
    max_size = 5 * 1024 * 1024  # 5MB in bytes
    if image.size > max_size:
        raise ValidationError('Image file too large. Size should not exceed 5MB.')

def validate_image_format(image):
    """Validate that uploaded file is an image"""
    valid_formats = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if hasattr(image, 'content_type') and image.content_type not in valid_formats:
        raise ValidationError('Unsupported file format. Please upload a JPEG, PNG, GIF, or WebP image.')

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100, blank=True)
    tagline = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        validators=[validate_image_size, validate_image_format],
        help_text='Upload a profile picture (max 5MB, JPEG/PNG/GIF/WebP only)'
    )

    def __str__(self):
        return f"{self.user}'s profile"

    def save(self, *args, **kwargs):
        # Delete old avatar when uploading a new one
        if self.pk:
            old_profile = UserProfile.objects.get(pk=self.pk)
            if old_profile.avatar and self.avatar != old_profile.avatar:
                old_profile.avatar.delete(save=False)
        super().save(*args, **kwargs)
