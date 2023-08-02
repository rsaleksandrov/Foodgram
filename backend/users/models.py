from django.contrib.auth.models import AbstractUser
from django.db import models


class FoodGramUser(AbstractUser):
    email = models.EmailField(
        blank=False,
    )
    first_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Фамилия',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']
        constraints = (
            models.UniqueConstraint(
                fields=('email',), name='foodgramuser_email_unique'
            ),
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='foodgramuser_user_email_unique',
            ),
        )

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        FoodGramUser,
        on_delete=models.CASCADE,
        related_name='subscriber',
        blank=False,
        verbose_name='Пользователь',
        help_text='Выберите пользователя',
    )
    author = models.ForeignKey(
        FoodGramUser,
        on_delete=models.CASCADE,
        related_name='subscribed',
        blank=False,
        verbose_name='Автор',
        help_text='Выберите автора',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='do_not_subscribe_to_self',
            ),
            models.UniqueConstraint(
                fields=('user', 'author'), name='user_author_unique'
            ),
        )

    def __str__(self):
        return f'{self.user.username} - {self.author.username}'
