from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    bio = models.TextField(
        'Биография',
        blank=True
    )


class Review(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='автор'
    )
    score = models.IntegerField('оценка', validators=[
                                MinValueValidator(1, 'Минимальная оценка-1'),
                                MaxValueValidator(10, 'Максимальная оценка-10')
                                ])
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name='произведение'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_riview')
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments',
        verbose_name='автор'
    )
    pub_date = models.DateTimeField(
        'Дата комментария', auto_now_add=True
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments',
        verbose_name='отзыв'
    )

    def __str__(self):
        return self.text
