from django.core.management.base import BaseCommand, CommandError

import logging

from store.products.models import Category, Product

def bad_category(category, bad_categories=list()):
    category.bad_category= True
    category.save()
    bad_categories.append(category.id)
    logging.info(f'Bad Category {category}')
    categories = Category.objects.filter(parent=category)
    for category in categories:
        bad_category(category, bad_categories)
    return bad_categories

class Command(BaseCommand):
    help = 'Recibe un id de categoria y deshabilita todo el path de childrens'


    def add_arguments(self, parser):
        parser.add_argument('--category_id', type=int)

    def handle(self, *args, **options):
        bad_categories = list()
        category_id = options['category_id']
        category = Category.objects.filter(id=category_id).first()
        if category:
            bad_categories = bad_category(category)
            products = Product.objects.filter(category__in=bad_categories).update(available=False)
            logging.info(f'{products} Productos prohibidos')