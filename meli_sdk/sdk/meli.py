from django.utils import timezone

from configparser import SafeConfigParser
# from .ssl_helper import SSLAdapter
from urllib.parse import urlencode

import json
import os
import re
import ssl
from meli_sdk.models import Token
from datetime import timedelta
import logging
from decouple import config
import asyncio
from utils.views import WebClient, chunk_list_every, get_with_semaphore


class Meli(object):
    def __init__(self, seller_id=None):
        self.client_secret = config('MELI_SECRET_KEY')
        self.client_id = config('MELI_APP_ID')
        self.limit_ids_per_request = 20
        # self.max_workers = 5
        self.max_concurrent = 100
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
        self.lock = asyncio.Lock()
        # try:
        #     self.SSL_VERSION = parser.get('config', 'ssl_version')
        #     self._requests.mount('https://', SSLAdapter(ssl_version=getattr(ssl, self.SSL_VERSION)))
        # except:
        #     self._requests = requests


    #AUTH METHODS
    def auth_url(self,redirect_URI=None):
        params = {'client_id':self.client_id,'response_type':'code'}
        if redirect_URI:
            params['redirect_uri'] = redirect_URI
        url = self.AUTH_URL  + '/authorization' + '?' + urlencode(params)
        return url

    async def authorize(self, code, redirect_URI):
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

        response = self.request(
            request_type='post',
            path=self.OAUTH_URL,
            params=params)

        if response:
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
            raise Exception("Offline-Access is not allowed.")

    async def update_token(self):
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

            response = await self.request(
                request_type='post'
                path=self.OAUTH_URL,
                params=params,
                body=params
            )

            if response:
                response_info = response.json()
                seg = response_info['expires_in']
                expiration = timezone.localtime() + timedelta(seconds=seg)
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
    async def request(
        self,
        request_type="get",
        path="",
        params={},
        body={},
        return_data="json",
        extra_headers={},
        auth=False,
        **kwargs,
    ):
        if body:
            body = json.dumps(body)

        auth= True if request_type in ('put','delete') else auth
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
        max_reintents = 30
        i = 0
        while i < max_reintents:  # max_reintents por si no recibe un Json
            i += 1
            async with (await WebClient().get_session()).__getattribute__(request_type)(
                uri, data=body, params=params, headers=headers, verify_ssl=False
            ) as resp:
                if not resp:
                    logging.error(
                        f"NOT RESP: {request_type} {uri} {body} {params}"
                    )
                    return
                try:
                    res_json = {}
                    if return_data == "json":
                        if resp.content_type == "text/html":
                            logging.error(
                                f"{request_type} {resp.status} {uri}.\n ERROR JSON RESPONSE: {await resp.text()} "
                            )
                            return

                        res_json = await resp.json()
                        if isinstance(res_json, (list, dict)):
                            final_res = res_json
                    elif return_data == "text":
                        res_text = await resp.text()
                        if res_text:
                            final_res = res_text
                    elif return_data is None:
                        final_res = None

                    if resp.status in (200, 201, 206):
                        if isinstance(final_res, list) and any(
                            1 for i in final_res if i.get("code") == 500
                        ):
                            logging.warn(
                                f"{request_type}, {resp.status}, {resp.url}, some one with code:500"
                            )
                            continue
                        return final_res
                    elif resp.status in (403,):  # 403 = Forbidden (meli day limit)
                        return final_res
                    elif resp.status in (
                        429,
                        500,
                        501,
                        502,
                        409,
                        504,
                    ):  # 504=not found(temporaly), 409 =optimistic locking, 429 = toomany request
                        if 0 < i < 5:
                            logging.debug(
                                f"{request_type} {resp.status} retrying No-{i} , too quikly? {0.2 * i}"
                            )
                        elif 5 < i:
                            logging.info(
                                f"{request_type} {resp.status} retrying No-{i} , too quikly? {0.2 * i}"
                            )
                        await asyncio.sleep(0.2 * i)
                        continue
                    elif resp.status == 401:  # expired_token
                        with await self.lock:
                            token = Token.objects.get(seller_id=self.seller_id)
                            if token.expiration > self.token.expiration:
                                self.token = token
                            else:
                                await self.update_token()
                                params['access_token']=self.access_token
                            max_reintents /= 3
                        continue
                    elif resp.status in (404, 400) and isinstance(res_json, dict):
                        logging.info(
                            f"{request_type}, {resp.status}, {resp.url}, {res_json.get('message')}, {res_json.get('cause')}"
                        )
                        return res_json
                    else:
                        if res_json:
                            logging.warn(
                                f"{request_type}, {resp.status}, {resp.url}, -{await resp.text()}-"
                            )
                        return
                except Exception as e:
                    logging.error(
                        f"Error on {request_type} return_data:{return_data} {uri}, {e}"
                    )
                    logging.debug('ERROR, sleeping 0.5 seg')
                    await asyncio.sleep(0.5)
                    continue

    async def pool_requests(self, coros:list, name:str):
        return await get_with_semaphore(coros, self.max_concurrent, name, 20)

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
        items_id = (str(item) for item un items_id)

        ids_list = list()
        for chunk_items in chunk_list_every(items_id, self.limit_ids_per_request):
            ids_list.append(','.join(chunk_items))

        return ids_list

    async def search_items(self, ids_list, path, params=dict()):
        stack_ids = self.split_ids(ids_list)
        params_send = list()
        for ids in stack_ids:
            params['ids'] = ids
            params_send.append(params.copy())

        logging.info(f'Cargando {len(ids_list)} items.')
        coros = [
            self.request(
                request_type='get',path=path,params=_params
            ) for _params in params_send]
        return await self.pool_requests(coros,'search_items')

    async def update_items(self, ids_list:list, bodys:list):
        path = '/items'
        assert len(ids_list) == len(bodys)
        logging.info(f'Actualizando {len(ids_list)} items.')
        coros = [
            self.request(
                request_type='put',
                path=f'{path}/{id}',
                auth=True,
                body=body
            )for id, body in zip(ids_list,bodys)]
        return await self.pool_requests(coros, 'update_items')