from django_filters.rest_framework import (CharFilter, FilterSet,
                                           ModelMultipleChoiceFilter,
                                           NumberFilter)

from recipes.models import Ingredient, Recipe, Tag

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

    class Meta:
        model = Recipe
        fields = ('author', 'tags')
