from enum import unique, IntEnum

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dob = models.DateField(null=True)
    location = models.TextField(null=False, default='unknown')
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
    files = models.FileField(null=False, upload_to='images/')

    def __str__(self):
        return self.username.user.username


class FriendRequest(models.Model):
    from_user = models.ForeignKey(UserProfile, related_name='sent_friend_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(UserProfile, related_name='received_friend_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From: {self.from_user}, To: {self.to_user}"


############################################# extra task################################################


def get_choices(enum_class):
    """
    Function to generate choices for Django model class choice field
    Args:
        enum_class (Enum): Either IntEnum or Enum class class
        containing related choices
    Returns:
        tuple of choices
        Examples:
            In case of IntEnum class
            ((3, 'BOOLEAN'), (2, 'DATETIME'), (0, 'INTEGER'), (1, 'STRING'))
            In case of Enum class
            (('A', 'BOOLEAN'), ('B', 'DATETIME'), ('C', 'INTEGER'),
            ('D', 'STRING'))
            )
    """
    choices = tuple([
        (tag.value, tag.name.replace('_', ' ').title()) for tag in enum_class
    ])
    return choices


@unique
class IconType(IntEnum):
    SVG = 1
    IMAGE = 2


SYSTEM_ADMIN_USER_ID = 121


class BaseInfo(models.Model):
    created_by_id = models.IntegerField(
        db_index=True, default=SYSTEM_ADMIN_USER_ID
    )
    updated_by_id = models.IntegerField(db_index=True, null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_on = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class Category(BaseInfo):
    name = models.CharField(max_length=500, unique=True)
    internal_name = models.CharField(max_length=500, unique=True, default="")

    def __str__(self):
        return self.name


class Icon(BaseInfo):
    """
    For a single record of this table
    """
    CONTAINER_ID = "icon"

    def icon_upload_to(instance, filename):
        # MEDIA_ROOT/category_<id>/client_<id>/<filename>
        path = f"icons/{instance.category_id}"
        if instance.client_id:
            path = f"{path}/{instance.client_id}"
        return f"{path}/{filename}"

    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL
    )

    internal_name = models.CharField(max_length=500, unique=True, default="")

    client_id = models.IntegerField(db_index=True, null=True, blank=True)

    name = models.CharField(max_length=1000, db_index=True)
    type = models.IntegerField(
        choices=get_choices(IconType), default=IconType.SVG.value
    )

    html = models.TextField(
        null=True, blank=True, help_text=(
        )
    )
    image = models.FileField(upload_to=icon_upload_to, null=True, blank=True)
    url = models.URLField(null=True, blank=True)

    class Meta:
        unique_together = ("category", "client_id", "name", "type")

    def __str__(self):
        return self.name