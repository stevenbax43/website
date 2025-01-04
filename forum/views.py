from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import Topic, Category, Reply
from .forms import TopicForm, ReplyForm, CategoryForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Check if user is a superuser
def is_superuser(user):
    return user.is_superuser
@login_required(login_url='accounts:login')
def topic_list(request):
    # Get the query parameter to filter topics
    filter_status = request.GET.get('status', 'open')  # Default to 'open' if no filter is applied
    categories = Category.objects.all()
    topics_by_category = {}
    # Loop through each category to get topics based on the filter
    for category in categories:
        if filter_status == 'closed':
            # Get only closed topics for this category
            topics = Topic.objects.filter(category=category)
        else:
            # Get only open topics for this category (default behavior)
            topics = Topic.objects.filter(category=category, is_closed=False)
        
        # Only include categories that have topics
        if topics.exists():
            topics_by_category[category] = topics
    
    # Pass the filtered topics and filter status to the template
    return render(request, 'forum/topic_list.html', {
        'topics_by_category': topics_by_category,
        'filter_status': filter_status,
    })
@login_required(login_url='accounts:login')
def topic_detail(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    replies = Reply.objects.filter(topic=topic, parent_reply__isnull=True)  # Top-level replies
    categories = Category.objects.first()
    # Handle closing the conversation if the user is the creator
    if request.method == 'POST' and 'close_conversation' in request.POST:
        if request.user == topic.created_by:
            topic.is_closed = True
            topic.save()
            messages.success(request, "The conversation has been closed successfully.")
        else:
            messages.error(request, "You are not authorized to close this conversation.")
        return redirect('forum:topic_detail', pk=topic.pk)
    # Handle replies only if the topic is open
    if request.method == 'POST' and not topic.is_closed:
        form = ReplyForm(request.POST, request.FILES)  
        if form.is_valid():
            reply = form.save(commit=False)
            reply.topic = topic
            reply.created_by = request.user
            reply.save()
            return redirect('forum:topic_detail', pk=topic.pk)
    else:
        form = ReplyForm()

    return render(request, 'forum/topic_detail.html', 
                  {'topic': topic, 'replies': replies, 'form': form, 'categories':categories}
                  )
@login_required(login_url='accounts:login')
def create_topic(request):
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.created_by = request.user
            topic.save()
            return redirect('forum:topic_list')
    else:
        form = TopicForm()
    return render(request, 'forum/create_topic.html', {'form': form})
@login_required(login_url='accounts:login')
def delete_reply(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    
    # Check if the user is the creator of the reply
    if reply.created_by == request.user:
        reply.delete()
        return redirect('forum:topic_detail', pk=reply.topic.pk)
    else:
        return render(request, '403.html')  # Optional: Handle unauthorized access
@login_required(login_url='accounts:login')
def reply_to_reply(request, pk):
    print('reply-to-reply')
    parent_reply = get_object_or_404(Reply, pk=pk)
    topic = parent_reply.topic
    if request.method == 'POST':
        form = ReplyForm(request.POST, request.FILES)
        if form.is_valid():
            new_reply = form.save(commit=False)
            new_reply.created_by = request.user
            new_reply.parent_reply = parent_reply
            new_reply.topic = topic
            new_reply.save()
            messages.success(request, 'Your reply has been posted.')
            return redirect('forum:topic_detail', pk=topic.pk)
    else:
        form = ReplyForm()

    return render(request, 'forum/reply_form.html', {'form': form, 'parent_reply': parent_reply})

@user_passes_test(is_superuser)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('forum:topic_list')  # Redirect to a list view or success page
    else:
        form = CategoryForm()
    return render(request, 'forum/add_category.html', {'form': form})

@user_passes_test(is_superuser)
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect('forum:topic_list')  # Redirect to a list view or success page
    else:
        form = CategoryForm(instance=category)
    return render(request, 'forum/edit_category.html', {'form': form, 'category': category})

