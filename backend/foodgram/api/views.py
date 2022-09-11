from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeForUserSerializer, RecipeIngredientSerializer,
                          RecipeReadSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer)
from core.filters import IngredientFilter, RecipeFilter
from core.permissions import IsOwnerOrReadOnly
from core.utils import pdf_buffer
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = [AllowAny]
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = [AllowAny]
    serializer_class = IngredientSerializer
    pagination_class = None
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly & IsOwnerOrReadOnly]
    filterset_fields = ()
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return RecipeSerializer
        elif self.action in ['favorite', 'shopping_cart']:
            return serializers.Serializer
        elif self.action in ['download_shopping_cart']:
            return IngredientSerializer

        return RecipeReadSerializer

    @action(methods=['get'], detail=False,
            permission_classes=[IsAuthenticated],
            pagination_class=None, filterset_fields=None)
    def download_shopping_cart(self, request):
        shoppingcarts = request.user.shoppingcarts.all()
        recipe_ingredient_list = []
        for shoppingcart in shoppingcarts:
            for ingredient in shoppingcart.recipe.recipe_ingredient.all():
                recipe_ingredient_list.append(
                    RecipeIngredientSerializer(ingredient).data
                )

        return FileResponse(pdf_buffer(recipe_ingredient_list),
                            as_attachment=True, filename='recipe.pdf')

    def paginate_template(self, recipes_list):
        page = self.paginate_queryset(recipes_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def action_template(self, request, pk, model, serializer):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'DELETE':
            get_object_or_404(
                model,
                user=request.user,
                recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        ser = serializer(data={'user': request.user.pk, 'recipe': recipe.pk})
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(
            RecipeForUserSerializer(recipe).data,
            status=status.HTTP_200_OK
        )

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated & IsOwnerOrReadOnly])
    def favorite(self, request, pk):
        return self.action_template(request, pk, Favorite, FavoriteSerializer)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated & IsOwnerOrReadOnly])
    def shopping_cart(self, request, pk):
        return self.action_template(request, pk, ShoppingCart,
                                    ShoppingCartSerializer)
