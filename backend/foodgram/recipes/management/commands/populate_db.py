import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Measurement


class Command(BaseCommand):
    help = 'Заполняет таблицу из csv файла'

    def add_arguments(self, parser):
        # parser.add_argument('tables', nargs='+', type=str)
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Удаляет строки в таблице, которые есть в csv',
        )

    def handle(self, *args, **options):
        if options['delete']:
            Ingredient.objects.all().delete()
            Measurement.objects.all().delete()
            return
        with open('./data/ingredients.json', 'r') as f:
            ings = json.load(f)
        for ing in ings:
            unit, _ = Measurement.objects.get_or_create(
                name=ing['measurement_unit']
            )
            _, _ = Ingredient.objects.get_or_create(
                name=ing['name'],
                measurement_unit=unit
            )
