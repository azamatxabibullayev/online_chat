from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import Http404
from .forms import MessageForm, GroupForm
from .models import Chat, Message, Profile


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'users/signup.html', {'form': form})


class LoginView(View):
    def get(self, request):
        login_form = AuthenticationForm()
        context = {
            'form': login_form
        }
        return render(request, 'users/login.html', context=context)

    def post(self, request):
        login_form = AuthenticationForm(data=request.POST)
        if login_form.is_valid():
            user = login_form.get_user()
            login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect('home')
        else:
            context = {
                'form': login_form
            }
            return render(request, 'users/login.html', context=context)


@login_required
def user_logout(request):
    request.user.profile.online = False
    request.user.profile.save()
    logout(request)
    return redirect('home')


@login_required
def chat_list(request):
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)
    chats = Chat.objects.filter(participants=request.user, is_group_chat=False)
    search_query = request.GET.get('q')
    search_results = None
    if search_query:
        search_results = User.objects.filter(username__icontains=search_query).exclude(id=request.user.id)
    return render(request, 'main/chat_list.html', {'chats': chats, 'search_results': search_results})


@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in chat.participants.all():
        return redirect('chat_list')

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = chat.participants.exclude(id=request.user.id).first()
            message.chat = chat
            message.save()
    else:
        form = MessageForm()

    messages = Message.objects.filter(chat=chat)
    other_participant = chat.participants.exclude(id=request.user.id).first()

    return render(request, 'main/chat_detail.html', {
        'chat': chat,
        'messages': messages,
        'other_participant': other_participant,
        'form': form
    })


@login_required
def start_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    if other_user == request.user:
        return redirect('chat_list')
    chat = Chat.objects.filter(participants=request.user).filter(participants=other_user).first()
    if not chat:
        chat = Chat.objects.create()
        chat.participants.set([request.user, other_user])
        chat.save()

    return redirect('chat_detail', chat_id=chat.id)


@login_required
def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/main/groups/')
    else:
        form = GroupForm()
    return render(request, 'main/create_group.html', {'form': form})


@login_required
def group_list(request):
    groups = Group.objects.all()
    return render(request, 'main/group_list.html', {'groups': groups})


@login_required
def add_participant(request, group_id):
    group_chat = get_object_or_404(Chat, id=group_id, is_group_chat=True)
    if request.method == 'POST':
        username = request.POST.get('username')
        user = get_object_or_404(User, username=username)
        if user != request.user:
            group_chat.participants.add(user)
    return redirect('group_chat_detail', group_id=group_chat.id)


@login_required
def group_chat_detail(request, group_id):
    group = get_object_or_404(Chat, id=group_id)
    messages = group.messages.all()

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.group = group
            message.save()
            form.save_m2m()
            return redirect('group_chat_detail', group_id=group.id)
    else:
        form = MessageForm()

    return render(request, 'main/group_chat_detail.html', {
        'group': group,
        'messages': messages,
        'form': form
    })


@login_required
def delete_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in chat.participants.all():
        return redirect('chat_list')

    if request.method == "POST":
        if 'delete_for_me' in request.POST:
            chat.participants.remove(request.user)
            if chat.participants.count() == 0:
                chat.delete()
            return redirect('chat_list')
        elif 'delete_for_both' in request.POST:
            chat.delete()
            return redirect('chat_list')
        elif 'cancel' in request.POST:
            return redirect('chat_detail', chat_id=chat.id)
    return render(request, 'main/confirm_delete.html', {'chat': chat})


def home(request):
    return render(request, 'home.html')


def handler404(request, exception):
    return render(request, '404.html', status=404)
