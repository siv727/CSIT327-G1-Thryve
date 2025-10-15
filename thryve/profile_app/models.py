from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

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
