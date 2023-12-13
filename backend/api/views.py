from django.db.models import F
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated, \
    IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.paginatiors import ResponsePaginator
from api.permissions import IsOwnerOrReadOnly
from api.serializers import (TagSerializer, IngredientSerializer,
                             RecipeGetSerializer, RecipeSerializer)
from recipes.models import Tag, Ingredient, Recipe, Favorite, Cart
from users.serializers import RecipeSubscribeSerializer


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.prefetch_related('tags').select_related('author')
    pagination_class = ResponsePaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = [IsOwnerOrReadOnly | IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeGetSerializer
        return RecipeSerializer

    @action(methods=['post', 'delete'], detail=True, url_path='favorite',
            url_name='favorite', permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        user = request.user
        try:
            recipe = Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            error_message = "рецепт не найден"
            code = status.HTTP_400_BAD_REQUEST if request.method == "POST" \
                else status.HTTP_404_NOT_FOUND
            return Response({"errors": error_message},
                            status=code)

        recipe_in_favorite = user.favorite.filter(recipe=recipe)

        if request.method == "POST":
            if recipe_in_favorite:
                error_message = "рецепт уже добавлен в избранное"
                return Response({"errors": error_message},
                                status=status.HTTP_400_BAD_REQUEST)

            Favorite.objects.create(user=user, recipe=recipe)
            serializer = RecipeSubscribeSerializer(
                recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            if not recipe_in_favorite:
                error_message = "рецепт отсутствует в покупках"
                return Response({"errors": error_message},
                                status=status.HTTP_400_BAD_REQUEST)

            recipe_in_favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True, url_path='shopping_cart',
            url_name='shopping_cart', permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        user = request.user
        try:
            recipe = Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            error_message = "рецепт не найден"
            code = status.HTTP_400_BAD_REQUEST if request.method == "POST" \
                else status.HTTP_404_NOT_FOUND
            return Response({"errors": error_message},
                            status=code)

        recipe_in_shopping_cart = user.cart_recipe.filter(recipe=recipe)

        if request.method == "POST":
            if recipe_in_shopping_cart:
                error_message = "рецепт уже добавлен в покупки"
                return Response({"errors": error_message},
                                status=status.HTTP_400_BAD_REQUEST)

            Cart.objects.create(user=user, recipe=recipe)
            serializer = RecipeSubscribeSerializer(
                recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            if not recipe_in_shopping_cart:
                error_message = "рецепт отсутствует в покупках"
                return Response({"errors": error_message},
                                status=status.HTTP_400_BAD_REQUEST)
            recipe_in_shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False, url_path='download_shopping_cart',
            url_name='download_shopping_cart',
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        carts = Cart.objects.filter(user=user).values(
            name=F('recipe__ingredients__name'),
            amount=F('recipe__ingredient_amount__amount'),
            unit=F('recipe__ingredients__measurement_unit'))

        result = {}
        for i in carts:
            result[i['name']] = {
                'name': i['name'],
                'amount':
                    result.get(i['name'], {}).get('amount', 0) + i['amount'],
                'unit': i['unit']}

        content = ""
        for v in result.values():
            content += f"{v['name']} ({v['unit']}) — {v['amount']}\n"

        response = HttpResponse(content,
                                content_type='text/plain; charset=utf-8')
        response[
            'Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
        return response
