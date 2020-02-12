from django.core.management.base import BaseCommand, CommandError

import logging

from meli_sdk.sdk.scraper import Scraper
from store.products.models import Category

class Command(BaseCommand):
    help = 'Scrapea el path por categorias hasta aquellas con menos de 9.000 items'


    def add_arguments(self, parser):
        parser.add_argument('--category_id', type=str)

    def handle(self, *args, **options):
        scraper = Scraper()
        category_id = options['category_id']
        if category_id:
            category = Category.objects.filter(id=int(category_id)).first()
            if category:
                scraper.scan_for_category(category)
            else:
                logging.info('Categria invalida')
        else:
            categories_ids = [
                # 1747,   # "name": "Accesorios para Vehículos"
                # 1368,   # "name": "Arte, Papelería y Mercería"
                # 1384,   # "name": "Bebés"
                # 1039,   # "name": "Cámaras y Accesorios"
                # 1051,   # "name": "Celulares y Teléfonos"
                # 1648,   # "name": "Computación"
                # 1144,   # "name": "Consolas y Videojuegos "
                # 1276,   # "name": "Deportes y Fitness"
                # 5726,   # "name": "Electrodomésticos"
                # 1000,   # "name": "Electrónica, Audio y Video"
                # 175794, # "name": "Herramientas y Construcción"
                # 1499,   # "name": "Industrias y Oficinas"
                1182,   # "name": "Instrumentos Musicales"
                # 1132,   # "name": "Juegos y Juguetes"
                # 3025,   # "name": "Libros, Revistas y Comics"
                # 1168,   # "name": "Música, Películas y Series"
                # 118204, # "name": "Recuerdos y Fiestas"
                # 3937,   # "name": "Relojes y Joyas"
                # 1430,   # "name": "Ropa y Accesorios"
                # 1953,   # "name": "Otras categorías"
            ]

            categories = Category.objects.filter(id__in=categories_ids)
            for category in categories:
                scraper.scan_for_category(category)