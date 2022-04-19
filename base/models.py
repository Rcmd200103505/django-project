import django.utils.timezone
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, date
from django.utils.timezone import make_aware, is_aware
from PIL import Image

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    complete = models.BooleanField(default=False, null=False)
    created = models.DateTimeField(auto_now_add=False, auto_now=False, blank=True, null=True)
    deadline = models.DateTimeField(auto_now_add=False, auto_now=False, blank=True, null=True)


    def save(self, *args, **kwargs):
        from dateutil import parser
        deadline = parser.parse(str(self.deadline))
        now = datetime.now()

        if not is_aware(deadline):
            deadline = make_aware(deadline)
        if not is_aware(now):
            now = make_aware(now)

        if deadline < now:
            raise ValidationError("The date cannot be in the past!")
        super(Task, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created']


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self):
        super().save()

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

