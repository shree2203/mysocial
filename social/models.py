from enum import unique, IntEnum

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dob = models.DateField(null=True)
    location = models.CharField(null=False, default='unknown', max_length=10)
    profile_image = models.ImageField(upload_to='images/', null=True, blank=True)
    phn_num = models.CharField(max_length=10, default='0000000000')
    gender = models.CharField(max_length=10, null=False, default='unknown')
    school = models.CharField(max_length=100, null=False, default='unknown')
    bio = models.TextField(blank=True)
    interest = models.CharField(max_length=100, null=False, default='unknown')
    friends = models.ManyToManyField('self', blank=True)

    def __str__(self):
        return self.user.username

    def temp_col(self):
        return f"{self.dob} {self.gender}"


class UserPost(models.Model):
    username = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)  # Automatically set to the current date
    time = models.TimeField(default=timezone.now)  # Automatically set to the current time
    caption = models.CharField(max_length=250, null=True)
    files = models.ImageField(null=False, upload_to='images/')


class FriendRequest(models.Model):
    from_user = models.ForeignKey(UserProfile, related_name='sent_friend_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(UserProfile, related_name='received_friend_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From: {self.from_user}, To: {self.to_user}"
