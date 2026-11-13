from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import os, re, nltk,json
from openai import OpenAI
from .models import Conversation, SingleUserBot
from dotenv import load_dotenv
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
# Load environment variables from .env
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config/settings/.env')
load_dotenv(dotenv_path)

# # Download NLTK data for title stopwords
# nltk.download('punkt')
# nltk.download('stopwords')
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

@login_required(login_url='accounts:login')
def chatbot(request, pk):
   # Retrieve all conversations associated with the current user
    conversations = Conversation.objects.filter(user=request.user).order_by('-created_at')
    print(request.user.first_name)
    # Get the selected conversation based on the pk passed in the URL
    selected_conversation = get_object_or_404(Conversation, id=pk, user=request.user)
    
    # Retrieve the user-bot responses associated with the selected conversation
    user_bot_responses = SingleUserBot.objects.filter(user=request.user, parent=selected_conversation)

     # Handle POST request to create a new bot response
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '')
        #print(f"User input: {user_input}")
        
        response = generate_openai_response(request.user, user_input, pk)
        
        if selected_conversation:
            single_user_bot = SingleUserBot(
                user=request.user,
                user_input=user_input,
                bot_response=response,
                created_at=timezone.now(),
                parent=selected_conversation,
            )
            single_user_bot.save()
      
        else:
            print("Error: No selected conversation to associate with SingleUserBot entry.")
        
        return JsonResponse({'response': response})
    
    return render(request, 'chat/chatbot.html', {
        'conversations': conversations,
        'user_bot_responses': user_bot_responses,
        'selected_conversation': selected_conversation
    })

def conversation_detail(request, id):
    conversation = get_object_or_404(Conversation, id=id)
    # Render a template with the conversation details
    #print(id)
    return render(request, 'chat/chatbot.html', {'conversation': conversation})

@login_required(login_url='accounts:login')
def create_new_chat(request):
    conversations = Conversation.objects.filter(user=request.user)
    return render(request, 'chat/chatbot_start.html',  {'conversations': conversations})

@csrf_exempt
def process_input(request):
   
    if request.method == 'POST':
        data = json.loads(request.body)
        user_input = data.get('input', '')
        #print(user_input)
        # Pak het eerste woord van de input
        first_word = user_input.split()[0] if user_input else ''
        New_conversation = Conversation(
            user = request.user,
            title= first_word,
            created_at = timezone.now()
        )
        New_conversation.save()
        #
        selected_conversation = get_object_or_404(Conversation, id=New_conversation.pk, user=request.user)
        #create botresponse and save with newly created conversation
        response = generate_openai_response(request.user, user_input, pk=None)
        single_user_bot = SingleUserBot(
                user=request.user,
                user_input=user_input,
                bot_response=response,
                created_at=timezone.now(),
                parent=selected_conversation,
            )
        single_user_bot.save()
        
        return JsonResponse({'redirect_url': f'/chatbot/{New_conversation.pk}/'})
    
OPENAI_API_URL = 'https://api.openai.com/v1/engines/davinci/completions'

def generate_openai_response(user, user_input, pk=None, max_history=5):
    conversation_log = []

    if pk is not None:  # Als er niet al een gesprek hiervoor is gemaakt.
        previous_conversations = SingleUserBot.objects.filter(user=user, id=pk).order_by('created_at')[:max_history]

        for conv in previous_conversations:
            conversation_log.append({"role": "user", "content": conv.user_input})
            conversation_log.append({"role": "assistant", "content": conv.bot_response})

    # Voeg de nieuwe gebruikersinvoer toe, ongeacht of pk None is
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

@require_POST
def delete_specific_conversation(request, pk):
    # Delete all instances of Conversation
    conversation = get_object_or_404(Conversation, user=request.user, id=pk)
    conversation.delete()
    return redirect('chat:create_new_conversation')


# def generate_title_from_input(user_input):
#     stop_words = set(stopwords.words('dutch'))
#     word_tokens = word_tokenize(user_input.lower(), language='dutch')
    
#     # Remove stop words and non-alphabetic words
#     filtered_words = [word for word in word_tokens if word.isalpha() and word not in stop_words]
    
#     # Join the first 2-3 significant words to create a title
#     title = ' '.join(filtered_words[:3])
    
#     return title.capitalize()