import json

from django.core.management import BaseCommand
from django.db import transaction

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Наполнение БД первичными данными'

    def _import_ingredients(self):
        with open('static/data/ingredients.json') as f:
            data = json.load(f)
            Ingredient.objects.bulk_create([
                Ingredient(**i) for i in data])
        self.stdout.write('Ингридиенты успешно добавлены')

    @transaction.atomic
    def handle(self, *args, **options):
        self._import_ingredients()
