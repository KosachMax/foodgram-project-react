from rest_framework import viewsets
from .models import Author, Recipe, Tag, IngredientInRecipe, Ingredient
from .serializers import AuthorSerializer, RecipeSerializer, TagSerializer, IngredientInRecipeSerializer, \
    IngredientSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-id')
    # permission_classes = (permissions.IsAuthenticated,)
    # filter_backends = [DjangoFilterBackend]
    # filterset_class = RecipeFilter
    # pagination_class = SmallPageNumberPagination
    serializer_class = RecipeSerializer

    def get_queryset(self):
        is_favorited = self.request.GET.get("is_favorited")
        is_in_shopping_cart = self.request.GET.get("is_in_shopping_cart")
        if is_favorited:
            return Recipe.objects.filter(favouriting__user=self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class IngredientInRecipeViewSet(viewsets.ModelViewSet):
    queryset = IngredientInRecipe.objects.all()
    serializer_class = IngredientInRecipeSerializer
