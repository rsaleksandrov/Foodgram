from django.contrib import admin

from recipies.models import Favorite, IngredientAmount, Recipe, ShoppingCart
from tags.models import Tag


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты'


class RecipeTagsFilter(admin.SimpleListFilter):
    title = 'Теги'
    parameter_name = 'tags'

    def lookups(self, request, model_admin):
        return [(tag.pk, tag.name) for tag in Tag.objects.all()]

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(tags__id=self.value())

        return None


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientAmountInline,)
    list_display = ('id', 'name', 'cooking_time', 'recipe_tags', 'author')
    search_fields = ('name', 'author__username')
    list_filter = [RecipeTagsFilter, 'author__username']
    filter_horizontal = ['tags']

    def recipe_tags(self, obj):
        return ', '.join([t.name for t in obj.tags.all()])

    recipe_tags.short_description = 'Теги'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user',)
