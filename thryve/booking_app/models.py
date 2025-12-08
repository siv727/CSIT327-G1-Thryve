from django.db import models
from django.conf import settings
from thryve_app.models import Listing

class BookingRequest(models.Model):
    # This listing is the item/service the user is trying to "Book"
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='booking_requests')

    # User who is sending the request (the one clicking "Book Now")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_bookings')

    # User who owns the listing (the one receiving the request)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_bookings')

    # Data derived from the modal
    proposed_start_date = models.DateField()
    proposed_end_date = models.DateField()
    message = models.TextField(blank=True, null=True, help_text="Message from the sender.")

    # Status to track negotiation/transaction process
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('completed', 'Completed')
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking Request for {self.listing.title} from {self.sender.email}"

    class Meta:
        # A sender can only have one pending request for a single listing at a time
        unique_together = ('listing', 'sender', 'status')
        constraints = [
            models.UniqueConstraint(fields=['listing', 'sender'], condition=models.Q(status='pending'), name='unique_pending_booking')
        ]
