from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from api.paginatiors import ResponsePaginator
from users.constants import API_USER_INFO_NAME
from users.models import Subscribe
from users.serializers import UserWithRecipesSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    pagination_class = ResponsePaginator
    queryset = User.objects.prefetch_related('subscribing').all()

    def get_permissions(self):
        if self.action == API_USER_INFO_NAME:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @action(methods=['get'], detail=False, url_path='subscriptions',
            url_name='subscriptions', permission_classes=[IsAuthenticated])
    def subscriptions(self, request, *args, **kwargs):
        queryset = User.objects.filter(subscribing__user=self.request.user)

        page = self.paginate_queryset(queryset)
        serializer = UserWithRecipesSerializer(
            page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['post'], detail=True, url_path='subscribe',
            url_name='subscribe', permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        sub_candidate = get_object_or_404(User, pk=id)

        serializer = UserWithRecipesSerializer(
            sub_candidate, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        Subscribe.objects.create(user=request.user, subscribing=sub_candidate)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        subscriber = get_object_or_404(User, pk=id)
        try:
            subscription = Subscribe.objects.get(user=request.user,
                                                 subscribing=subscriber)
        except Subscribe.DoesNotExist:
            error_message = "запись не найдена"
            return Response({"errors": error_message},
                            status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
