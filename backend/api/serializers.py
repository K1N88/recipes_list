from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Ingredient, Tag, Recipe, Favorite,
                            RecipeIngredient, ShoppingCart)
from users.models import FoodgramUser


class AuthorSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = FoodgramUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        if not self.context['request'].user.is_authenticated:
            return False
        return self.context['request'].user.subscriber.all().exists()


class SubscribeSerializer(AuthorSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = FoodgramUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_recipes(self, obj):
        recipes_limit_default = 3
        if 'recipes_limit' in self.context['request'].query_params.keys():
            recipes_limit = self.context['request'].query_params[
                'recipes_limit'
            ]
        else:
            recipes_limit = recipes_limit_default
        return FavoriteSerializer(
            Recipe.objects.filter(author=obj)[:int(recipes_limit)],
            many=True
        ).data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


def set_ingredients(recipe, ingredients):
    RecipeIngredient.objects.bulk_create([RecipeIngredient(
        recipe=recipe,
        ingredient=ingredient['id'],
        amount=ingredient['amount']
    ) for ingredient in ingredients])


def is_favorited(self, obj):
    return Favorite.objects.filter(
        favorite_user__recipe=obj
    ).exists()


def is_in_shopping_cart(self, obj):
    return ShoppingCart.objects.filter(
        cart_user__recipe=obj
    ).exists()


class RecipePostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    image = Base64ImageField(max_length=None, use_url=True)
    cooking_time = serializers.IntegerField(min_value=1)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    ingredients = RecipeIngredientSerializer(
        source='ingredient_recipe', many=True
    )

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        return is_favorited(self, obj)

    def get_is_in_shopping_cart(self, obj):
        return is_in_shopping_cart(self, obj)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredient_recipe')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        set_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredient_recipe')
        tags = validated_data.pop('tags')
        instance.author = validated_data.get('author', instance.author)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.save()
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(
            recipe=instance,
        ).delete()
        set_ingredients(instance, ingredients)
        return instance


class RecipeSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        return is_favorited(self, obj)

    def get_is_in_shopping_cart(self, obj):
        return is_in_shopping_cart(self, obj)

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
