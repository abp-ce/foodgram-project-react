from rest_framework import serializers

from core.fields import Base64ImageField, Hex2NameColor
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    color = Hex2NameColor(read_only=True)
    name = serializers.ReadOnlyField()
    slug = serializers.ReadOnlyField()

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.ReadOnlyField(
        source='measurement_unit.name'
    )

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit.name',
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class EmptyRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Recipe
        fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=False)
    ingredients = RecipeIngredientSerializer(source='recipe_ingredient',
                                             many=True)
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        if self.context.get('request').auth:
            return obj.favorites.filter(
                user=self.context.get('request').user
            ).count() != 0
        return False

    def get_is_in_shopping_cart(self, obj):
        if self.context.get('request').auth:
            return obj.shoppingcarts.filter(
                user=self.context.get('request').user
            ).count() != 0
        return False

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredient')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            recipe.tags.add(tag)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(**ingredient['ingredient']),
                amount=ingredient['amount']
            )
        self.fields['tags'] = TagSerializer(many=True)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get(
            'cooking_time'
            )
        instance.image = validated_data.get('image')

        RecipeIngredient.objects.filter(recipe=instance).all().delete()
        ingredients = validated_data.pop('recipe_ingredient')
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=Ingredient.objects.get(
                    **ingredient['ingredient']
                ),
                amount=ingredient['amount']
            )

        instance.tags.clear()
        tags = validated_data.pop('tags')
        for tag in tags:
            instance.tags.add(tag)

        instance.save()
        self.fields['tags'] = TagSerializer(many=True)
        return instance


class RecipeReadSerializer(RecipeSerializer):
    tags = TagSerializer(many=True)


class RecipeForUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class UserWithRecipesSerializer(UserSerializer):
    recipes = RecipeForUserSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if 'recipes_limit' in self.context and self.context['recipes_limit']:
            ret['recipes'] = ret['recipes'][:self.context['recipes_limit']]
        return ret
