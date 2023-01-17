from django.contrib import admin
from django.db.models import Count
from django import forms

from recipes.models import (Ingredient, Tag, Recipe, ShoppingCart,
                            Favorite, RecipeIngredient)


admin.site.register(Tag)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)


class RecipeIngredientAdminForm(forms.ModelForm):
    amount = forms.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'amount']


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    form = RecipeIngredientAdminForm


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'name', 'in_favorite')
    list_filter = ('tags', 'author', 'name')
    search_fields = ('name',)
    ordering = ('author',)
    inlines = [
        RecipeIngredientInline,
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
