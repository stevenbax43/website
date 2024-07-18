from django.shortcuts import render, redirect, get_object_or_404
from .models import Topic, Reply
from .forms import TopicForm, ReplyForm

def topic_list(request):
    topics = Topic.objects.all()
    return render(request, 'forum/topic_list.html', {'topics': topics})

def topic_detail(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    replies = topic.replies.all()

    if request.method == 'POST':
        form = ReplyForm(request.POST, request.FILES)  
        if form.is_valid():
            reply = form.save(commit=False)
            reply.topic = topic
            reply.created_by = request.user
            reply.save()
            return redirect('forum:topic_detail', pk=topic.pk)
    else:
        form = ReplyForm()

    return render(request, 'forum/topic_detail.html', {'topic': topic, 'replies': replies, 'form': form})

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

def delete_reply(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    
    # Check if the user is the creator of the reply
    if reply.created_by == request.user:
        reply.delete()
        return redirect('forum:topic_detail', pk=reply.topic.pk)
    else:
        return render(request, '403.html')  # Optional: Handle unauthorized access