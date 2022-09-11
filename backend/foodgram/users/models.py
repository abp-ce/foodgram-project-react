from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    first_name = models.CharField('Имя', max_length=150, blank=False,
                                  null=False)
    last_name = models.CharField('Фамилия', max_length=150, blank=False,
                                 null=False)
    email = models.EmailField('Email', unique=True)

    REQUIRED_FIELDS = ['first_name', 'last_name', 'email', 'password']


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='%(app_label)s_%(class)s_unique_relationships'
            ),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_prevent_self_follow',
                check=~models.Q(user=models.F('author')),
            ),
        ]
