# community_app/forms.py

from django import forms
from .models import CommunityPost, Comment # Import the new Comment model

## 1. Form for Creating a New Community Post
class CommunityPostForm(forms.ModelForm):
    class Meta:
        model = CommunityPost
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': "Share experiences and connect with other SMEs..."
            }),
        }
        labels = {
            'content': '', # Hides the default label
        }

# --- NEW FORM: CommentForm ---
class CommentForm(forms.ModelForm):
    """Form to handle the submission of a comment."""
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 1,
                'placeholder': "Add a comment...",
                'class': "form-control form-control-sm", # Apply initial styling
            }),
        }
        labels = {
            'content': '',
        }
# -----------------------------