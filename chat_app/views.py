from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import ChatMessage

@login_required
def client_chat(request):
    admin_user = User.objects.get(username='clinton')  # Ensure 'admin' username exists in your database
    client_user = request.user

    # Fetch chat messages between the client and the admin
    chat_messages = ChatMessage.objects.filter(
        sender__in=[client_user, admin_user],
        recipient__in=[client_user, admin_user]
    ).order_by('timestamp')

    if request.method == 'POST':
        # Save new message from the client
        message_content = request.POST.get('message')
        ChatMessage.objects.create(sender=client_user, recipient=admin_user, message=message_content)
        return redirect('client_chat')  # Reload page to show the new message
    print('heree kdjfkajdkf')
    return render(request, 'chat_app/client.html', {'messages': chat_messages, 'admin_user': admin_user})


@login_required
def admin_chat(request):
    admin_user = request.user

    # Fetch all unique clients who have sent messages to the admin
    clients = ChatMessage.objects.filter(recipient=admin_user).values('sender').distinct()

    selected_client = request.GET.get('client')
    chat_messages = []
    print('clients', clients)
    
    if selected_client:
        # Fetch messages for the selected client
        selected_user = User.objects.get(id=selected_client)
        chat_messages = ChatMessage.objects.filter(
            sender__in=[selected_user, admin_user],
            recipient__in=[selected_user, admin_user]
        ).order_by('timestamp')

        if request.method == 'POST':
            # Save new message from the admin
            message_content = request.POST.get('message')
            ChatMessage.objects.create(sender=admin_user, recipient=selected_user, message=message_content)
            return redirect(f'{request.path}?client={selected_client}')  # Reload page with the same client
    print('msgs: ', chat_messages)
    return render(request, 'chat_app/admin_chat.html', {'clients': clients, 'messages': chat_messages})






from django.http import JsonResponse
from django.shortcuts import get_object_or_404


@login_required
def get_chat_messages(request):
    username = request.GET.get('username')
    admin_user = User.objects.get(username='clinton')  # Admin username
    client_user = get_object_or_404(User, username=username)

    # Fetch chat messages between admin and the client
    chat_messages = ChatMessage.objects.filter(
        sender__in=[admin_user, client_user],
        recipient__in=[admin_user, client_user]
    ).order_by('timestamp')

    # Serialize chat messages
    messages = [{
        'message': chat.message,
        'timestamp': chat.timestamp.strftime('%Y-%m-%d %H:%M'),
        'sender_is_admin': chat.sender == admin_user,
    } for chat in chat_messages]

    return JsonResponse({'messages': messages})














from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import SignUpForm, LoginForm

# Signup View
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log the user in after signup
            messages.success(request, f"Account created for {user.username}!")
            return redirect('client_chat')  # Redirect to chat page or any other page
    else:
        form = SignUpForm()

    return render(request, 'chat_app/signup.html', {'form': form})

# Login View
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back {user.username}!")
            return redirect('client_chat')  # Redirect to chat page or any other page
        else:
            messages.error(request, "Invalid login credentials.")
    else:
        form = LoginForm()

    return render(request, 'chat_app/login.html', {'form': form})

# Logout View
from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logging out











from django.db.models import Max, Q

@login_required
def admin_chat(request):
    admin_user = request.user

    # Fetch the latest message for each client who has sent or received messages with the admin
    latest_messages = (
        ChatMessage.objects.filter(Q(sender=admin_user) | Q(recipient=admin_user))
        .values('sender', 'recipient')
        .annotate(latest_timestamp=Max('timestamp'))
    )

    print('here', latest_messages)

    # Organize latest messages into new and delivered categories
    new_messages = []
    delivered_messages = []

    for msg in latest_messages:
        # Determine the client (not the admin user)
        if msg['sender'] == admin_user.id:
            client_id = msg['recipient']
        else:
            client_id = msg['sender']

        # Fetch the actual message object
        latest_message = ChatMessage.objects.filter(
            Q(sender_id=client_id, recipient=admin_user) |
            Q(sender=admin_user, recipient_id=client_id),
            timestamp=msg['latest_timestamp']
        ).first()

        # Categorize based on message status
        if latest_message.status == 'new':
            new_messages.append(latest_message)
        else:
            delivered_messages.append(latest_message)

    # Optionally sort messages by timestamp
    new_messages.sort(key=lambda x: x.timestamp, reverse=True)
    delivered_messages.sort(key=lambda x: x.timestamp, reverse=True)

    selected_client = request.GET.get('client')
    chat_messages = []

    if selected_client:
        # Fetch messages for the selected client
        selected_user = User.objects.get(id=selected_client)
        chat_messages = ChatMessage.objects.filter(
            sender__in=[selected_user, admin_user],
            recipient__in=[selected_user, admin_user]
        ).order_by('timestamp')

        if request.method == 'POST':
            # Save new message from the admin
            message_content = request.POST.get('message')
            ChatMessage.objects.create(sender=admin_user, recipient=selected_user, message=message_content)
            return redirect(f'{request.path}?client={selected_client}')  # Reload page with the same client

    return render(
        request,
        'chat_app/admin_chat.html',
        {
            'new_messages': new_messages,
            'delivered_messages': delivered_messages,
            'messages': chat_messages,
        }
    )
