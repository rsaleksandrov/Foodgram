from distutils.util import strtobool

import django_filters

from ingredients.models import Ingredient
from recipies.models import Recipe
from tags.models import Tag

BOOL_CHOICE = (
    ('1', 'True'),
    ('0', 'False'),
)


class IngredientNameFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name', lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipiesFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    author = django_filters.NumberFilter(
        field_name='author', lookup_expr='exact'
    )
    is_favorited = django_filters.ChoiceFilter(
        choices=BOOL_CHOICE, method='filter_favorited'
    )
    is_in_shopping_cart = django_filters.ChoiceFilter(
        choices=BOOL_CHOICE, method='filter_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags']

    def filter_favorited(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return Recipe.objects.none()

        if strtobool(value):
            return queryset.filter(favorites__user=self.request.user)

        return queryset.exclude(favorites__user=self.request.user)

    def filter_shopping_cart(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return Recipe.objects.none()

        if strtobool(value):
            return queryset.filter(shopping_cart__user=self.request.user)

        return queryset.exclude(shopping_cart__user=self.request.user)
