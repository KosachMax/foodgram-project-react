from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, RecipeViewSet, TagViewSet, IngredientsViewSet

app_name = 'api'

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'ingredients', IngredientsViewSet, basename='ingredient')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
