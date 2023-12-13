from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status

from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient
from recipes.utils.map_ingredients_to_recipe import map_ingredients_to_recipe
from users.serializers import UserSerializer

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',)

    def get_is_in_shopping_cart(self, obj):
        current_user = self.context['request'].user
        if not current_user.is_anonymous:
            return obj.cart_user.filter(user=current_user).exists()
        return False

    def get_is_favorited(self, obj):
        current_user = self.context['request'].user
        if not current_user.is_anonymous:
            return obj.favorite.filter(user=current_user).exists()
        return False

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipe_amount__amount')
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount',)


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time',)

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        map_ingredients_to_recipe(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        map_ingredients_to_recipe(ingredients, instance)
        return instance

    def to_representation(self, instance):
        return RecipeGetSerializer(instance, context=self.context).data

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                "Поле не может быть пустым",
                code=status.HTTP_400_BAD_REQUEST)
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                "Рецепт должен содержать ингредиенты",
                code=status.HTTP_400_BAD_REQUEST)
        id_set = set()
        for ingredient in value:
            obj = Ingredient.objects.filter(id=ingredient['id']).exists()
            if not obj:
                raise serializers.ValidationError(
                    "Ингредиент отсутствует",
                    code=status.HTTP_400_BAD_REQUEST)
            if ingredient['id'] in id_set:
                raise serializers.ValidationError(
                    "Ингредиенты не должны повторяться",
                    code=status.HTTP_400_BAD_REQUEST)
            id_set.add(ingredient['id'])
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                "Рецепт должен содержать тэги",
                code=status.HTTP_400_BAD_REQUEST)
        tag_set = set()
        for tag in value:
            if tag in tag_set:
                raise serializers.ValidationError(
                    "Тэги не должны повторяться",
                    code=status.HTTP_400_BAD_REQUEST)
            tag_set.add(tag)
        return value
