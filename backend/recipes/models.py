from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser

MAX_LENGTH_USER = 150
MAX_LENGTH = 200


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    email = models.EmailField(
        'email',
        unique=True,
        max_length=254,
        blank=False,
        null=False
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_LENGTH_USER,
        blank=False,
        null=False
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_LENGTH_USER,
        blank=False,
        null=False
    )
    age = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.first_name


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'], name='unique_subscription'
        )]


class Ingredient(models.Model):
    name = models.CharField(
        'Ингредиент',
        max_length=MAX_LENGTH,
    )
    measurement_unit = models.CharField(
        'Единица измерения ',
        max_length=MAX_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=MAX_LENGTH, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(max_length=MAX_LENGTH, unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        'Название рецепта',
        max_length=MAX_LENGTH
    )
    text = models.TextField(
        'Описание',
    )
    cooking_time = models.IntegerField(
        'Время приготовления',
        validators=[MinValueValidator
                    (1,
                     'Не может быть менее минуты')
                    ]
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='tags',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
    )
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
        related_name='ingredient'
    )

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецептов'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_recipe'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favourites'
            )
        ]
        ordering = ('user',)


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]
        ordering = ['user']

    def __str__(self):
        return (f'Ингредиенты из рецепта \
        "{self.recipe}" успешно добавлены в корзину!')
