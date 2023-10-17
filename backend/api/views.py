from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from rest_framework import viewsets, status
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    IsAuthenticated,
    SAFE_METHODS,
    IsAuthenticatedOrReadOnly
)

from rest_framework.response import Response

from .utils import create_object, delete_object
from .models import (
    Recipe,
    Tag,
    Ingredient,
    Subscription,
    ShoppingCart,
    Favorite
)
from .serializers import (
    UserSerializer,
    TagSerializer,
    IngredientSerializer,
    SubscriptionReadSerializer,
    SubscriptionSerializer,
    RecipeFavoriteSerializer,
    ShoppingCartSerializer,
    FavoriteSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer
)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id):
        if request.method == 'POST':
            serializer = create_object(
                request,
                id,
                SubscriptionSerializer,
                SubscriptionReadSerializer,
                User
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        delete_object(request, id, User, Subscription)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        user = request.user
        authors = User.objects.filter(subscribing__user=user)

        paged_queryset = self.paginate_queryset(authors)
        serializer = SubscriptionReadSerializer(
            paged_queryset,
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)


class IngredientsViewSet(viewsets.ModelViewSet):
    pagination_class = None
    serializer_class = IngredientSerializer

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        ingredients_name = self.request.query_params.get('name')
        if ingredients_name is not None:
            queryset = queryset.filter(name__istartswith=ingredients_name)
        return queryset


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IsOwnerOrReadOnly:
    pass


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    permission_classes = (IsOwnerOrReadOnly, IsAuthenticatedOrReadOnly)

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'amount_ingredients__ingredient', 'tags'
        ).all()
        tags_name = self.request.query_params.get('name')
        if tags_name is not None:
            recipes = recipes.filter(tags__slug__istartswith=tags_name)
        return recipes

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk):
        if request.method == 'POST':
            serializer = create_object(
                request,
                pk,
                FavoriteSerializer,
                RecipeFavoriteSerializer,
                Recipe
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        delete_object(request, pk, Recipe, Favorite)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            serializer = create_object(
                request,
                pk,
                ShoppingCartSerializer,
                RecipeFavoriteSerializer,
                Recipe
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        delete_object(request, pk, Recipe, ShoppingCart)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = ShoppingCart.objects.filter(
            user=request.user
        ).values(
            'recipe_id__ingredients__name',
            'recipe_id__ingredients__measurement_unit'
        ).annotate(
            total_amount=Sum(
                'recipe_id__ingredients__amount_ingredients__amount'
            )
        )
        shopping_list = 'Список покупок:'

        for ingredient in ingredients:
            shopping_list.append(
                f'{ingredient["recipe_id__ingredients__name"]} '
                f'({ingredient["recipe_id__ingredients__measurement_unit"]})'
                f'{ingredient["total_amount"]}'
            )
        content = '\n'.join(shopping_list)
        response = HttpResponse(content, content_type='text/plain')
        response[
            'Content-Disposition'
        ] = 'attachment; filename="shopping_list.txt"'

        return response
