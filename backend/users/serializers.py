from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateMixin
from rest_framework import serializers

from recipes.models import Recipe
from users.constants import USER_PASSWORD_MAX_LENGTH

User = get_user_model()


class UserCreateSerializer(UserCreateMixin, serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"},
                                     write_only=True,
                                     max_length=USER_PASSWORD_MAX_LENGTH)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password')
        read_only_fields = ('id',)


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

    def validate(self, data):
        user = self.context['request'].user
        sub_candidate = self.instance
        if user == sub_candidate:
            raise serializers.ValidationError(
                {'errors': 'пользователь не может быть подписан сам на себя'})

        if user.subscriber.filter(subscribing_id=sub_candidate.id).exists():
            raise serializers.ValidationError(
                {"errors": "пользователь уже подписан"})

        return data

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')
