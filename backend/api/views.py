from django.contrib.auth import get_user_model
from django.db.models import Sum, Exists, OuterRef
from django.http import HttpResponse, FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    IsAuthenticated,
    SAFE_METHODS,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from recipes.models import (
    Recipe,
    Tag,
    Ingredient,
    Subscription,
    ShoppingCart,
    Favorite
)
from .permissions import IsOwnerOrReadOnly
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
from .utils import CreateDeleteMixin
from .filters import RecipeFilter

User = get_user_model()


class FoodgramUserViewSet(UserViewSet, CreateDeleteMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['post'])
    def subscribe(self, request, id):
        serializer = self.create_object(
            request,
            id,
            SubscriptionSerializer,
            SubscriptionReadSerializer,
            User
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id):
        self.delete_object(request, id, User, Subscription)
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


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ('^name',)
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet, CreateDeleteMixin):
    pagination_class = PageNumberPagination
    permission_classes = (IsOwnerOrReadOnly, IsAuthenticatedOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'ingredient__ingredient', 'tags'
        ).all()
        if self.request.user.is_authenticated:
            recipes = recipes.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(
                        user=self.request.user,
                        recipe_id=OuterRef('pk'),
                    )
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=self.request.user,
                        recipe_id=OuterRef('pk'),
                    )
                ),
            ).select_related('author')
        return recipes

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk):
        serializer = self.create_object(
            request,
            pk,
            FavoriteSerializer,
            RecipeFavoriteSerializer,
            Recipe
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        self.delete_object(request, pk, Recipe, Favorite)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def shopping_cart(self, request, pk):
        serializer = self.create_object(
            request,
            pk,
            ShoppingCartSerializer,
            RecipeFavoriteSerializer,
            Recipe
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        self.delete_object(request, pk, Recipe, ShoppingCart)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = ShoppingCart.objects.filter(
            user=request.user
        ).values_list(
            'recipe_id__ingredients__name',
            'recipe_id__ingredients__measurement_unit',
            Sum('recipe_id__ingredients__ingredient__amount'))
        ingredients = set(ingredients)

        shopping_list = ['Список покупок:']

        for ingredient in ingredients:
            shopping_list.append(
                f'{ingredient[0]} '
                f'({ingredient[1]})'
                f'{ingredient[2]}'
            )
        content = '\n'.join(shopping_list)
        response = HttpResponse(content, content_type='text/plain')
        response[
            'Content-Disposition'
        ] = 'attachment; filename="shopping_list.txt"'

        return FileResponse(
            '\n'.join(shopping_list),
            status=status.HTTP_200_OK,
            content_type='text/plain',
        )
