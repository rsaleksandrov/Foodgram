from django.db import models


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        verbose_name='Название ингредиента',
        help_text='Введите название ингредиента (не более 200 символов)',
    )
    measurement_unit = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        verbose_name='Единица измерения',
        help_text='Введите единицу измерения (не более 200 символов)',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['id']

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'
