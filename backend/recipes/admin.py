from django.contrib import admin
from django.db.models import Count

from recipes.models import (Ingredient, Tag, Recipe, ShoppingCart,
                            Favorite, RecipeIngredient)


admin.site.register(Tag)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1


class IngredientInline(admin.TabularInline):
    model = Ingredient
    readonly_fields = ('name', 'measurement_unit')
    inlines = [
        RecipeIngredientInline,
    ]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'name', 'in_favorite')
    list_filter = ('tags', 'author', 'name')
    search_fields = ('name',)
    ordering = ('author',)
    inlines = [
        IngredientInline,
    ]

    def in_favorite(self, obj):
        result = Favorite.objects.filter(recipe=obj).aggregate(Count("recipe"))
        return result["recipe__count"]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
