from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        'Ингредиент',
        max_length=200,
    )
    measurement_unit = models.CharField(
        'Единица измерения ',
        max_length=200
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        'Название',
        max_length=200
    )
    text = models.TextField(
        'Описание',
    )
    cooking_time = models.IntegerField(
        'Время приготовления',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    tags = models.ManyToManyField(Tag)
    ingredients = models.ManyToManyField(Ingredient)
    image = models.ImageField(
        'Фото рецепта',
        upload_to='static/recipe/',
        blank=True,
        null=True,
    )
    pub_date = models.DateTimeField(
        'Когда опубликовано',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient')
    amount = models.PositiveSmallIntegerField(
        'Кол-во',
        default=1
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe'
    )

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецептов'
        ordering = ('-id',)

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'
