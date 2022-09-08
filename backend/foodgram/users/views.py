from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Follow, User
from .serializers import EmptyUserSerializer
from api.serializers import UserWithRecipesSerializer


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
            page,
            many=True,
            context={
                'request': request,
                'recipes_limit': recipes_limit
            }
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated],
            serializer_class=EmptyUserSerializer)
    def subscribe(self, request, id):
        author = User.objects.get(pk=id)
        if request.method == 'DELETE':
            try:
                to_delete = get_object_or_404(
                    Follow,
                    user=request.user,
                    author=author
                )
                to_delete.delete()
            except IntegrityError as err:
                raise serializers.ValidationError({'errors': err})
            return Response(status=status.HTTP_204_NO_CONTENT)
        try:
            Follow.objects.create(
                user=request.user,
                author=author
            )
        except IntegrityError as err:
            raise serializers.ValidationError({'errors': err})
        serializer = UserWithRecipesSerializer(
            author,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
