# community_app/models.py

from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL 

class CommunityPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_posts')
    content = models.TextField(help_text="The main text content of the post.")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Community Post"
        verbose_name_plural = "Community Posts"

    def __str__(self):
        return f"Post by {self.user.username} - {self.content[:50]}..."

    @property
    def likes_count(self):
        # Count of related PostLike objects
        return self.likes.count()

    # --- NEW PROPERTY: Comment Count ---
    @property
    def comments_count(self):
        # Count of related Comment objects
        return self.comments.count()
    # -----------------------------------


class PostLike(models.Model):
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_posts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensures a user can only like a single post once
        unique_together = ('post', 'user') 
        verbose_name = "Post Like"

    def __str__(self):
        return f"{self.user.username} liked Post {self.post.id}"


# --- NEW MODEL: Comment ---
class Comment(models.Model):
    """Represents a comment on a community post."""
    post = models.ForeignKey(
        CommunityPost, 
        on_delete=models.CASCADE,
        related_name='comments' # Use 'comments' for reverse lookups
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE
    )
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at'] # Display oldest comments first
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f'Comment by {self.user.username} on Post {self.post.id}'
# -----------------------------