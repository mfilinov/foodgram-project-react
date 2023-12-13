from django.contrib import admin
from django.contrib.admin import display
from django.utils.html import format_html

from recipes.models import (Tag, Ingredient, Recipe, RecipeIngredient,
                            Favorite, Cart)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug',
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeTagInline(admin.TabularInline):
    model = Recipe.tags.through
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'text',
        'image_preview',
        'cooking_time',
        'author',
        'in_favorites'
    )
    search_fields = ('name', 'author')
    list_display_links = ('name',)
    list_filter = ('name', 'author', 'tags')
    inlines = [RecipeIngredientInline, RecipeTagInline]

    @display(description='В избранном')
    def in_favorites(self, obj):
        return obj.favorite.count()

    @display(description='Изображение')
    def image_preview(self, obj):
        return format_html(
            f'<img src="{obj.image.url}" height=50px />')


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


admin.site.empty_value_display = 'Не задано'
