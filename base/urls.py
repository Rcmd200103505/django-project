from django.urls import path
from .views import TaskList, TaskDetail, TaskCreate, TaskUpdate, DeleteView, CustomLoginView, RegisterPage
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
)
from . import views

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
    path('', TaskList.as_view(), name='tasks'),
    path('task/<int:pk>/', TaskDetail.as_view(), name='task'),
    path('task-create/', TaskCreate.as_view(), name='task-create'),
    path('task-update/<int:pk>/', TaskUpdate.as_view(), name='task-update'),
    path('task-delete/<int:pk>/', DeleteView.as_view(), name='task-delete'),
    path('check_task/<int:task_id>', views.check_task, name="check_task"),
    path('task-create-ajax', views.task_create, name="task-create-ajax"),
    path('task-calendar', views.calendar_current_month, name='task-calendar-current'),
    path('task-calendar/<int:year>/<int:month>', views.task_calendar, name='task-calendar'),
    path('get-task-ajax/<int:task_id>', views.get_task_ajax, name='get-task-ajax'),
    path('profile/', views.profile, name='profile'),
    path('posts', PostListView.as_view(), name='blog-home'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('about/', views.about, name='blog-about'),
    path('editor/', views.editor, name='editor'),
    path('delete_document/<int:docid>/', views.delete_document, name='delete_document'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

