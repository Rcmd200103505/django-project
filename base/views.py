from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.http import Http404, JsonResponse, HttpResponseBadRequest
from .models import Task
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib import messages
from .forms import UserUpdateForm, ProfileUpdateForm, UserRegisterForm
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post
from .models import Document
from .models import Room, Message


class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')


class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(title__startswith=search_input)

            context['search_input'] = search_input

        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'


def task_create(request):
    title = request.POST['title']
    desc = request.POST['description']
    created = request.POST['created']
    if title and desc:
        if request.POST['deadline']:
            deadline = request.POST['deadline']
            task_obj = Task(title=title, description=desc, user=request.user, deadline=deadline, created=created)
        else:
            task_obj = Task(title=title, description=desc, user=request.user, created=created)
        status = 'success'
        try:
            task_obj.save()
        except Exception as e:
            return HttpResponseBadRequest(e)
        response_data = {
            'status': status
        }
        return JsonResponse(response_data)
    return JsonResponse({'status': 'invalid request'})


from enum import Enum
from datetime import datetime
from django.utils.timezone import make_aware
from calendar import monthrange
import calendar


class Months(Enum):
    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12


def get_tasks_for_day(day, user=None):
    if not user:
        return [
            {'task': task,
             'deadline': task.deadline.day == day.day
             } for task in Task.objects.filter(deadline__gte=day,
                                               created__lte=day)]
    return [
        {'task': task,
         'deadline': task.deadline.day == day.day
         } for task in Task.objects.filter(deadline__gte=day,
                                           created__lte=day, user=user)]


def task_calendar(request, year, month):
    month_dt = monthrange(year, month)
    start_weekday = month_dt[0]
    num_of_days = month_dt[1]
    context = {
        'start_weekday': start_weekday,
        'days': [
            {
                'tasks': get_tasks_for_day(datetime(year, month, i + 1), user=request.user),
                'day': datetime(year, month, i + 1),
            } for i in range(num_of_days)
        ],
        'month': datetime(year, month, 1).strftime('%B'),
        'next_month': {'month': month + 1 if month < 12 else 1, 'year': year if month < 12 else year + 1},
        'prev_month': {'month': month - 1 if month > 1 else 12, 'year': year if month > 1 else year - 1},
        'year': year,
    }
    # print(context)
    return render(request, 'base/task_calendar.html', context)


def calendar_current_month(request):
    dt = datetime.now()
    year = dt.year
    month = dt.month
    month_dt = monthrange(year, month)
    start_weekday = month_dt[0]
    num_of_days = month_dt[1]
    # print(request.user)
    context = {
        'start_weekday': start_weekday,
        'days': [
            {
                'tasks': get_tasks_for_day(datetime(year, month, i + 1), user=request.user),
                'day': datetime(year, month, i + 1),
            } for i in range(num_of_days)
        ],
        'month': dt.strftime('%B'),
        'next_month': {'month': month + 1 if month < 12 else 1, 'year': year if month < 12 else year + 1},
        'prev_month': {'month': month - 1 if month > 1 else 12, 'year': year if month > 1 else year - 1},
        'year': year,
    }
    # print(context)
    return render(request, 'base/task_calendar.html', context)


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'created', 'deadline']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'created', 'deadline', 'complete']
    success_url = reverse_lazy('tasks')


class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')


def check_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        print('-----task object obtained-----')
        task.complete = not task.complete
        print('-----task object is to be saved-----')
        print(task)
        task.save()
        response_data = {
            'complete': task.complete
        }
        return JsonResponse(response_data)
    except Exception as e:
        print(e)
        raise Http404('Task not found')


def get_task_ajax(request, task_id):
    task = Task.objects.get(id=task_id)
    response_data = {
        'title': task.title,
        'description': task.description,
        'deadline': task.deadline,
        'created': task.created,
    }
    return JsonResponse(response_data)


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'base/profile.html', context)


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'base/register.html', {'form': form})


def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'base/posts.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'base/posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']


class PostDetailView(DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about(request):
    return render(request, 'base/about.html', {'title': 'About'})


def editor(request):
    docid = int(request.GET.get('docid', 0))
    documents = Document.objects.all()

    if request.method == 'POST':
        docid = int(request.POST.get('docid', 0))
        title = request.POST.get('title')
        content = request.POST.get('content', '')

        if docid > 0:
            document = Document.objects.get(pk=docid)
            document.title = title
            document.content = content
            document.save()

            return redirect('editor')
        else:
            document = Document.objects.create(title=title, content=content)

    if docid > 0:
        document = Document.objects.get(pk=docid)
    else:
        document = ''
    context = {
        'docid': docid,
        'documents': documents,
        'document': document
    }

    return render(request, 'base/editor.html', context)


def delete_document(request, docid):
    document = Document.objects.get(pk=docid)
    document.delete()

    return redirect('editor')


def home(request):
    return render(request, 'base/home.html')


def room(request, room):
    username = request.GET.get('username')
    room_details = Room.objects.get(name=room)
    return render(request, 'base/room.html', {
        'username': username,
        'room': room,
        'room_details': room_details
    })


def checkview(request):
    room = request.POST['room_name']
    username = request.POST['username']

    if Room.objects.filter(name=room).exists():
        return redirect('/'+room + '/?username=' + username)
    else:
        new_room = Room.objects.create(name=room)
        new_room.save()
        return redirect('/'+room + '/?username=' + username)


def send(request):
    message = request.POST['message']
    username = request.POST['username']
    room_id = request.POST['room_id']

    new_message = Message.objects.create(value=message, user=username, room=room_id)
    new_message.save()
    return HttpResponse('Message sent successfully')


def getMessages(request, room):
    room_details = Room.objects.get(name=room)

    messages = Message.objects.filter(room=room_details.id)
    return JsonResponse({"messages": list(messages.values())})
