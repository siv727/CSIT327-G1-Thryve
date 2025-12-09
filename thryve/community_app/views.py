# community_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
# Import the new models and forms
from .forms import CommunityPostForm, CommentForm 
from .models import CommunityPost, PostLike, Comment 
# Make sure to import Comment

@login_required
def community_feed(request):
    """Displays the community feed page."""
    
    # Pre-fetch comments to reduce database queries (N+1 problem)
    posts = CommunityPost.objects.all().select_related('user').prefetch_related('comments__user')
    form = CommunityPostForm()
    comment_form = CommentForm() # Initialize the CommentForm
    
    # 2. Determine which posts the current user has liked
    liked_posts_ids = []
    if request.user.is_authenticated:
        liked_posts_ids = PostLike.objects.filter(
            user=request.user, 
            post__in=posts
        ).values_list('post_id', flat=True)

    context = {
        'posts': posts,
        'form': form,
        'comment_form': comment_form, # Add the comment form to context
        'liked_posts_ids': list(liked_posts_ids),
    }
    return render(request, 'community_app/community.html', context)

@login_required
def create_community_post(request):
    # ... (existing code for creating post) ...
    """Handles the form submission for creating a new post."""
    if request.method == 'POST':
        form = CommunityPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('community_app:community_feed')
    
    return redirect('community_app:community_feed')


@login_required
def toggle_post_like(request, post_id):
    # ... (existing code for toggling like) ...
    """Toggles a like on a post (handled via AJAX)."""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        post = get_object_or_404(CommunityPost, id=post_id)
        
        like, created = PostLike.objects.get_or_create(post=post, user=request.user)
        
        if created:
            action = 'liked'
        else:
            like.delete()
            action = 'unliked'
        
        return JsonResponse({
            'status': 'success',
            'action': action,
            'new_count': post.likes_count 
        })
    return HttpResponseBadRequest("Invalid request.")


# --- NEW VIEW: Add Comment ---
@login_required
def add_comment(request, post_id):
    """Handles adding a new comment via an AJAX POST request."""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        post = get_object_or_404(CommunityPost, id=post_id)
        
        # Use the CommentForm to validate content
        form = CommentForm(request.POST) 
        
        if form.is_valid():
            # Create and save the new comment
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()

            # Get user and business name for display in the client
            user_full_name = f"{request.user.first_name} {request.user.last_name}"
            # Safely get the company name (assuming user has a related businessprofile)
            try:
                business_name = request.user.businessprofile.company_name
            except AttributeError:
                business_name = "SME User" 
            
            # Prepare the data to return to the client
            return JsonResponse({
                'status': 'success',
                'new_count': post.comments_count, # Use the model property for count
                'content': comment.content,
                'user_full_name': user_full_name,
                'business_name': business_name,
                'created_at': comment.created_at.strftime("%#m/%#d/%Y"), 
            })
        else:
            # Return form errors if validation fails
            return JsonResponse({
                'status': 'error', 
                'message': dict(form.errors), 
                'post_id': post_id
            }, status=400)
    
    return HttpResponseBadRequest("Invalid request.")
# -----------------------------