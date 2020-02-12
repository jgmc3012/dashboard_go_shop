from django.core.management.base import BaseCommand, CommandError

import logging

from meli_sdk.sdk.scraper import ScraperCategory
from store.products.models import Category

class Command(BaseCommand):
    help = 'Scrapea el path por categorias hasta aquellas con menos de 9.000 items'


    def add_arguments(self, parser):
        parser.add_argument('--category_id', type=str)

    def handle(self, *args, **options):
        scraper = ScraperCategory()
        category = options['category_id']
        if category:
            scraper.scraping_path(category)
        else:
            categories = [
                {
                    "id": "MCO1747",
                    "name": "Accesorios para Vehículos"
                },
                {
                    "id": "MCO1368",
                    "name": "Arte, Papelería y Mercería"
                },
                {
                    "id": "MCO1384",
                    "name": "Bebés"
                },
                {
                    "id": "MCO1039",
                    "name": "Cámaras y Accesorios"
                },
                {
                    "id": "MCO1051",
                    "name": "Celulares y Teléfonos"
                },
                {
                    "id": "MCO1648",
                    "name": "Computación"
                },
                {
                    "id": "MCO1144",
                    "name": "Consolas y Videojuegos "
                },
                {
                    "id": "MCO1276",
                    "name": "Deportes y Fitness"
                },
                {
                    "id": "MCO5726",
                    "name": "Electrodomésticos"
                },
                {
                    "id": "MCO1000",
                    "name": "Electrónica, Audio y Video"
                },
                {
                    "id": "MCO175794",
                    "name": "Herramientas y Construcción"
                },
                {
                    "id": "MCO1499",
                    "name": "Industrias y Oficinas"
                },
                {
                    "id": "MCO1182",
                    "name": "Instrumentos Musicales"
                },
                {
                    "id": "MCO1132",
                    "name": "Juegos y Juguetes"
                },
                {
                    "id": "MCO3025",
                    "name": "Libros, Revistas y Comics"
                },
                {
                    "id": "MCO1168",
                    "name": "Música, Películas y Series"
                },
                {
                    "id": "MCO118204",
                    "name": "Recuerdos y Fiestas"
                },
                {
                    "id": "MCO3937",
                    "name": "Relojes y Joyas"
                },
                {
                    "id": "MCO1430",
                    "name": "Ropa y Accesorios"
                },
                {
                    "id": "MCO1953",
                    "name": "Otras categorías"
                }
            ]

            for category in categories:
                if not Category.objects.filter(id=int(category['id'][3:])).first():
                    Category.objects.create(
                        id=int(category['id'][3:]),
                        name=category['name']
                    )
                scraper.scraping_path(category['id'])
