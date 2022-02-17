from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    bio = models.TextField(
        'Биография',
        blank=True
    )


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)


class Genre(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=255)
    year = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        related_name="titles", blank=True, null=True
    )
    genre = models.ManyToManyField(
        Genre, through='GenreTitle', related_name='titles')

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
