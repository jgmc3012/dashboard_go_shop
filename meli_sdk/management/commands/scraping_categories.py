from django.core.management.base import BaseCommand, CommandError

import logging

from meli_sdk.sdk.scraper import ScraperCategory


class Command(BaseCommand):
    help = 'Scrapea el path por categorias hasta aquellas con menos de 9.000 items'


    def add_arguments(self, parser):
        parser.add_argument('--category_id', type=str)

    def handle(self, *args, **options):
        scraper = ScraperCategory()
        category = options['category_id']
        scraper.scraping_path(category)