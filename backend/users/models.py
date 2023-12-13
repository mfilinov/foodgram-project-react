from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_email
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    password = models.CharField(_("password"), max_length=150)
    email = models.EmailField(
        'email address',
        max_length=254,
        unique=True,
        help_text=(
            'Required. 254 characters or fewer. '
            'Letters, digits and @/./- only.'),
        validators=[validate_email],
        error_messages={
            'unique': 'Пользователь с таким email уже существует.',
        },
    )
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']

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
