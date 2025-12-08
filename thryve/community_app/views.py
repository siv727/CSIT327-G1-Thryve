# community_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from .forms import CommunityPostForm 
from .models import CommunityPost, PostLike 

@login_required
def community_feed(request):
    """Displays the community feed page."""

    # NOTE: 
    posts = CommunityPost.objects.all().select_related('user')
    form = CommunityPostForm()
    
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
        'liked_posts_ids': list(liked_posts_ids),
    }
    return render(request, 'community_app/community.html', context)

@login_required
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


@login_required
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
