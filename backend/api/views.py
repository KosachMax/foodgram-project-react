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

from .permissions import IsOwnerOrReadOnly

from .utils import create_object, delete_object
from recipes.models import (
    Recipe,
    Tag,
    Ingredient,
    Subscription,
    ShoppingCart,
    Favorite, IngredientInRecipe
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


class FoodgramUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['post'])
    def subscribe(self, request, id):
        serializer = create_object(
            request,
            id,
            SubscriptionSerializer,
            SubscriptionReadSerializer,
            User
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id):
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
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    permission_classes = (IsOwnerOrReadOnly, IsAuthenticatedOrReadOnly)

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'ingredients', 'tags'
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

    @action(detail=True, methods=['post'])
    def create_favorite(self, request, pk):
        serializer = create_object(
            request,
            pk,
            FavoriteSerializer,
            RecipeFavoriteSerializer,
            Recipe
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def delete_favorite(self, request, pk):
        delete_object(request, pk, Recipe, Favorite)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def shopping_cart(self, request, pk):
        serializer = create_object(
            request,
            pk,
            ShoppingCartSerializer,
            RecipeFavoriteSerializer,
            Recipe
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def delete_shopping_cart(self, request, pk):
        delete_object(request, pk, Recipe, ShoppingCart)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = (
            IngredientInRecipe.objects
            .filter(recipe__in=request.user.cart.all())
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
        )
        shopping_list = ['Список покупок:']

        for ingredient in ingredients:
            shopping_list.append(
                f'{ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]})'
                f'{ingredient["total_amount"]}'
            )
        content = '\n'.join(shopping_list)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'

        return response
