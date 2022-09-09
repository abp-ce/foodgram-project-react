from django_filters.rest_framework import (CharFilter, FilterSet,
                                           ModelMultipleChoiceFilter,
                                           NumberFilter)

from core.utils import filter_template
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag

BOOLEAN_CHOICES = (
    (0, False),
    (1, True),
)


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    author = NumberFilter(field_name='author__id', lookup_expr='exact')
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = NumberFilter(field_name='is_favorited',
                                method='is_favorited_filter')
    is_in_shopping_cart = NumberFilter(field_name='is_in_shopping_cart',
                                       method='is_in_shopping_cart_filter')

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def is_favorited_filter(self, queryset, name, value):
        return filter_template(self.request, queryset, Favorite, value)

    def is_in_shopping_cart_filter(self, queryset, name, value):
        return filter_template(self.request, queryset, ShoppingCart, value)
