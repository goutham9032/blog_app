import time
import string
import random

from django.db import models
from django.contrib.auth.models  import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

DEFAULT_USER_AVTRS = settings.DEFAULT_AVATARS
get_rand_string = lambda x:''.join(random.choice(string.ascii_lowercase) for _ in range(x))

class BlogPost(models.Model):
    description = models.CharField(max_length=255, blank=True)
    file_location = models.CharField(max_length=255, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.IntegerField(default=int(time.time()))
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    likes_count = models.IntegerField(default=0)

class BlogComments(models.Model):
    comment_creator = models.ForeignKey(User, on_delete=models.CASCADE)
    blogpost = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    comment = models.CharField(max_length=255, default='')
    slug = models.CharField(max_length=20, default=get_rand_string(5))

class UserLikes(models.Model):
    blog = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class UserAddInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.CharField(max_length=255, default=random.choices(DEFAULT_USER_AVTRS)[0])
    active = models.BooleanField(default=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserAddInfo.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.useraddinfo.save()
