from django.core.validators import MinValueValidator
from django.db import models

from ingredients.models import Ingredient
from tags.models import Tag
from users.models import FoodGramUser


class Recipe(models.Model):
    author = models.ForeignKey(
        FoodGramUser,
        related_name='recipies',
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        help_text='Выберите автора рецепта',
    )
    name = models.CharField(
        max_length=200,
        blank=False,
        null=False,
        verbose_name='Название рецепта',
        help_text='Введите название рецепта (не более 200 символов)',
    )
    text = models.TextField(
        blank=False,
        null=False,
        verbose_name='Описание рецепта',
        help_text='Введите описание рецепта',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        help_text='Введите время приготовления в минутах (>=1)',
        blank=False,
        null=False,
        default=1,
        validators=[
            MinValueValidator(
                1,
                'Время приготовления должно быть больше или равно 1',
            )
        ],
    )
    image = models.ImageField(
        upload_to='recipies_img/',
        null=False,
        blank=False,
        verbose_name='Фото',
    )
    tags = models.ManyToManyField(Tag, blank=False, related_name='recipies')
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=False,
        related_name='recipies',
        through='IngredientAmount',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        help_text='Введите дату публикации.',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        blank=False,
        null=False,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        blank=False,
        null=False,
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        help_text='Введите количество ингредиента (>=1)',
        validators=[
            MinValueValidator(
                1,
                'Количество должно быть больше или равно 1',
            )
        ],
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return (
            f'{self.recipe.name} '
            f'[{self.ingredient.name} - {self.amount} '
            f'{self.ingredient.measurement_unit}]'
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        FoodGramUser,
        on_delete=models.CASCADE,
        related_name='favorites',
        blank=False,
        verbose_name='Пользователь',
        help_text='Выберите пользователя',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        blank=False,
        verbose_name='Рецепт',
        help_text='Выберите рецепт',
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ['id']
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='favorite_user_recipe_unique'
            ),
        )

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        FoodGramUser,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        blank=False,
        verbose_name='Пользователь',
        help_text='Выберите пользователя',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        blank=False,
        verbose_name='Рецепт',
        help_text='Выберите рецепт',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        ordering = ['id']
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='shopping_cart_user_recipe_unique',
            ),
        )

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'
