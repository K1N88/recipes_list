from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings

from recipes.validators import validate_name, validate_hex


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=settings.MAX_LENGTH, verbose_name='тег',
                            unique=True, validators=[validate_name])
    slug = models.SlugField(unique=True)
    color = models.CharField(max_length=7, verbose_name='цвет', unique=True,
                             validators=[validate_hex])

    class Meta:
        ordering = ['slug']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=settings.MAX_LENGTH,
                            verbose_name='продукт', validators=[validate_name])
    measurement_unit = models.CharField(max_length=settings.MAX_LENGTH,
                                        verbose_name='единицы измерения')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='автор рецепта'
    )
    name = models.CharField(max_length=settings.MAX_LENGTH,
                            verbose_name='название рецепта',
                            validators=[validate_name])
    image = models.ImageField(upload_to='recipes/',
                              verbose_name='изображение блюда')
    text = models.TextField(verbose_name='текст рецепта')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='время приготовления',
    )
    tags = models.ManyToManyField(Tag, related_name='tags')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='ingredients',
        blank=False
    )

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='ингридиент',
        related_name='+',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
        verbose_name='рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='количество',
    )

    def __str__(self):
        return f'''рецепт {self.recipe}
                   ингридиент {self.ingredient} количество {self.amount}'''


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',  # получаем queryset
                                       # в сериалайзерах стр 84
        verbose_name='пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='любимый рецепт',
    )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart_user',  # получаем queryset
                                   # в сериалайзерах стр 90
        verbose_name='пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт для покупки',
    )
