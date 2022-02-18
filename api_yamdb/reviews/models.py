from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

'''
class MyUserManage(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **kwargs):
        user = self.model(email=email, is_staff=True, is_superuser=True, **kwargs)
        user.set_password(password)
        user.save()
        return user
'''

class User(AbstractUser):
    ROLES = (
        ('user', 'user'),
        ('moderator', 'moderator'),
        ('admin', 'admin'),
    )
    bio = models.TextField(
        verbose_name='Биография',
        blank=True
    )
    confirmation_code = models.CharField(max_length=255, default='000000')
    email = models.EmailField(
        verbose_name='Email пользователя',
        max_length=254,
        unique=True
    )
    role = models.CharField(
        verbose_name='Права доступа',
        max_length=10,
        choices=ROLES,
        default='user'
    )
    #objects = MyUserManage()

    def __str__(self):
        return self.username
    
    def is_admin(self):
        return self.role == 'admin' or self.is_staff or self.is_superuser

    def is_moderator(self):
        return self.role == 'moderator'
