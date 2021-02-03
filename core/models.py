import uuid
import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin
from django.conf import settings


def post_image_file_path(instance, filename):
    """Generate file path for new post image"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads/posts/', filename)

def post_avatar_path(instance, filename):
    """Generate file path for new avatar"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4}.{ext}'

    return os.path.join('uploads/avatar/', filename)


class UserManager(BaseUserManager):
    def create_user(self, email, first_name, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), first_name=first_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, first_name, password):
        user = self.create_user(email, first_name, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model"""
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)

    username = models.CharField(max_length=255, unique=True)

    avatar = models.ImageField(
        null=True,
        upload_to=post_avatar_path
    )

    his_followers = models.OneToOneField(
        'Followers',
        on_delete=models.CASCADE,
        related_name='his_followers',
        null=True
    )

    his_follows = models.OneToOneField(
        'Follows',
        on_delete=models.CASCADE,
        related_name='his_follows',
        null=True
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    def __str__(self):
        return self.first_name

    @property
    def follow(self):
        a =  self.his_follows.follows.all().__len__()
        return a

    @property
    def follower(self):
        a =  self.his_followers.followers.all().__len__()
        return a


# class FriendShip(models.Model):
#     """Friendship object beetwen users"""
class Followers(models.Model):
    """Followers of a user"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers_user'
    )
    followers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='followers'
    )

    def __str__(self):
        return self.user.first_name


class Follows(models.Model):
    """Users object that follows a user"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follows_user'
    )
    follows = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='follows'
    )

    def __str__(self):
        return self.user.first_name


class Post(models.Model):
    """Post model of a user"""
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=510)
    image = models.ImageField(
        null=True,
        upload_to=post_image_file_path
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.title} ({self.user.first_name})'


class Thread(models.Model):
    # thread for chat group
    name = models.CharField(max_length=255, blank=True, null=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    messages = models.ManyToManyField('Message')


class Message(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
