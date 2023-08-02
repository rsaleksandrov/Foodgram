import csv

from django.core.management.base import BaseCommand, CommandParser

from ingredients.models import Ingredient

TABLE_NAME = 'ingredients_ingredient'


class Command(BaseCommand):
    help = 'Load ingredients list from csv file'

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            'args', nargs='+', help='CSV file name', metavar='csv-file-name'
        )

    def handle(self, *args, **options):
        for file in args:
            with open(file, 'r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)
                for row in reader:
                    Ingredient.objects.get_or_create(
                        name=row[0], measurement_unit=row[1]
                    )
            print(f'The data from the "{file}" has been uploaded successfully')
