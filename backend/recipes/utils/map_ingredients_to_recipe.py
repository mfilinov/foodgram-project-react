from recipes.models import RecipeIngredient


def map_ingredients_to_recipe(ingredients, recipe):
    RecipeIngredient.objects.bulk_create([
        RecipeIngredient(
            recipe=recipe,
            ingredient_id=i['id'],
            amount=i['amount'],
        )
        for i in ingredients])
