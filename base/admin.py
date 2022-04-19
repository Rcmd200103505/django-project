from django.contrib import admin
from .models import Task
from .models import Profile

admin.site.register(Task)
admin.site.register(Profile)
