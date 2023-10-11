from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import AuthorViewSet, RecipeViewSet, TagViewSet, IngredientsViewSet

router = DefaultRouter()
router.register(r'users', AuthorViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients_in_recipe', IngredientsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
