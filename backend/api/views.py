from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import IngredientNameFilter, RecipiesFilter
from api.paginators import CustomPNPaginator
from api.permissions import IsAuthenticatedAuthorOrReadOnly
from api.serializers import (
    FavoriteAddSerializer,
    FoodGramUserSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeViewSerializer,
    SetPasswordSerializer,
    ShoppingCartAddSerializer,
    SubscribeCreateSerializer,
    SubscribeSerializer,
    TagSerializer,
)
from ingredients.models import Ingredient
from recipies.models import IngredientAmount, Recipe
from tags.models import Tag
from users.models import FoodGramUser


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = FoodGramUser.objects.all()
    serializer_class = FoodGramUserSerializer
    pagination_class = CustomPNPaginator

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.set_password(request.data['password'])
        user.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def me(self, request):
        serializer = FoodGramUserSerializer(
            request.user,
            context=self.get_serializer_context(),
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)

        request.user.set_password(request.data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        authors = FoodGramUser.objects.filter(subscribed__user=request.user)
        paginate_authors_queryset = self.paginate_queryset(authors)
        serializer = SubscribeSerializer(
            paginate_authors_queryset,
            context=self.get_serializer_context(),
            many=True,
        )

        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request, pk):
        if request.method == 'POST':
            serializer = SubscribeCreateSerializer(
                data={
                    'user': request.user.id,
                    'author': pk,
                }
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not request.user.subscriber.filter(author_id=pk).exists():
                return Response(
                    {'error': 'Подписки нет'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            request.user.subscriber.filter(author_id=pk).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientNameFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedAuthorOrReadOnly,)
    pagination_class = CustomPNPaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipiesFilter

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer

        return RecipeViewSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            serializer = FavoriteAddSerializer(
                data={
                    'user': request.user.id,
                    'recipe': pk,
                }
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not request.user.favorites.filter(recipe_id=pk).exists():
                return Response(
                    {'error': 'Рецепта нет в избранном'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            request.user.favorites.filter(recipe_id=pk).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            serializer = ShoppingCartAddSerializer(
                data={
                    'user': request.user.id,
                    'recipe': pk,
                }
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not request.user.shopping_cart.filter(recipe_id=pk).exists():
                return Response(
                    {'error': 'Рецепта нет в корзине'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            request.user.shopping_cart.filter(recipe_id=pk).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        shopping_cart_recipes_id = (
            request.user.shopping_cart.all().values_list(
                'recipe__id', flat=True
            )
        )
        ingredients_list = IngredientAmount.objects.filter(
            recipe_id__in=shopping_cart_recipes_id
        ).values('ingredient__name', 'ingredient__measurement_unit', 'amount')

        shopping_cart = {}
        for ingredient in ingredients_list:
            if ingredient['ingredient__name'] in shopping_cart:
                shopping_cart[ingredient['ingredient__name']][0] += ingredient[
                    'amount'
                ]
            else:
                shopping_cart[ingredient['ingredient__name']] = [
                    ingredient['amount'],
                    ingredient['ingredient__measurement_unit'],
                ]

        shopping_cart_file = ''
        for name, data in shopping_cart.items():
            shopping_cart_file = (
                shopping_cart_file + f'{name}\t{data[0]} {data[1]}\n'
            )

        response = HttpResponse(
            shopping_cart_file, status=200, content_type='text/plain'
        )
        response[
            'Content-Disposition'
        ] = f'attachment; filename="{request.user.username}shopping_cart.txt"'
        return response
