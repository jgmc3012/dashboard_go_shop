from configparser import SafeConfigParser
from .ssl_helper import SSLAdapter
from urllib.parse import urlencode
import json
import os
import re
import requests
import ssl
from meli_sdk.models import Token
from datetime import timedelta
from django.utils import timezone
from concurrent.futures import ThreadPoolExecutor
import threading
import math
import logging
from decouple import config


class Meli(object):
    def __init__(self, seller_id=None):
        self.client_secret = config('MELI_SECRET_KEY')
        self.client_id = config('MELI_APP_ID')
        self.limit_ids_per_request = 20
        self.max_workers = 5
        self.seller_id = seller_id
        try:
            self.token = Token.objects.get(seller_id=seller_id)
        except Token.DoesNotExist:
            self.token = None

        parser = SafeConfigParser()
        parser.read(os.path.dirname(os.path.abspath(__file__))+'/config.ini')

        self.API_ROOT_URL = parser.get('config', 'api_root_url')
        self.SDK_VERSION = parser.get('config', 'sdk_version')
        self.AUTH_URL = parser.get('config', 'auth_url')
        self.OAUTH_URL = parser.get('config', 'oauth_url')
        self._requests = requests.Session()
        try:
            self.SSL_VERSION = parser.get('config', 'ssl_version')
            self._requests.mount('https://', SSLAdapter(ssl_version=getattr(ssl, self.SSL_VERSION)))
        except:
            self._requests = requests


    #AUTH METHODS
    def auth_url(self,redirect_URI=None):
        params = {'client_id':self.client_id,'response_type':'code'}
        if redirect_URI:
            params['redirect_uri'] = redirect_URI
        url = self.AUTH_URL  + '/authorization' + '?' + urlencode(params)
        return url

    def authorize(self, code, redirect_URI):
        params = {
            'grant_type' : 'authorization_code',
            'client_id' : self.client_id,
            'client_secret' : self.client_secret,
            'code' : code,
            'redirect_uri' : redirect_URI
        }
        headers = {
            'Accept': 'application/json',
            'User-Agent':self.SDK_VERSION,
            'Content-type':'application/json'
        }
        uri = self.make_path(self.OAUTH_URL)

        response = self._requests.post(uri, params=urlencode(params), headers=headers)
        if response.ok:
            response_info = response.json()
            access_token = response_info['access_token']
            if 'refresh_token' in response_info:
                refresh_token = response_info['refresh_token']
            else:
                refresh_token = '' # offline_access not set up
            
            seg = response_info['expires_in']
            expiration = timezone.now() + timedelta(seconds=seg)
            if self.token:
                self.token.access_token = access_token
                self.token.refresh_token = refresh_token
                self.token.expiration = expiration
            else:                
                self.token = Token(
                    access_token=access_token,
                    refresh_token=refresh_token,
                    expiration=expiration,
                    seller_id=self.seller_id
                )
            self.token.save()
        else:
            # response code isn't a 200; raise an exception
            response.raise_for_status()

    def get_refresh_token(self):
        if self.refresh_token:
            params = {
                'grant_type' : 'refresh_token',
                'client_id' : self.client_id,
                'client_secret' : self.client_secret,
                'refresh_token' : self.refresh_token
            }
            headers = {
                'Accept': 'application/json',
                'User-Agent':self.SDK_VERSION,
                'Content-type':'application/json'
            }
            uri = self.make_path(self.OAUTH_URL)

            response = self._requests.post(
                uri, params=urlencode(params),
                headers=headers,
                data=params
            )

            if response.ok:
                response_info = response.json()
                seg = response_info['expires_in']
                expiration = timezone.now() + timedelta(seconds=seg)
                self.token.access_token = response_info['access_token']
                self.token.refresh_token = response_info['refresh_token']
                self.token.expiration = expiration
                self.token.save()

            else:
                # response code isn't a 200; raise an exception
                response.raise_for_status()
        else:
            raise Exception("Offline-Access is not allowed.")

    # REQUEST METHODS
    def get(self, path, params=None, extra_headers=None, auth=False):
        params = params or {}
        if auth:
            params['access_token']=self.access_token
        headers = {
            'Accept': 'application/json',
            'User-Agent':self.SDK_VERSION,
            'Content-type':'application/json'
        }
        if extra_headers:
            headers.update(extra_headers)
        uri = self.make_path(path)
        response = self._requests.get(uri, params=urlencode(params), headers=headers)
        if response.status_code == 200:
            return response.json()
        
        #### Esto debe ser un decorador
        elif response.status_code == 401:
            token = Token.objects.get(app_id=client_id)
            if token.expiration > self.token.expiration:
                self.token = token
            else:
                self.refresh_token()
            return self.get(path,params, extra_headers)

        elif response.status_code == 404:
            return response.json()
        else:
            raise Exception('Error en peticion personalizar mensaje')

    def post(self, path, body=None, params=None, extra_headers=None, auth=False):
        params = params or {}
        if auth:
            params['access_token']=self.access_token
        headers = {
            'Accept': 'application/json',
            'User-Agent':self.SDK_VERSION,
            'Content-type':'application/json'
        }
        if extra_headers:
            headers.update(extra_headers)
        uri = self.make_path(path)
        if body:
            body = json.dumps(body)

        response = self._requests.post(
            uri, data=body, params=urlencode(params), headers=headers
        )
        if response.status_code != 200:
            logging.warning(f'Status Code:{response.status_code} en {uri}')

        return response.json()

    def put(self, path, body=None, params=None, extra_headers=None):
        params = params or {}
        headers = {
            'Accept': 'application/json',
            'User-Agent':self.SDK_VERSION,
            'Content-type':'application/json'
        }
        if extra_headers:
            headers.update(extra_headers)
        uri = self.make_path(path)
        if body:
            body = json.dumps(body)

        response = self._requests.put(
            uri, data=body, params=urlencode(params), headers=headers
        )
        if response.status_code != 200:
            logging.warning(f'Status Code:{response.status_code} en {uri}. Respuesta:{response.json()}')

        return response.json()

    def delete(self, path, params=None, extra_headers=None):
        params = params or {}
        headers = {
            'Accept': 'application/json',
            'User-Agent':self.SDK_VERSION,
            'Content-type':'application/json'
        }
        if extra_headers:
            headers.update(extra_headers)
        uri = self.make_path(path)
        response = self._requests.delete(uri, params=params, headers=headers)
        return response

    def options(self, path, params=None, extra_headers=None):
        params = params or {}
        headers = {
            'Accept': 'application/json',
            'User-Agent':self.SDK_VERSION,
            'Content-type':'application/json'
        }
        if extra_headers:
            headers.update(extra_headers)
        uri = self.make_path(path)
        response = self._requests.options(
            uri, params=urlencode(params), headers=headers
        )
        return response

    def make_path(self, path, params=None):
        params = params or {}
        # Making Path and add a leading / if not exist
        if not (re.search("^\/", path)):
            path = "/" + path
        path = self.API_ROOT_URL + path
        if params:
            path = path + "?" + urlencode(params)

        return path

    @property
    def access_token(self):
        if self.token:
            if self.token.expiration < (timezone.now()+timedelta(seconds=30)):
                self.get_refresh_token()
            return self.token.access_token
        else:
            raise Exception('Debe Autentificarse manualmente en el portal')

    @property
    def refresh_token(self):
        if self.token:
            return self.token.refresh_token
        else:
            raise Exception('Debe Autentificarse manualmente en el portal')

    def split_ids(self, items_id):
        items_id = tuple(items_id)# Para hacerlos suscribible, ya que puede llegar cualquier iterable.

        iters = math.ceil(len(items_id)/self.limit_ids_per_request)
        ids_list = list()
        for i in range(iters):
            begin = 0 if i == 0 else begin+self.limit_ids_per_request
            end = begin+self.limit_ids_per_request if i<(iters-1) else len(items_id)
            slice_products = [str(item) for item in items_id[begin:end] ]
            ids_list.append(','.join(slice_products))

        return ids_list

    def map_pool_get(self, paths:list, params=None, extra_headers=None):
        extra_headers = extra_headers if extra_headers else [extra_headers]*len(paths)
        params = params if params else [params]*len(paths)
        logging.info(f'Se estan realizando {len(paths)} peticiones.')
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = executor.map(self.get, paths, params, extra_headers)
        response = list()
        for result in results:
            response.append(result)
        return response

    def map_pool_put(self, paths, body=None, params=None, extra_headers=None):
        logging.info(f'Se estan realizando {len(paths)} peticiones.')
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = executor.map(self.put, paths,body, params, extra_headers)        
        response = list()
        for result in results:
            response.append(result)
        return response

    def search_items(self, ids_list, path, params=dict(), extra_headers=None):
        stack_ids = self.split_ids(ids_list)
        params_send = list()
        for ids in stack_ids:
            params['ids'] = ids
            params_send.append(params.copy())
        
        logging.info(f'Cargando {len(ids_list)} items.')
        items = self.map_pool_get(
            [path]*len(stack_ids),
            params_send,
            [extra_headers]*len(stack_ids),
        )
        return items

    def uptade_items(self, ids_list:list, bodys:list, extra_headers=None):
        path = '/items'
        paths = [f'{path}/{id}' for id in ids_list]
        params =  {'access_token': self.access_token}
        logging.info(f'Actualizando {len(ids_list)} items.')
        if not extra_headers:
            extra_headers = [extra_headers]*len(ids_list)

        self.map_pool_put(
            paths,
            bodys,
            [params]*len(ids_list),
            extra_headers,
        )