from django.contrib import admin
from .models import User, Ingredient, Tag, Recipe


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'first_name', 'last_name')
    list_filter = ('email', 'username')
    search_fields = ('username', 'email')


admin.site.register(User, UserAdmin)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)


admin.site.register(Ingredient, IngredientAdmin)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    search_fields = ('name', 'author__username')


admin.site.register(Tag, TagAdmin)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'text', 'cooking_time',
                    'author', 'pub_date',)
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name', 'author__username')


admin.site.register(Recipe, RecipeAdmin)
