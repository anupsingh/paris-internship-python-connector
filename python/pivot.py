import requests as rq
from base64 import b64encode
from urllib.parse import urlencode
import re
import json
from utils import get_cubes_from_discovery, convert_mdx_to_dataframe, parse_headers, detect_error, convert_store_to_dataframe, list_to_dict, AGGREGATION_FIELD

class Connector:
    # ==== Definition ====

    endpoint = None
    username = None
    password = None
    cubes = None

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
        self.discover()

    # ==== Methods to make API calls ====


    def check_if_connected(self):
        if self.endpoint == None:
            raise Exception('You must specify the URL of the ActivePivot instance')
        if self.username == None or self.password == None:
            raise Exception('You must be connected')

    def get(self, url):
        self.check_if_connected()
        endpoint = self.url(url)
        return json.loads(rq.get(endpoint, headers={
            "Authorization": f'Basic {self.authorization}',
        }).text)

    def post(self, url, body):
        self.check_if_connected()
        endpoint = self.url(url)
        body = json.dumps(body).encode('utf-8')
        return json.loads(rq.post(endpoint, headers={
            "Authorization": f'Basic {self.authorization}',
            "Content-Type": "application/json"
        }, data=body).text)

    # ==== Get data about every cubes ====

    def discover(self):
        response = self.get("pivot/rest/v4/cube/discovery")
        detect_error(response)

        self.cubes = get_cubes_from_discovery(response)
        # print(self.cubes)

    def mdx_query(self, mdx_request):
        def refresh():
            response = self.post('pivot/rest/v4/cube/query/mdx', {
                "mdx": mdx_request
            })
            detect_error(response)

            return convert_mdx_to_dataframe(response, self.cubes)
        return Query(refresh)

    def store_fields(self, store):
        response = self.get(f'pivot/rest/v4/datastore/data/stores/{store}')
        detect_error(response)
        return parse_headers(response["data"]["headers"])
    # def store_fields(self, store):
    #     def refresh():
    #         response = self.get(f'pivot/rest/v4/datastore/data/stores/{store}')
    #         detect_error(response)
    #         headers = parse_headers(response["data"]["headers"])
    #         rows = response["data"]["rows"]
    #         return convert_store_to_dataframe(headers, rows)
    #     return Query(refresh)

    def stores(self):
        response = self.get('pivot/rest/v4/datastore/discovery/storeNames')
        detect_error(response)
        return response['data']

    def store_references(self, store):
        response = self.get(f'pivot/rest/v4/datastore/discovery/references/{store}')
        detect_error(response)
        return response['data']

    def store_query(self, store, fields, branch="master", conditions=None, epoch=None, timeout=30000, limit=100, offset=0):
        limit = int(limit)
        offset = int(offset)
        timeout = int(timeout)
        
        page_size = min(limit, 10)
        start_extras = offset % page_size
        end_extras = (offset + limit) % page_size
        nb_pages = (start_extras != 0) + limit // page_size + (end_extras != 0)
        page_offset = offset // page_size + 1
        
        def refresh():
            cond = conditions
            base = "pivot/rest/v4/datastore"
            body = {
                "fields": fields,
                "branch": branch,
                "timeout": timeout
            }
            if epoch != None: body['epoch'] = epoch
            if cond:
                if type(cond) == str:
                    cond = json.loads(cond)
                body["conditions"] = cond
            
            response = self.post(f'{base}/data/stores/{store}?query=&page={page_offset}&pageSize={page_size}', body)
            detect_error(response)
            headers = parse_headers(response["data"]["headers"])
            rows = response["data"]["rows"]
            page_index = 1
            while page_index < nb_pages and response["data"]["pagination"].get("nextPageUrl"):
                page_index += 1
                response = self.post(f'{base}{response["data"]["pagination"]["nextPageUrl"]}&query=', body)
                detect_error(response)
                rows.extend(response["data"]["rows"])
            real_end_extras = len(rows) - offset - limit
            # Trimming 
            rows = rows[start_extras:(len(rows)-real_end_extras)]
            return convert_store_to_dataframe(headers, rows)
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
    
