import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class LoadCommand(BaseCommand):
    def handle(self, *args, **options):
        with open('recipes/data/ingredients.csv', encoding='utf-8') as i:
            reader = csv.reader(i)
            for row in reader:
                name, measurement_unit = row
                Ingredient.objects.get_or_create(
                    name=name, measurement_unit=measurement_unit
                )