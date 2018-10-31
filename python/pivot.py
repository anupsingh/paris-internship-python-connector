import requests as rq
from base64 import b64encode
from urllib.parse import urlencode
import re
import json
from utils import convert_dict_to_mdx

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
        response = Query("post", endpoint, headers={
            "Authorization": f'Basic {self.authorization}',
            "Content-Type": "application/json"
        }, body=body)
        return response

    def mdx(self, mdx_request):
        return self.request('pivot/rest/v4/cube/query/mdx', {
            "mdx": mdx_request
        })
        

class Query:
    method = None
    endpoint = None
    body = None
    headers = None
    response = None
    response_json = None
    dataframe = None

    def __init__(self, method, endpoint, body=None, headers=None):
        self.method = method
        self.endpoint = endpoint
        self.body = body
        self.headers = headers
        self.refresh()

    def refresh(self):
        if self.method.lower() == 'post':
            self.post()
    
    def post(self):
        self.response = rq.post(self.endpoint, headers=self.headers, data=self.body)
        self.response_json = json.loads(self.response.text)

    def to_data_frame(self, compute=False):
        if self.response_json == None:
            raise Exception("Must perform request first")

        if self.dataframe != None and not(compute):
            return self.dataframe
        
        # Error handling
        if self.response_json.get('status') == 'error':
            error = ''
            for err in self.response_json.get('error').get('errorChain'):
                error += err.get('message') + '\n'
            raise Exception(error)
        
        self.dataframe = convert_dict_to_mdx(self.response_json)
        return self.dataframe

    
def refreshed(query):
    return Query(query.method, query.endpoint, body=query.body, headers=query.headers)
    
