# community_app/forms.py
from django import forms
from .models import CommunityPost 

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
