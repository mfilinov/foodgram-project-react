from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from djoser.serializers import UserCreateMixin
from rest_framework import serializers

from recipes.models import Recipe

User = get_user_model()
username_validator = UnicodeUsernameValidator()


def validate_username_include_me(value):
    if value == 'me':
        raise serializers.ValidationError(
            "Использовать имя 'me' в качестве username запрещено")
    return value


class UserCreateSerializer(UserCreateMixin, serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"},
                                     write_only=True, max_length=150)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password')
        read_only_fields = ('id',)

    def validate_username(self, value):
        return validate_username_include_me(value)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        current_user = self.context['request'].user
        if not current_user.is_anonymous:
            is_subscribed = obj.subscribing.filter(user=current_user).exists()
            return is_subscribed
        return False

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed')
        read_only_fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed')


class RecipeSubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_fields = ('id', 'name', 'image', 'cooking_time',)


class UserWithRecipesSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit')
        if recipes_limit:
            recipes = obj.recipe.all()[:int(recipes_limit)]
        else:
            recipes = obj.recipe.all()
        return RecipeSubscribeSerializer(recipes, many=True, context={
            'request': self.context['request']}).data

    def get_recipes_count(self, obj):
        return obj.recipe.all().count()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')
