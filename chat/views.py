from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import os, re, nltk
from openai import OpenAI
from .models import Conversation, SavedConversation
from dotenv import load_dotenv
from django.utils import timezone

# Load environment variables from .env
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config/settings/.env')
load_dotenv(dotenv_path)

# Download NLTK data for title stopwords
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

#Create your views here.
@login_required(login_url='accounts:login')
def chatbot(request):
    conversations = Conversation.objects.filter(author_id=request.user)
    saved_conversations = SavedConversation.objects.filter(author=request.user)
    
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '')
        response = generate_openai_response(request.user, user_input)
        
       
        conversation = Conversation(
            author_id = request.user,
            user_input= user_input,
            bot_response = response,
            created_at = timezone.now()
        )
        conversation.save()
        return JsonResponse({'response': response})
        
    return render(request, 'chat/chatbot.html', {'conversations': conversations,'saved_conversations': saved_conversations})


OPENAI_API_URL = 'https://api.openai.com/v1/engines/davinci/completions'

def generate_openai_response(user, user_input, max_history=5):
    previous_conversations = Conversation.objects.filter(author_id=user).order_by('created_at')[:max_history]
    conversation_log = []
    for conv in previous_conversations:
            conversation_log.append({"role": "user", "content": conv.user_input})
            conversation_log.append({"role": "assistant", "content": conv.bot_response})

    # Voeg de nieuwe gebruikersinvoer toe
    conversation_log.append({"role": "user", "content": user_input})

    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=OPENAI_API_KEY)

        # Send combined messages to OpenAI for completion
        chat_completion = client.chat.completions.create(
            messages=conversation_log,
            model="gpt-4o",  # Use an appropriate model name
        )
        
         # Extract the completion content from the response
        content = ""
        for choice in chat_completion.choices:
            content += choice.message.content + "\n"  # Concatenate all completions
            

        bot_response = re.sub(r"\*\*(.*?)\*\*", r'<strong>\1</strong>', content.strip()) #alle woorden tussen ** bold maken 
        bot_response2 = re.sub(r"### (\w+)", r'<strong><span style="font-size: larger;">\1</span></strong>', bot_response)
        conversation_log.append({"role": "assistant", "content": bot_response2})

        return bot_response2  # Remove leading/trailing whitespace
    except Exception as e:
        return str(e)


def delete_all_conversations(request):
    # Delete all instances of Conversation
    Conversation.objects.filter(author_id=request.user).delete()

    return redirect('chat:chatbot')

@login_required(login_url='accounts:login')
def save_all_conversations(request):
   
    if request.method == 'POST':
        title = request.POST.get('title', 'Conversation')
        conversations = Conversation.objects.filter(author_id=request.user, saved_conversation__isnull=True)

        if conversations.exists():
            first_user_input = conversations.order_by('created_at').first().user_input
            title = generate_title_from_input(first_user_input)
            saved_conversation = SavedConversation(author=request.user, title=title)
            saved_conversation.save()

            for conv in conversations:
                conv.saved_conversation = saved_conversation
                conv.save()

    return redirect('chat:chatbot')

def generate_title_from_input(user_input):
    stop_words = set(stopwords.words('dutch'))
    word_tokens = word_tokenize(user_input.lower(), language='dutch')
    
    # Remove stop words and non-alphabetic words
    filtered_words = [word for word in word_tokens if word.isalpha() and word not in stop_words]
    
    # Join the first 2-3 significant words to create a title
    title = ' '.join(filtered_words[:3])
    
    return title.capitalize()