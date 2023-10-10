from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RecipeViewSet, TagViewSet, IngredientInRecipeViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients_in_recipe', IngredientInRecipeViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]

# settings.py
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'api',
]