import requests as rq
from base64 import b64encode
from urllib.parse import urlencode
import re
import json
from .utils import (
    get_cubes_from_discovery,
    convert_mdx_to_dataframe,
    parse_headers,
    detect_error,
    convert_store_to_dataframe,
    list_to_dict,
    AGGREGATION_FIELD,
)
from .autotype import auto_type_list


class Connector:
    # ==== Definition ====

    cubes = None

    def __init__(self, endpoint, authentication):
        tools = authentication(endpoint.rstrip("/"))
        self.get = tools.get
        self.post = tools.post
        self.discover()

    # ==== Get data about every cubes ====

    def discover(self):
        response = self.get("pivot/rest/v4/cube/discovery")
        detect_error(response)

        self.cubes = get_cubes_from_discovery(response)
        # print(self.cubes)

    def mdx_query(self, mdx_request, types={}):
        def refresh():
            response = self.post("pivot/rest/v4/cube/query/mdx", body={"mdx": mdx_request})
            detect_error(response)

            return convert_mdx_to_dataframe(response, self.cubes)

        return Query(refresh, types)

    def store_fields(self, store):
        response = self.get(f"pivot/rest/v4/datastore/data/stores/{store}")
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
        response = self.get("pivot/rest/v4/datastore/discovery/storeNames")
        detect_error(response)
        return response["data"]

    def store_references(self, store):
        response = self.get(f"pivot/rest/v4/datastore/discovery/references/{store}")
        detect_error(response)
        return response["data"]

    def store_query(
        self,
        store,
        fields,
        branch="master",
        conditions=None,
        epoch=None,
        timeout=30000,
        limit=100,
        offset=0,
        types={},
    ):
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
            body = {"fields": fields, "branch": branch, "timeout": timeout}
            if epoch != None:
                body["epoch"] = epoch
            if cond:
                if type(cond) == str:
                    cond = json.loads(cond)
                body["conditions"] = cond

            response = self.post(
                f"{base}/data/stores/{store}?query=&page={page_offset}&pageSize={page_size}",
                body=body,
            )
            detect_error(response)
            headers = parse_headers(response["data"]["headers"])
            rows = response["data"]["rows"]
            page_index = 1
            while page_index < nb_pages and response["data"]["pagination"].get("nextPageUrl"):
                page_index += 1
                response = self.post(
                    f'{base}{response["data"]["pagination"]["nextPageUrl"]}&query=', body=body
                )
                detect_error(response)
                rows.extend(response["data"]["rows"])
            real_end_extras = max(len(rows) - offset - limit, 0)
            # Trimming
            rows = rows[start_extras : (len(rows) - real_end_extras)]
            return convert_store_to_dataframe(headers, rows)

        return Query(refresh, types)


class Query:
    __method = None
    dataframe = None
    types = {}

    def __init__(self, method, types={}):
        self.__method = method
        self.types = types
        self.refresh()
        self.detect_type()
        self.apply_types()

    def refresh(self):
        self.dataframe = self.__method()
        self.apply_types()

    def detect_type(self):
        def detect_type(values):
            type = auto_type_list(values)
            name = values.name
            if type is not None and name not in self.types:
                self.types[name] = type

        self.dataframe.apply(detect_type)

    def apply_types(self):
        if self.dataframe is None:
            return

        def format_dataframe(values):
            type = self.types.get(values.name)
            if type is None:
                type = lambda x: x
            return [
                type(value) if value != AGGREGATION_FIELD else AGGREGATION_FIELD for value in values
            ]

        self.dataframe.update(self.dataframe.apply(format_dataframe))


def refreshed(query):
    return Query(query.method, query.types)
