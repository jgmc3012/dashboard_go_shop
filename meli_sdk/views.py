from django.shortcuts import render, redirect
from .sdk.meli import Meli

from .sdk.meli import Meli
import logging
import csv
import threading
import requests
from concurrent.futures import ThreadPoolExecutor
import math
import json
from urllib.parse import urlencode
from decouple import config

results = list()
event = threading.Event()
API_MELI = "https://api.mercadolibre.com"
me_id=503380447
bad_sellers = {
    'YAXA': 163181195,
    'YAXACHINA': 221747504,
    'RANYAVE_IMPORTACIONES': 153822209,
    'LEFTIMPORTACIONES':302612225,
    'IMPORTADOS-USA-COLOMBIA':48695277,
    'RANYAVE IMPORTACIONES':153822209,
    'LATINPORT':244313028,
    'USA SHIPPING':132265535,
    'M.L IMPORT':354080066,
    'ADISCOLIMPORTADORES':101964722,
    'AMYTECHIMPORTACIONES':246148347,
    'IMPOR.GONZALEZ':438300617,
    'LEFTIMPORTACIONES':302612225,
    'AMYTECHIMPORTACIONES':246148347
    }

access_token = config('access_token_meli')

product_items = dict()
bad_products = list()
executor = ThreadPoolExecutor(max_workers=10)
bucle_n = 0

def request_meli(path, params):
    
    global access_token #PATH, executor,

    params['access_token'] = access_token #limit : 100

    res = requests.get(path,params=params) #path=PATH

    if res.status_code == 200:
        
        data = res.json()

        return data
    else:
        raise f'Error en la peticion a MercadoLibre {res}'

def push_items(items):
    global results
    lock = threading.Lock()
    with lock:
        results += items

def search_items(items_id, func_manager):
    global executor, event, product_items, bad_products

    path = f"{API_MELI}/items"
    iters = math.ceil(len(items_id)/20)
    ids = list()
    for i in range(iters):
        begin = 0 if i == 0 else begin+20
        end = begin+20 if i<(iters-1) else len(items_id)
        slice_products = [item for item in items_id[begin:end] ]
        ids.append(','.join(slice_products))

    executor.map(func_manager, [path]*(iters+1), ids, [len(items_id)]*(iters+1))
    event.wait()
    print(bad_products) #WARNING
    return product_items.copy(), bad_products.copy()

######################## MIS PUBLICACIONES ######################################
def get_items_for_seller(seller_id=me_id):
    global executor, results, event
    path = f"{API_MELI}/users/{seller_id}/items/search"
    limit_per_request = 100
    params = {
        'limit': limit_per_request,
        'search_type': 'scan',
    }

    data = request_meli(path, params)
    data_push_ids(data)
    total = data.get('paging').get('total')
    params['scroll_id'] = data.get('scroll_id')
    total_of_requests = math.ceil(total/limit_per_request) - 1 #Menos 1 porque ya se realizo una peticion
    
    for i in range(total_of_requests):
        data = request_meli(path,params)
        data_push_ids(data) 
    
    return results

def data_push_ids(data):
    global results, event
    items_ids = data.get('results')
    push_items(items_ids)
    total= data.get('paging').get('total')
    logging.info(f'({len(results)}/{total})')

######################## MCO DE MIS PUBLICACIONES ################################

def rq_products_by_id(path, ids, total):
    global product_items, event, bad_products
    products = request_meli(path, {
        'ids':ids,
        'attributes': 'attributes,id',
        'include_internal_attributes': True})
    
    for product in products:
        fine = False
        id = product.get('body').get('id')
        for attr in product.get('body').get('attributes'):
            if attr.get('id') == 'SELLER_SKU':
                fine = True
                mco = attr.get('value_name')
                product_items[id] = {
                    'mlv': id,
                    'mco': mco
                }
        if not fine:
            bad_products.append(id)

    current = len(product_items.keys())+len(bad_products)
    logging.info(f'({current}/{total}) de las productos completados.')
    
    if current>=total:
        event.set()

###################### OBTENER VALOR ###################################
len_stack_prices = 0
def get_prices_by_products(path, ids, total):
    global product_items, event, len_stack_prices, bad_products
    products = request_meli(path, {
        'ids':ids,
        'attributes': 'id,price'})
    
    count = 0
    for product in products:
        id = product.get('body').get('id')
        price = product.get('body').get('price')
        count += 1
        if not price:
            bad_products.append(id)
        else:
            product_items[id] = float(price)
    
    len_stack_prices += count
    logging.info(f'({len_stack_prices}/{total}) de las productos completados.')
    
    if len_stack_prices>=total:
        event.set()

def get_prices(products):
    global product_items,event, executor, bad_products
    executor = ThreadPoolExecutor(max_workers=10)
    product_items = dict()
    event.clear()
    bad_products = list()

    items = [products[key].get('mco').split('-')[0] for key in products.keys()]

    return search_items(items,get_prices_by_products)

##################       GET MCOS        #################################
def discard_items(data):
    global event, bad_sellers, bucle_n
    items = data.get('results')
    
    mcos = [ item.get('id') for item in items if not (item.get('seller').get('id') in bad_sellers.values())]
    
    push_items(mcos)
    bucle_n += 1
    logging.info(f'Progreso ({bucle_n}/200)')
    if (bucle_n == 200):
        event.set()

def get_mcos(category):
    global API_MELI, executor, results, event, bucle_n
    results = list()
    event.clear()
    bucle_n = 0

    url = f'{API_MELI}/sites/MCO/search'
    params = {
        'condition': 'new',
        'offset': 0,
        'search_type': 'scan',
        'category':category,
        'power_seller': 'yes',
        'shipping_cost': 'free',
        'attributes': 'paging,results'
    }

    for i in range(10000//50):
        params['offset'] = i*50
        future = executor.submit(request_meli, url, params.copy())
        future.add_done_callback(
            lambda future: discard_items(future.result())
        )
    event.wait()
    return results

###################### ACTUALIZAR PRECIOS ###################################

def update_publication(item_id, index, total, kwargs):
    global event

    body = dict()

    for key in kwargs.keys():
        body[key] = kwargs.get(key)
    url = f"{API_MELI}/items/{item_id}"
    params = {
        'access_token': access_token
    }
    headers = {'Accept': 'application/json', 'Content-type':'application/json'}
    
    body = json.dumps(body)
    
    response = requests.put(url, data=body, params=urlencode(params), headers=headers)
    
    if response.status_code == 200:
        logging.info(f'Producto {item_id} actualizado. numero {index+1}')
        if (index+1) == total:
            event.set()
    else:
        logging.error(response.status_code)
        logging.error(response.message)
        raise f'Error in Request {response.status_code}'
    
def update_produtcs(products:list):
    global executor, event

    ids = [product.get('mlv') for product in products]
    price = [{'price': product.get('price')} for product in products]

    executor.map(update_publication, ids, range(len(products)), [len(products)]*len(products),price)
    event.wait()