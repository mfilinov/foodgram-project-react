from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from recipes.constants import (
    TAG_NAME_MAX_LENGTH,
    TAG_SLUG_MAX_LENGTH,
    TAG_COLOR_MAX_LENGTH,
    INGREDIENT_NAME_MAX_LENGTH,
    INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH,
    RECIPE_NAME_MAX_LENGTH,
    RECIPE_TEXT_MAX_LENGTH,
    RECIPE_C_T_MIN_VALUE,
    RECIPE_C_T_MAX_VALUE,
    RECIPE_INGREDIENT_AMOUNT_MIN_VALUE,
    RECIPE_INGREDIENT_AMOUNT_MAX_VALUE)
from recipes.validators import validate_color

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Название', max_length=TAG_NAME_MAX_LENGTH, unique=True)
    color = models.CharField(
        'Цвет в HEX', max_length=TAG_COLOR_MAX_LENGTH,
        unique=True, validators=[validate_color])
    slug = models.SlugField(
        'Уникальный слаг', max_length=TAG_SLUG_MAX_LENGTH,
        unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название', max_length=INGREDIENT_NAME_MAX_LENGTH, db_index=True)
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField('Название',
                            max_length=RECIPE_NAME_MAX_LENGTH)
    text = models.TextField('Текстовое описание',
                            max_length=RECIPE_TEXT_MAX_LENGTH)
    image = models.ImageField('Изображение',
                              upload_to='recipe_images')
    cooking_time = models.PositiveIntegerField(
        'Время приготовления в минутах',
        validators=[MinValueValidator(RECIPE_C_T_MIN_VALUE),
                    MaxValueValidator(RECIPE_C_T_MAX_VALUE)])
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipe')
    tags = models.ManyToManyField(to=Tag, related_name='recipe')
    ingredients = models.ManyToManyField(
        to=Ingredient,
        through='RecipeIngredient',
        related_name='recipe')
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='ingredient_amount')
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='recipe_amount')
    amount = models.PositiveIntegerField(
        'Количество в рецепте',
        validators=[MinValueValidator(RECIPE_INGREDIENT_AMOUNT_MIN_VALUE),
                    MaxValueValidator(RECIPE_INGREDIENT_AMOUNT_MAX_VALUE)])

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.recipe.name} - {self.ingredient} - {self.amount}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorite')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorite')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_user_favorite'
            )
        ]

    def __str__(self):
        return f'{self.recipe} - {self.user}'


class Cart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='cart_recipe')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='cart_user')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_user_cart'
            )
        ]

    def __str__(self):
        return f'{self.recipe} - {self.user}'
