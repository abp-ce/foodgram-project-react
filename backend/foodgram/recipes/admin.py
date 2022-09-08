from django.contrib import admin
from django.db.models import Count

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 2


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    ordering = ('name',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorited_count', 'pub_date')
    list_filter = ('name', 'author', 'tags')
    ordering = ('name',)
    filter_horizontal = ('ingredients',)
    search_fields = ('name', 'author', 'tags')
    inlines = [RecipeIngredientInline]

    def favorited_count(self, obj):
        return obj._favorited_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # queryset = queryset.annotate(
        #     _favorited_count=Count("favorites"),
        # )
        return queryset.annotate(
            _favorited_count=Count("favorites"),
        )


admin.site.register(Tag)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)

# admin.site.register(RecipeIngredient)
