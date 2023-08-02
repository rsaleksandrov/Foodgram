import base64

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import (
    UniqueTogetherValidator,
    UniqueValidator,
    ValidationError,
)

from ingredients.models import Ingredient
from recipies.models import Favorite, IngredientAmount, Recipe, ShoppingCart
from tags.models import Tag
from users.models import FoodGramUser, Subscribe


class FoodGramUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[
            UnicodeUsernameValidator(),
            UniqueValidator(queryset=FoodGramUser.objects.all()),
        ],
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=FoodGramUser.objects.all())],
    )
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = FoodGramUser
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}
        validators = {
            UniqueTogetherValidator(
                queryset=FoodGramUser.objects.all(),
                fields=('username', 'email'),
            ),
        }

    def get_is_subscribed(self, obj):
        request = self.context.get('request')

        return (
            request is not None
            and not request.user.is_anonymous
            and Subscribe.objects.filter(
                user=request.user,
                author=obj,
            ).exists()
        )


class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, attrs):
        request = self.context.get('request')
        if request is None:
            raise serializers.ValidationError(
                {'non_field_error': 'Запрос не передан'}
            )

        if not request.user.check_password(attrs['current_password']):
            raise serializers.ValidationError(
                {'current_password': 'Не верный пароль'}
            )

        if attrs['new_password'] == attrs['current_password']:
            raise serializers.ValidationError(
                {'non_field_error': 'Пароли совпадают'}
            )

        return super().validate(attrs)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('id', 'name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientAmoutCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeShortSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )

    def get_image(self, obj):
        return obj.image.url


class RecipeViewSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    author = FoodGramUserSerializer()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'text',
            'image',
            'cooking_time',
            'tags',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_image(self, obj):
        return obj.image.url

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            request is not None
            and not request.user.is_anonymous
            and Favorite.objects.filter(
                user=request.user,
                recipe=obj,
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request is not None
            and not request.user.is_anonymous
            and ShoppingCart.objects.filter(
                user=request.user,
                recipe=obj,
            ).exists()
        )

    def get_ingredients(self, obj):
        ingredients_amount = IngredientAmount.objects.filter(
            recipe=obj,
        )
        serializer = IngredientAmountSerializer(
            ingredients_amount,
            many=True,
        )
        return serializer.data


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.IntegerField(min_value=0), required=True
    )
    ingredients = IngredientAmoutCreateSerializer(required=True, many=True)
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = (
            'name',
            'text',
            'cooking_time',
            'image',
            'tags',
            'ingredients',
        )

    def validate_tags(self, tags):
        if Tag.objects.filter(id__in=tags).count() != len(tags):
            raise ValidationError(
                {'tags': 'Заданы отсутствующие теги'},
            )

        return tags

    def validate_ingredients(self, ingredients):
        ingredients_id = [data['id'] for data in ingredients]
        if Ingredient.objects.filter(
            id__in=ingredients_id,
        ).count() != len(ingredients):
            raise ValidationError(
                {'ingredients': 'Заданы отсутствующие ингредиенты'}
            )

        return ingredients

    def _set_tags_and_ingredients(self, instance, tags_data, ingredients_data):
        tags = Tag.objects.filter(id__in=tags_data)
        instance.tags.set(tags)

        ingredients = []
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data['id'])
            ingredients.append(
                IngredientAmount(
                    recipe=instance,
                    ingredient=ingredient,
                    amount=ingredient_data['amount'],
                )
            )
        IngredientAmount.objects.bulk_create(ingredients)

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data,
        )

        self._set_tags_and_ingredients(recipe, tags_data, ingredients_data)

        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')

        instance.tags.clear()
        instance.ingredients.clear()

        self._set_tags_and_ingredients(instance, tags_data, ingredients_data)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeViewSerializer(
            instance,
            context={'request': self.context.get('request')},
        )
        return serializer.data


class SubscribeSerializer(FoodGramUserSerializer):
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count',
    )
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes',
    )

    class Meta:
        model = FoodGramUser
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes_count',
            'recipes',
        )
        read_only_fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes_count',
            'recipes',
        )

    def get_recipes_count(self, obj):
        return obj.recipies.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if request is None:
            return []

        recipes_limit = request.GET.get('recipes_limit', None)
        if recipes_limit is None:
            user_recipies = obj.recipies.all()
        else:
            user_recipies = obj.recipies.all()[: int(recipes_limit)]

        serialiser = RecipeShortSerializer(
            user_recipies,
            context=self.context,
            many=True,
        )

        return serialiser.data


class SubscribeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ['user', 'author']
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=['user', 'author'],
                message='На этого автора уже подписаны',
            )
        ]

    def validate(self, attrs):
        if attrs['user'] == attrs['author']:
            raise serializers.ValidationError(
                {'error': 'На самого себя не подписываемся'}
            )
        return super().validate(attrs)

    def to_representation(self, instance):
        serializer = SubscribeSerializer(
            instance.user,
            context={'request': self.context.get('request')},
        )
        return serializer.data


class FavoriteAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['user', 'recipe']
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['user', 'recipe'],
                message='Этот рецепт уже в избранном',
            )
        ]

    def to_representation(self, instance):
        serializer = RecipeShortSerializer(
            instance.recipe,
            context={'request': self.context.get('request')},
        )
        return serializer.data


class ShoppingCartAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ['user', 'recipe']
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=['user', 'recipe'],
                message='Этот рецепт уже в корзине',
            )
        ]

    def to_representation(self, instance):
        serializer = RecipeShortSerializer(
            instance.recipe,
            context={'request': self.context.get('request')},
        )
        return serializer.data
