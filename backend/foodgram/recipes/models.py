from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=50, verbose_name='тег', unique=True)
    slug = models.SlugField(unique=True)
    color = models.CharField(max_length=7, verbose_name='цвет', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['slug']


class Ingredient(models.Model):
    name = models.CharField(max_length=250, verbose_name='продукт')
    measurement_unit = models.CharField(max_length=20,
                                        verbose_name='единицы измерения')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='автор рецепта'
    )
    name = models.CharField(max_length=50, verbose_name='название рецепта')
    image = models.ImageField(upload_to='recipes/',
                              verbose_name='изображение блюда')
    text = models.TextField(verbose_name='текст рецепта')
    cooking_time = models.IntegerField(verbose_name='время приготовления')
    tags = models.ManyToManyField(
        Tag,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient'
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
        verbose_name='ингридиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
        verbose_name='рецепт'
    )
    amount = models.IntegerField(verbose_name='количество')

    def __str__(self):
        return f'рецепт {self.recipe} - ингридиент {self.ingredient}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='любимый рецепт',
    )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart_user',
        verbose_name='пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='рецепт для покупки',
    )


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='автор рецепта',
    )
