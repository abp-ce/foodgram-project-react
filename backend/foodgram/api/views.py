from django.db.utils import IntegrityError
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .serializers import (EmptyRecipeSerializer, IngredientSerializer,
                          RecipeForUserSerializer, RecipeIngredientSerializer,
                          RecipeReadSerializer, RecipeSerializer,
                          TagSerializer)
from core.filters import IngredientFilter, RecipeFilter
from core.utils import pdf_buffer
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ()
    filterset_class = RecipeFilter

    def get_queryset(self):
        fav = self.request.query_params.get('is_favorited', None)
        if fav == '1':
            if self.request.auth:
                ids = Favorite.objects.filter(
                    user=self.request.user
                ).values('recipe')
                return Recipe.objects.filter(pk__in=ids).all()
            else:
                return None
        cart = self.request.query_params.get('is_in_shopping_cart', None)
        if cart == '1':
            if self.request.auth:
                ids = ShoppingCart.objects.filter(
                    user=self.request.user
                ).values('recipe')
                return Recipe.objects.filter(pk__in=ids).all()
            else:
                return None
        return Recipe.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return RecipeSerializer
        elif self.action in ['favorite', 'shopping_cart']:
            return EmptyRecipeSerializer
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

    def action_template(self, request, pk, model):
        recipe = Recipe.objects.get(pk=pk)
        if request.method == 'DELETE':
            try:
                to_delete = get_object_or_404(
                    model,
                    user=request.user,
                    recipe=recipe
                )
                to_delete.delete()
            except IntegrityError as err:
                raise serializers.ValidationError({'errors': err})
            return Response(status=status.HTTP_204_NO_CONTENT)
        try:
            model.objects.create(
                user=request.user,
                recipe=recipe
            )
        except IntegrityError as err:
            raise serializers.ValidationError({'errors': err})
        serializer = RecipeForUserSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        return self.action_template(request, pk, Favorite)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        return self.action_template(request, pk, ShoppingCart)
