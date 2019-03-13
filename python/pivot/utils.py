import pandas as pd
from math import isnan

from .mdx import MEASURE_FIELD, DIMENSION_FIELD


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


def cubes_leaves(cubes):
    leaves = {}
    for cube_name in cubes:
        cube = cubes[cube_name]
        duplicates = set()
        cube_leaves = {}
        for dimension_name in cube["dimensions"]:
            dimension = cube["dimensions"][dimension_name]
            for hierarchy_name in dimension["hierarchies"]:
                hierarchy = dimension["hierarchies"][hierarchy_name]
                for index_level, level in enumerate(hierarchy["levels"]):
                    if level in duplicates:
                        continue
                    if level in cube_leaves:
                        del cube_leaves[level]
                        duplicates.add(level)
                        continue
                    cube_leaves[level] = [
                        DIMENSION_FIELD,
                        dimension_name,
                        hierarchy_name,
                        hierarchy["levels"][: index_level + 1],
                    ]
        for measure in cube["measures"]:
            if measure in cube_leaves:
                continue
            cube_leaves[measure] = [MEASURE_FIELD, measure]
        leaves[cube_name] = cube_leaves
    return leaves


def find_length_positions(positions):
    initial_position = positions[0]
    for (index, position) in enumerate(positions[1:]):
        if position[-1] == initial_position[-1]:
            return index + 1


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
