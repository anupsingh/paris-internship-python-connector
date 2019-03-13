import requests as rq
import pandas as pd
from base64 import b64encode
from urllib.parse import urlencode
import re
import json

from typing import Dict, List, Union

from .utils import get_cubes_from_discovery, parse_headers, detect_error, convert_store_to_dataframe
from .mdx import convert_mdx_to_dataframe
from .query import Query
from .authentication import AuthenticationBuilder
from .autotype import Types


JSON_Flat = Dict[str, Union[str, int, None]]


class Connector:
    # ==== Definition ====

    cubes = None

    def __init__(self, endpoint: str, authentication: AuthenticationBuilder):
        tools = authentication(endpoint.rstrip("/"))
        self.get = tools.get
        self.post = tools.post
        self.discover()

    # ==== Get data about every cubes ====

    def discover(self):
        """
        Get the infos of the cube, the number of axes, their labels, ...
        """
        response = self.get("pivot/rest/v4/cube/discovery")
        detect_error(response)

        self.cubes = get_cubes_from_discovery(response)

    def stores(self) -> Types:
        """
        Get the list of stores of a cube
        """
        response = self.get("pivot/rest/v4/datastore/discovery/storeNames")
        detect_error(response)
        return response["data"]

    def store_fields(self, store: str):
        """
        Get the list of available fields of a specific store with their respective types
        """
        response = self.get(f"pivot/rest/v4/datastore/data/stores/{store}")
        detect_error(response)
        return parse_headers(response["data"]["headers"])

    def store_references(self, store: str):
        """
        Get the references of the provided store
        """
        response = self.get(f"pivot/rest/v4/datastore/discovery/references/{store}")
        detect_error(response)
        return response["data"]

    def mdx_query(self, mdx_request: str, types: Types = {}) -> Query:
        """
        Execute a MDX query
        """

        def refresh():
            response = self.post("pivot/rest/v4/cube/query/mdx", body={"mdx": mdx_request})
            detect_error(response)

            return convert_mdx_to_dataframe(response, self.cubes)

        return Query(refresh, types)

    def store_query(
        self,
        store: str,
        fields: List[str],
        branch: str = "master",
        conditions: JSON_Flat = None,
        epoch: Union[str, None] = None,
        timeout: int = 30000,
        limit: int = 100,
        offset: int = 0,
        types: Types = {},
    ) -> Query:
        """
        Execute a query directly on the data store.
        Must specify the name of the data store and the fields that you want to retrieve.

        You can specify:
            - the conditions if you want to filter the data
            - the timeout in ms of the request (delay to wait at most for the query to complete in Pivot)
            - the epoch (optional category for the message)
            - the branch on which the request will be done
            - the limit and the offset for pagination
            - the returned types
        """
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

