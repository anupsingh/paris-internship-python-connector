import requests as rq
from urllib.parse import urlencode
from base64 import b64encode
import json

from typing import Dict, Callable, NamedTuple


def _get(url: str, params: Dict[str, str] = {}) -> str:
    pass


def _post(url: str, params: Dict[str, str] = {}, body: Dict[str, str] = {}) -> str:
    pass


class Auth(NamedTuple):
    get: _get
    post: _post


def build_url(endpoint: str, pathname: str, params: Dict[str, str] = {})->str:
    """
    Format an url string:

    Example:
        > url('http://google.com/','/search', { "query":"my query" })
        'http://google.com//search?query=my+query'
    """
    uri = f'{endpoint}/{pathname.lstrip("/")}'
    if len(params) >= 1:
        uri = f'{uri}?{urlencode(params)}'
    return uri


def simple_auth(username: str, password: str) -> Callable[[str], Auth]:
    """
    Create a wrapper around a simple auth API
    """
    def call(endpoint: str) -> Auth:
        token = f'{username}:{password}'
        authorization = b64encode(token.encode('utf-8')).decode('utf-8')

        def is_connected():
            if endpoint == None:
                raise Exception(
                    'You must specify the URL of the ActivePivot instance')
            if username == None or password == None:
                raise Exception('You must be connected')

        def get(url: str, params: Dict[str, str] = {}):
            is_connected()
            built_endpoint = build_url(endpoint, url, params)
            return json.loads(rq.get(built_endpoint, headers={
                "Authorization": f'Basic {authorization}',
            }).text)

        def post(url: str, params: Dict[str, str] = {}, body: Dict[str, str] = {}):
            is_connected()
            built_endpoint = build_url(endpoint, url, params)
            body = json.dumps(body).encode('utf-8')
            return json.loads(rq.post(built_endpoint, headers={
                "Authorization": f'Basic {authorization}',
                "Content-Type": "application/json"
            }, data=body).text)

        return Auth(get, post)
    return call
