from configparser import SafeConfigParser
from .ssl_helper import SSLAdapter
from urllib.parse import urlencode
import json
import os
import re
import requests
import ssl
from meli_sdk.models import Token
from datetime import datetime, timedelta


class Meli(object):
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.refresh_token = None
        self.expiration = None


        parser = SafeConfigParser()
        parser.read(os.path.dirname(os.path.abspath(__file__))+'/config.ini')

        self._requests = requests.Session()
        try:
            self.SSL_VERSION = parser.get('config', 'ssl_version')
            self._requests.mount('https://', SSLAdapter(ssl_version=getattr(ssl, self.SSL_VERSION)))
        except:
            self._requests = requests

        self.API_ROOT_URL = parser.get('config', 'api_root_url')
        self.SDK_VERSION = parser.get('config', 'sdk_version')
        self.AUTH_URL = parser.get('config', 'auth_url')
        self.OAUTH_URL = parser.get('config', 'oauth_url')

    #AUTH METHODS
    def auth_url(self,redirect_URI=None):
        params = {'client_id':self.client_id,'response_type':'code'}
        if redirect_URI:
            params['redirect_uri'] = redirect_URI
        url = self.AUTH_URL  + '/authorization' + '?' + urlencode(params)
        return url

    def authorize(self, code, redirect_URI):
        params = { 'grant_type' : 'authorization_code', 'client_id' : self.client_id, 'client_secret' : self.client_secret, 'code' : code, 'redirect_uri' : redirect_URI}
        headers = {'Accept': 'application/json', 'User-Agent':self.SDK_VERSION, 'Content-type':'application/json'}
        uri = self.make_path(self.OAUTH_URL)

        response = self._requests.post(uri, params=urlencode(params), headers=headers)

        if response.ok:
            response_info = response.json()
            self.access_token = response_info['access_token']
            if 'refresh_token' in response_info:
                self.refresh_token = response_info['refresh_token']
            else:
                self.refresh_token = '' # offline_access not set up
            
            seg = response_info['expires_in']
            self.expiration = datetime.now() + timedelta(seg)
            token = Token(
                access_token = self.access_token,
                refresh_token = self.refresh_token,
                expiration = datetime.now() + timedelta(seg)
            )
            token.save()
            return self.access_token
        else:
            # response code isn't a 200; raise an exception
            response.raise_for_status()

    def get_refresh_token(self):
        if self.refresh_token:
            params = {'grant_type' : 'refresh_token', 'client_id' : self.client_id, 'client_secret' : self.client_secret, 'refresh_token' : self.refresh_token}
            headers = {'Accept': 'application/json', 'User-Agent':self.SDK_VERSION, 'Content-type':'application/json'}
            uri = self.make_path(self.OAUTH_URL)

            response = self._requests.post(uri, params=urlencode(params), headers=headers, data=params)

            if response.ok:
                response_info = response.json()
                self.access_token = response_info['access_token']
                self.refresh_token = response_info['refresh_token']
                self.expiration = response_info['expires_in']
                token = Token(
                    access_token = self.access_token,
                    refresh_token = self.refresh_token,
                    expiration = datetime.now() + timedelta(seg)
                )
                token.save()

            else:
                # response code isn't a 200; raise an exception
                response.raise_for_status()
        else:
            raise Exception("Offline-Access is not allowed.")

    # REQUEST METHODS
    def get(self, path, params=None, extra_headers=None):
        params = params or {}
        headers = {'Accept': 'application/json', 'User-Agent':self.SDK_VERSION, 'Content-type':'application/json'}
        if extra_headers:
            headers.update(extra_headers)
        uri = self.make_path(path)
        response = self._requests.get(uri, params=urlencode(params), headers=headers)
        if response.status_code == 200:
            data = res.json()
            return data
        elif response.status_code == 401:
            self.refresh_token()
            return self.get(path,params, extra_headers)
        else:
            raise Exception('Error en peticion personalizar mensaje')

    def post(self, path, body=None, params=None, extra_headers=None):
        params = params or {}
        headers = {'Accept': 'application/json', 'User-Agent':self.SDK_VERSION, 'Content-type':'application/json'}
        if extra_headers:
            headers.update(extra_headers)
        uri = self.make_path(path)
        if body:
            body = json.dumps(body)

        response = self._requests.post(uri, data=body, params=urlencode(params), headers=headers)
        return response

    def put(self, path, body=None, params=None, extra_headers=None):
        params = params or {}
        headers = {'Accept': 'application/json', 'User-Agent':self.SDK_VERSION, 'Content-type':'application/json'}
        if extra_headers:
            headers.update(extra_headers)
        uri = self.make_path(path)
        if body:
            body = json.dumps(body)

        response = self._requests.put(uri, data=body, params=urlencode(params), headers=headers)
        return response

    def delete(self, path, params=None, extra_headers=None):
        params = params or {}
        headers = {'Accept': 'application/json', 'User-Agent':self.SDK_VERSION, 'Content-type':'application/json'}
        if extra_headers:
            headers.update(extra_headers)
        uri = self.make_path(path)
        response = self._requests.delete(uri, params=params, headers=headers)
        return response

    def options(self, path, params=None, extra_headers=None):
        params = params or {}
        headers = {'Accept': 'application/json', 'User-Agent':self.SDK_VERSION, 'Content-type':'application/json'}
        if extra_headers:
            headers.update(extra_headers)
        uri = self.make_path(path)
        response = self._requests.options(uri, params=urlencode(params), headers=headers)
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
        if self.access_token:
            if self.expiration < (datetime.now()+timedelta(seconds=10)):
                self.get_refresh_token()
            return self.access_token
        else:
            raise Exception('Debe Autentificarse manualmente en el portal')