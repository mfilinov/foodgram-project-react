from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import validate_email
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.constants import (
    USER_PASSWORD_MAX_LENGTH,
    USER_EMAIL_MAX_LENGTH,
    USER_FIRST_NAME_MAX_LENGTH,
    USER_LAST_NAME_MAX_LENGTH, USER_USERNAME_MAX_LENGTH)
from users.validators import validate_username_include_me


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=USER_USERNAME_MAX_LENGTH,
        unique=True,
        help_text=_(
            f"Required. {USER_USERNAME_MAX_LENGTH} characters or fewer."
            " Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator, validate_username_include_me],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    password = models.CharField(_("password"),
                                max_length=USER_PASSWORD_MAX_LENGTH)
    email = models.EmailField(
        'email address',
        max_length=USER_EMAIL_MAX_LENGTH,
        unique=True,
        help_text=(
            f'Required. {USER_EMAIL_MAX_LENGTH} characters or fewer. '
            'Letters, digits and @/./- only.'),
        validators=[validate_email],
        error_messages={
            'unique': 'Пользователь с таким email уже существует.',
        },
    )
    first_name = models.CharField(_('first name'),
                                  max_length=USER_FIRST_NAME_MAX_LENGTH)
    last_name = models.CharField(_('last name'),
                                 max_length=USER_LAST_NAME_MAX_LENGTH)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriber')
    subscribing = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribing')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscribing'],
                name='unique_user_subscribing'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.subscribing}'
