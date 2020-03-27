from django.core.management.base import BaseCommand, CommandError

from meli_sdk.sdk.scraper import ScraperCategory
from store.products.models import Category

class Command(BaseCommand):
    help = 'Scrapea el path por categorias hasta aquellas con menos de 9.000 items'


    def add_arguments(self, parser):
        parser.add_argument('--category_id', type=str)
        parser.add_argument('--code-meli', type=str) #MLM, MCO, MLV...

    def handle(self, *args, **options):
        scraper = ScraperCategory()
        category = options['category_id']
        country_meli = options['code_meli']
        if category:
            scraper.scraping_path(category)
        else:
            categories = scraper.get(f'sites/{country_meli.upper()}/categories')
            for category in categories:
                if not Category.objects.filter(id_meli=int(category['id'][3:])).first():
                    Category.objects.create(
                        id_meli=int(category['id'][3:]),
                        name=category['name']
                    )
                scraper.scraping_path(category['id'])