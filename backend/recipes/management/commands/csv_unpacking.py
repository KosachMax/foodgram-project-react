import csv

from django.core.management import BaseCommand

from api.models import Ingredient

FILE_PATH = '/Users/mac/Diploma/foodgram-project-react/data/ingredients.csv'

Model_to_csv = {
    Ingredient: 'ingredients.csv',
}


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for model, csv_file in Model_to_csv.items():
            with open(
                    FILE_PATH,
                    'r',
                    encoding='utf-8',
            ) as csv_files:
                reader = csv.DictReader(csv_files)
                model.objects.bulk_create(
                    model(**data) for data in reader
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        'Готово! Данные уже в модели'
                    )
                )