from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Follow, User
from .serializers import FollowSerializer
from api.serializers import UserWithRecipesSerializer
from core.permissions import IsOwnerOrReadOnly


class FoodgramUserViewSet(UserViewSet):

    @action(methods=['get'], detail=False,
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        followers = request.user.follower.all()
        user_list = []
        for follower in followers:
            user_list.append(follower.author)

        r_l = request.query_params.get('recipes_limit', None)
        if r_l is not None:
            try:
                recipes_limit = int(r_l)
            except ValueError:
                recipes_limit = None
        else:
            recipes_limit = None

        page = self.paginate_queryset(user_list)
        if page is not None:
            serializer = UserWithRecipesSerializer(
                page,
                many=True,
                context={
                    'request': request,
                    'recipes_limit': recipes_limit
                }
            )
            return self.get_paginated_response(serializer.data)

        serializer = UserWithRecipesSerializer(
            user_list,
            many=True,
            context={
                'request': request,
                'recipes_limit': recipes_limit
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated & IsOwnerOrReadOnly],
            serializer_class=serializers.Serializer)
    def subscribe(self, request, id):
        author = get_object_or_404(User, pk=id)
        if request.method == 'DELETE':
            get_object_or_404(
                Follow,
                user=request.user,
                author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        ser = FollowSerializer(data={'user': request.user.pk,
                               'author': author.pk})
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(
            UserWithRecipesSerializer(
                author,
                context={'request': request}
            ).data,
            status=status.HTTP_200_OK
        )
