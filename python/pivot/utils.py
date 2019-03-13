import pandas as pd
from math import isnan


def get_cubes_from_discovery(dictionary):
    cubes = {}
    for cube in dictionary["data"]["catalogs"][0]["cubes"]:
        raw_name = cube["name"]
        display_name = cube["caption"]
        measures = list_to_dict(cube["measures"])
        dimensions = {}
        for dimension in cube["dimensions"]:
            formatted_dimension = {"name": dimension["caption"]}

            hierarchies = {}
            for hierarchy in dimension["hierarchies"]:
                formatted_hierarchy = {
                    "name": hierarchy["caption"],
                    "levels": [level["name"] for level in hierarchy["levels"]],
                }
                hierarchies[hierarchy["name"]] = formatted_hierarchy
            formatted_dimension["hierarchies"] = hierarchies
            formatted_dimension["default_hierarchy"] = formatted_dimension["hierarchies"][
                dimension["defaultHierarchy"]
            ]

            dimensions[dimension["name"]] = formatted_dimension
        cubes[raw_name] = {"name": display_name, "measures": measures, "dimensions": dimensions}
    return cubes


def find_length_positions(positions):
    initial_position = positions[0]
    for (index, position) in enumerate(positions[1:]):
        if position[-1] == initial_position[-1]:
            return index + 1


def detect_measures_axe_id(dictionary):
    for (axe_index, axe) in enumerate(dictionary["data"]["axes"]):
        for (hierarchy_index, hierarchy) in enumerate(axe["hierarchies"]):
            if hierarchy["hierarchy"] == "Measures":
                return (axe_index, hierarchy_index)
    return (-1, -1)


def convert_store_to_dataframe(headers, rows):
    datastore = [{header: element for (header, element) in zip(headers, row)} for row in rows]
    return pd.DataFrame(data=datastore)


def detect_error(response):
    if response["status"] == "error":
        error = ""
        for err in response["error"]["errorChain"]:
            error += err["message"] + "\n"
        raise Exception(error)


def parse_type(element):
    if element == "int":
        return int
    if element == "String":
        return str


def parse_headers(headers):
    return {header["name"]: parse_type(header["type"]) for header in headers}


def list_to_dict(l):
    return {element["name"]: element["caption"] for element in l}
