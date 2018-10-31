import requests as rq
from base64 import b64encode
from urllib.parse import urlencode
import re
import json
from utils import convert_mdx_to_dataframe

class Connector:
    endpoint = None
    username = None
    password = None

    @property
    def authorization(self):
        token = f'{self.username}:{self.password}'
        return b64encode(token.encode('utf-8')).decode('utf-8')

    def url(self, pathname, options={}):
        uri = f'{self.endpoint}/{pathname.lstrip("/")}'
        if len(options) >= 1:
            uri = f'{uri}?{urlencode(options)}'
        return uri

    def __init__(self, endpoint=None, username=None, password=None):
        self.open(endpoint)
        self.connect(username, password)
    
    def open(self, endpoint):
        self.endpoint = endpoint.rstrip('/')

    def connect(self, username, password):
        self.username = username
        self.password = password

    def check_if_connected(self):
        if self.endpoint == None:
            raise Exception('You must specify the URL of the ActivePivot instance')
        if self.username == None or self.password == None:
            raise Exception('You must be connected')

    def request(self, url, body):
        self.check_if_connected()
        endpoint = self.url(url)
        body = json.dumps(body).encode('utf-8')
        return json.loads(rq.post(endpoint, headers={
            "Authorization": f'Basic {self.authorization}',
            "Content-Type": "application/json"
        }, data=body).text)

    def mdx(self, mdx_request):
        def refresh():
            response = self.request('pivot/rest/v4/cube/query/mdx', {
                "mdx": mdx_request
            })
            if response.get('status') == 'error':
                error = ''
                for err in response.get('error').get('errorChain'):
                    error += err.get('message') + '\n'
                raise Exception(error)
            
            return convert_mdx_to_dataframe(response)
        return Query(refresh)
        

class Query:
    method = None
    dataframe = None

    def __init__(self, method):
        self.method = method
        self.refresh()

    def refresh(self):
        self.dataframe = self.method()
    
    
def refreshed(query):
    return Query(query.method)
    
