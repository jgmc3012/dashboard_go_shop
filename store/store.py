from django.contrib.auth import authenticate

import math
import logging
import os
import re

from decouple import config

from meli_sdk.sdk.meli import Meli
from .products.models import Product, Picture, Attribute
from store.models import BusinessModel


class Store(Meli):
    DIRECTION = config('STORE_DIRECTION')
    URI_CALLBACK = config('MELI_URI_CALLBACK')
    inventary = []
    sales = []
    pools = []
    queues = []

    def __init__(self, seller_id=None):
        super().__init__(seller_id)
        self._name_ = None
        self._attentive_user = None

    def init_properties(self):
        """
        Inicia los valores de la prodiedades que son obtenidas de la DB.
        """
        BM = BusinessModel.objects.get(pk=self.SELLER_ID)
        self._name_ = BM.name
        self._country_ = BM.country

    @property
    def currency(self):
        if not self._country_:
            self.init_properties()
        return self.get_currency(self._country_)
    
    @property
    def meli_code(self):
        if not self._country_:
            self.init_properties()
        return self.get_meli_code(self._country_)

    @property
    def name(self):
        if not self._name_:
            self.init_properties()
        return self._name_
    
    @property
    def country(self):
        if not self._country_:
            self.init_properties()
        return self._country_

    def delete_numbers(self, string):
        """
        Elimina los numero de un string
        """
        parent =  r'[\w/,]?\d+[\w/,]?'
        return re.sub(self.pattern,'', string)

    @property
    def attentive_user(self):
        if not self._attentive_user:
            username = config('ATTENTIVE_USER_NICK')
            password = config('ATTENTIVE_USER_PASS')
            self._attentive_user = authenticate(username=username,password=password)
        return self._attentive_user

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
        return self.update_items(
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

    def publish(self, product_store, price_usd, paused=True):
        product = product_store.product
        pictures = Picture.objects.filter(product=product)[:9]
        if not pictures:
            msg = f'El producto {product} no tiene imagenes asociadas'
            logging.warning(msg)
            return {
                'ok' : False,
                'msg': msg
            }

        attributes = Attribute.objects.filter(product=product)

        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(f'{dir_path}/templates/{self.name}.txt') as file:
            description= file.read()
            
        category = self.predict_category(
            title=f'{product.title} {product.category_name}',
            price=product_store.sale_price*price_usd
        )

        title = self.cut_title(product.title)
        if self.country == 've':
            title = self.delete_numbers(title)

        body = {
            "title": title,
            "category_id": category,
            "price":product_store.sale_price*price_usd,
            "available_quantity": 5 if product.quantity > 5 else product.quantity,
            "buying_mode":"buy_it_now",
            "condition":"new",
            "currency_id": self.currency,
            "listing_type_id":"gold_special",
            "description":{
                "plain_text": description.replace('product_description', product.description)
            },
            "pictures": [{"source": picture.src} for picture in pictures],
        }
        attr =  self.get_attributes(attributes)
        if attr:
            body["attributes"] = attr
        path = '/items'
        res = self.post(path, body=body, auth=True)
        if res.get('id'):
            product_store.sku = res.get('id')
            product_store.save()
            logging.info(f'{product}. Agregado con exito a la tienda')
            logging.debug(res)
            if paused:
                body = {
                   'status':'paused'
                }
                self.put(
                    path=f'{path}/{res.get("id")}',
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
        path = f'/sites/{self.meli_code}/category_predictor/predict'
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

    def get_attributes(self, attributes_draw:list):
        meli_values = {
            'marca': 'BRAND',
            'color': 'COLOR',
            'modelo': 'MODEL',
            'talla': 'SIZE',
        }
        attributes = list()
        for _attribute_ in attributes_draw:
            for id in meli_values:
                if id in _attribute_.id_meli:
                    attribute = {
                        'id': meli_values[id],
                        'value_name': _attribute_.value
                    }
                    attributes.append(attribute)
        return attributes