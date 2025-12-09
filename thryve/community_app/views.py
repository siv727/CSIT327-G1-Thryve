# community_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden 
from .forms import CommunityPostForm, CommentForm 
from .models import CommunityPost, PostLike, Comment 

# -----------------------------------------------------------
# CHANGE 1: Added login_url='login' to community_feed
@login_required(login_url='login')
def community_feed(request):
    """Displays the community feed page."""
    
    # Pre-fetch comments to reduce database queries (N+1 problem)
    posts = CommunityPost.objects.all().select_related('user__userprofile').prefetch_related('comments__user__userprofile')
    form = CommunityPostForm()
    comment_form = CommentForm() 
    
    # Determine which posts the current user has liked
    liked_posts_ids = []
    if request.user.is_authenticated:
        liked_posts_ids = PostLike.objects.filter(
            user=request.user, 
            post__in=posts
        ).values_list('post_id', flat=True)

    context = {
        'posts': posts,
        'form': form,
        'comment_form': comment_form, 
        'liked_posts_ids': list(liked_posts_ids),
        'user': request.user, # Explicitly pass the user for the template condition
    }
    return render(request, 'community_app/community.html', context)

# -----------------------------------------------------------
# CHANGE 2: Added login_url='login' to create_community_post
@login_required(login_url='login')
def create_community_post(request):
    """Handles the form submission for creating a new post."""
    if request.method == 'POST':
        form = CommunityPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('community_app:community_feed')
    
    return redirect('community_app:community_feed')


# -----------------------------------------------------------
# CHANGE 3: Added login_url='login' to toggle_post_like
@login_required(login_url='login')
def toggle_post_like(request, post_id):
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


# -----------------------------------------------------------
# CHANGE 4: Added login_url='login' to delete_community_post
@login_required(login_url='login')
def delete_community_post(request, post_id):
    """Deletes a community post if the user is the author (via AJAX)."""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        post = get_object_or_404(CommunityPost, id=post_id)
        
        # CRITICAL: Check if the current user is the author of the post
        if post.user != request.user:
            return JsonResponse({
                'status': 'error',
                'message': 'You are not authorized to delete this post.'
            }, status=403)

        post.delete()
        
        return JsonResponse({'status': 'success', 'message': 'Post deleted successfully.'})
    
    return HttpResponseBadRequest("Invalid request.")


# -----------------------------------------------------------
# CHANGE 5: Added login_url='login' to add_comment
@login_required(login_url='login')
def add_comment(request, post_id):
    """Handles adding a new comment via an AJAX POST request."""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        post = get_object_or_404(CommunityPost, id=post_id)
        
        form = CommentForm(request.POST) 
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()

            user_full_name = f"{request.user.first_name} {request.user.last_name}"
            # NEW: Use display_name if available
            if hasattr(request.user, 'userprofile') and request.user.userprofile.display_name:
                user_full_name = request.user.userprofile.display_name
            try:
                business_name = request.user.businessprofile.company_name
            except AttributeError:
                business_name = "SME User" 
            
            # NOTE: We now return comment.id (comment.pk) for the frontend delete function
            return JsonResponse({
                'status': 'success',
                'comment_id': comment.pk, 
                'new_count': post.comments_count, 
                'content': comment.content,
                'user_display_name': user_full_name,
                'business_name': business_name,
                'created_at': comment.created_at.strftime("%#m/%#d/%Y"), 
            })
        else:
            return JsonResponse({
                'status': 'error', 
                'message': dict(form.errors), 
                'post_id': post_id
            }, status=400)
    
    return HttpResponseBadRequest("Invalid request.")


# -----------------------------------------------------------
# CHANGE 6: Added login_url='login' to delete_comment
@login_required(login_url='login')
def delete_comment(request, post_id, comment_id):
    """Deletes a comment if the user is the author (via AJAX)."""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Retrieve the specific comment, ensuring it belongs to the post_id 
        comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
        
        # CRITICAL: Check if the current user is the author of the comment
        if comment.user != request.user:
            return JsonResponse({
                'status': 'error',
                'message': 'You are not authorized to delete this comment.'
            }, status=403) # 403 Forbidden

        comment.delete()
        
        return JsonResponse({'status': 'success', 'message': 'Comment deleted successfully.'})
    
    return HttpResponseBadRequest("Invalid request.")