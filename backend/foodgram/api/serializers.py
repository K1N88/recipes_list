from django.contrib.auth import get_user_model
from rest_framework import serializers

from drf_extra_fields.fields import Base64ImageField

from recipes.models import (Ingredient, Tag, Recipe, Favorite,
                            Subscribe, RecipeIngredient, ShoppingCart)
from users.serializers import AuthorSerializer
from users.models import CustomUser


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
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


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
        return Favorite.objects.filter(
            user=self.context['request'].user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        return ShoppingCart.objects.filter(
            user=self.context['request'].user, recipe=obj
        ).exists()

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredient_recipe')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
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
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
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
        if self.context['request'].user.is_authenticated:
            return Favorite.objects.filter(
                user=self.context['request'].user, recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        if self.context['request'].user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=self.context['request'].user, recipe=obj
            ).exists()
        return False

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return Subscribe.objects.filter(
            user=self.context['request'].user, author=obj
        ).exists()

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(
            author=obj
        ).count()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(
            author=obj
        )
        return FavoriteSerializer(recipes, many=True).data


class SubscribePostSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return True

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(
            author=obj
        ).count()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(
            author=obj
        )
        return FavoriteSerializer(recipes, many=True).data


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('__all__')
