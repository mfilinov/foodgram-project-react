from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from users.models import Subscribe
from users.paginatiors import UserPaginator
from users.serializers import UserWithRecipesSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    pagination_class = UserPaginator
    queryset = User.objects.prefetch_related('subscribing').all()

    def get_permissions(self):
        if self.action == 'me':
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

    @action(methods=['post', 'delete'], detail=True, url_path='subscribe',
            url_name='subscribe', permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        sub_candidate = get_object_or_404(User, pk=id)

        if user == sub_candidate:
            error_message = "пользователь не может быть подписан сам на себя"
            return Response({"errors": error_message},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == "POST":
            if user.subscriber.filter(subscribing_id=id).exists():
                error_message = "пользователь уже подписан"
                return Response({"errors": error_message},
                                status=status.HTTP_400_BAD_REQUEST)
            Subscribe.objects.create(user=user, subscribing=sub_candidate)
            serializer = UserWithRecipesSerializer(sub_candidate, context={
                'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            sub_obj = Subscribe.objects.filter(user=user,
                                               subscribing=sub_candidate)
            if not sub_obj:
                error_message = "вы не подписаны на указанного пользователя"
                return Response({"errors": error_message},
                                status=status.HTTP_400_BAD_REQUEST)
            sub_obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
