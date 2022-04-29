from django.contrib import admin
from .models import Task
from .models import Profile
from .models import Post
from .models import Document
from .models import Room, Message

admin.site.register(Task)
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Document)
admin.site.register(Room)
admin.site.register(Message)
