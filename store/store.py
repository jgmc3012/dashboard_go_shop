from meli_sdk.sdk.meli import Meli
from decouple import config
import math
import logging
from .products.models import Product, Picture, Attribute
import os
import re

from dollar_for_life.models import History
from store.models import BusinessModel, BadWord

class Store(Meli):
    DIRECTION = config('STORE_DIRECTION')
    URI_CALLBACK = config('MELI_URI_CALLBACK')
    inventary = []
    sales = []
    pools = []
    queues = []

    def __init__(self, seller_id=None):
        if seller_id:
            self.SELLER_ID = seller_id
        else:
            self.SELLER_ID = config('MELI_ME_ID')
        super().__init__(self.SELLER_ID)
        words = BadWord.objects.all().values_list('word', flat=True)
        words = [ f'({word.upper()})' for word in words]
        self.pattern_bad_words = '|'.join(words)

    def get_inventory_by_api(self)->list:
        """
        Retorna un lista con todos los sku de los productos publicados en la tienda
        """
        inventory = list()
        path = f"/users/{self.SELLER_ID}/items/search"
        limit_per_request = 100
        params = {
            'access_token': self.access_token,
            'limit': limit_per_request,
            'search_type': 'scan',
        }

        data = self.get(path, params)
        total = data.get('paging').get('total')
        params['scroll_id'] = data.get('scroll_id')
        inventory += data.get('results')
        total_of_requests = math.ceil(total/limit_per_request) - 1 #Menos 1 porque ya se realizo una peticion
    
        for i in range(total_of_requests):
            data = self.get(path,params)
            inventory += data.get('results')
            logging.info(f'Productos cargados ({len(inventory)}/{total})')    

        return inventory

    def get_mcos_by_api(self,skus):
        products = {
            'fine':dict(),
            'bad':list()
        }
        path='/items'
        params = {
            'access_token': self.access_token,
            'attributes': 'attributes,id',
            'include_internal_attributes': True
        }
        products_draw = self.search_items(skus, path, params)
        for product in products_draw:
            bad = True
            id = product.get('body').get('id')
            for attr in product.get('body').get('attributes'):
                if attr.get('id') == 'SELLER_SKU':
                    bad = False
                    mco = attr.get('value_name')
                    products.get('fine')[id] = {
                        'mlv': id,
                        'mco': mco,
                    }
            if bad:
                products.get('bad').append(id)
        return products

    def get_product_by_api(self, skus):
        products = {
            'fine':dict(),
            'bad':list()
        }
        path='/items'
        params = {
            'access_token': self.access_token,
            'attributes': 'id,price,seller_id,thumbnail,title',
        }
        
        products_draw = self.search_items(skus, path, params)
        
        for product_draw in products_draw:
            product = product_draw.get('body')
            sku = product.get('id')
            product_push = {
                'sku': sku,
                'price': product.get('price'),
                'seller_id': product.get('seller_id'),
                'title': product.get('title'),
                'image': product.get('thumbnail'),
            }

            if not product.get('price'):
                products.get('bad').append(sku)
            else:
                products.get('fine')[sku] = product_push
        
        return(products)

    def get_seller_for_api(self, seller_ids):
        
        path='/users'
        params = {'attributes': 'id,nickname,'}
        sellers_draw = self.search_items(seller_ids, path, params)
        sellers = [seller.get('body') for seller in sellers_draw]
        return sellers

    def publications_pauser(self, ids_publications):
        body = {
            'status':'paused'
        }
        self.update_items(
            ids_list=ids_publications,
            bodys=[body]*len(ids_publications)
        )

    def verify_existence(self, product):
        sku = product.provider_sku
        product_draw = self.get_product_by_api([sku])
        product_api = product_draw.get('fine').get(sku)
        if not product_api.get('price'):
            return {
                'ok':False,
                'msg': 'El producto esta agotado.'
            }
        return {
                'ok':True,
                'msg': 'Todo okey!'
            }
    def publish(self, product, paused=True):
        if product.sku:
            return {
                'ok': True,
                'data': product
            }

        if re.search(self.pattern_bad_words, product.title.upper()):
            msg = f'{product.title} no publicado. Contiene palabras prohibidas.'
            logging.warning(msg)
            product.available = False
            product.save()
            return {
                'ok': False,
                'msg': msg
            }
        USD = History.objects.order_by('-datetime').first()
        BM = BusinessModel.objects.get(pk=self.SELLER_ID)
        price_usd = USD.rate + BM.usd_variation

        pictures = Picture.objects.filter(product=product)
        if not pictures:
            msg = f'El producto {product} no tiene imagenes asociadas'
            logging.warning(msg)
            return {
                'ok' : False,
                'msg': msg
            }

        attributes = Attribute.objects.filter(product=product)

        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(f'{dir_path}/templates/goshop.txt') as file:
            description= file.read()
        category = self.predict_category(
            title=product.title,
            category_from=f'MLV{product.category.id}',
            price=product.sale_price*price_usd
        )
        pattern = r'[\w/,]?\d+[\w/,]?'

        body = {
            "title": re.sub(pattern,'',product.title),
            "category_id": category,
            "price":product.sale_price*price_usd,
            "available_quantity": 5 if product.quantity > 5 else product.quantity,
            "buying_mode":"buy_it_now",
            "condition":"new",
            "currency_id": "VES",
            "listing_type_id":"gold_special",
            "description":{
                "plain_text": description
            },
            "pictures": [{"source": picture.src} for picture in pictures],
            "attributes": [{
                'id': attribute.id_meli,
                'value_name':attribute.value,
                'value_id':attribute.value_id
                } for attribute in attributes]
        }
        path = '/items'
        res = self.post(path, body=body, auth=True)
        if res.get('id'):
            product.sku = res.get('id')
            product.save()
            logging.info(f'{product.title}. Agregado con exito a la tienda')
            logging.debug(res)
            if paused:
                body = {
                   'status':'paused'
                }
                self.put(
                    path=f'{path}/{product.sku}',
                    body=body,
                )
            return {
                'ok': True,
                'data': product
            }
        else:
            return {
                'ok': False,
                'msg': 'Error en la peticion a mercadolibre',
                'data': res
            }
        
    def predict_category(self, title, category_from=None,price=None):
        path = '/sites/MLV/category_predictor/predict'
        params = {
            'title': title
        }
        if self.seller_id:
            params['seller_id'] = self.seller_id
        if category_from:
            params['category_from'] = category_from
        if price:
            params['price'] = price

        category = self.get(path, params)
        return category['id']