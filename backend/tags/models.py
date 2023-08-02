from django.db import models

from tags.validators import color_code_validate


class Tag(models.Model):
    name = models.CharField(
        max_length=200, unique=True, verbose_name='Имя тега'
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        validators=[color_code_validate],
        verbose_name='Цвет',
        help_text='Цвет тега в HEX-формате (#RRGGBB)',
    )
    slug = models.SlugField(
        max_length=200, unique=True, verbose_name='Код тега (строка)'
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['id']

    def __str__(self):
        return self.name
