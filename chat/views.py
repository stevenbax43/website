from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import openai, os
from .models import Conversation
from dotenv import load_dotenv
from django.utils import timezone

# Load environment variables from .env
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config/settings/.env')
load_dotenv(dotenv_path)

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
@login_required(login_url='accounts:login')
def chatbot2(request):
    return render(request, 'chat/chatbot2.html')
# Create your views here.
@login_required(login_url='accounts:login')
def chatbot(request):
    conversations = Conversation.objects.filter(author_id=request.user)
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '')
        response = generate_openai_response(user_input)
        
       
        conversation = Conversation(
            author_id = request.user,
            user_input= user_input,
            bot_response = response,
            created_at = timezone.now()
        )
        conversation.save()
        return JsonResponse({'response': response})
        
    return render(request, 'chat/chatbot.html', {'conversations': conversations})


OPENAI_API_URL = 'https://api.openai.com/v1/engines/davinci/completions'

def generate_openai_response(prompt, max_tokens=100):
    openai.api_key = OPENAI_API_KEY  # Set the OpenAI API key

    # Use the openai.ChatCompletion.create method
    chat_completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens
    )

    return chat_completion['choices'][0]['message']['content'].strip()


def delete_all_conversations(request):
    # Delete all instances of NewsArticle
    Conversation.objects.filter(author_id=request.user).delete()
    # You may also want to delete associated media files, assuming they are stored in the 'news_thumbs' folder

    return redirect('chat:chatbot')