from django.db.models import F
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
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

    @action(methods=['post'], detail=True, url_path='favorite',
            url_name='favorite', permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        return self.add(request, pk, Favorite)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return self.delete_obj(request, pk, Favorite)

    @action(methods=['post'], detail=True, url_path='shopping_cart',
            url_name='shopping_cart', permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return self.add(request, pk, Cart)

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, pk):
        return self.delete_obj(request, pk, Cart)

    @staticmethod
    def delete_obj(request, pk, model):
        recipe = get_object_or_404(Recipe, pk=pk)
        obj = model.objects.filter(user=request.user, recipe=recipe)
        if not obj:
            error_message = "рецепт отсутствует"
            return Response({"errors": error_message},
                            status=status.HTTP_400_BAD_REQUEST)

        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def add(request, pk, model):
        user = request.user
        try:
            recipe = Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            error_message = "рецепт не найден"
            return Response({"errors": error_message},
                            status=status.HTTP_400_BAD_REQUEST)

        if model.objects.filter(user=user, recipe=recipe).exists():
            error_message = "рецепт уже добавлен"
            return Response({"errors": error_message},
                            status=status.HTTP_400_BAD_REQUEST)

        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeSubscribeSerializer(
            recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
