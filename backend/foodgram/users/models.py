from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator

from foodgram.settings import MAX_LENGTH
from users.validators import validate_username


class CustomUser(AbstractUser):
    email = models.EmailField(
        max_length=254,
        unique=True,
        validators=[EmailValidator]
    )
    username = models.CharField(
        max_length=MAX_LENGTH,
        unique=True,
        verbose_name='Логин пользователя',
        validators=[validate_username],
    )
    first_name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Имя пользователя'
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Фамилия пользователя'
    )
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'password']

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='email_user_unique',
                fields=['email', 'username'],
            ),
        ]
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username[:15]
