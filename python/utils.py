import pandas as pd
from math import isnan


AGGREGATION_FIELD = "All"


def autoparse(value, type=None):
    try:
        if type is not None:
            return type(value)
    except:
        return value
    try:
        return int(value)
    except:
        try:
            return float(value)
        except:
            return value


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
                    "levels": [level["name"] for level in hierarchy["levels"]]
                }
                hierarchies[hierarchy["name"]] = formatted_hierarchy
            formatted_dimension["hierarchies"] = hierarchies
            formatted_dimension["default_hierarchy"] = formatted_dimension["hierarchies"][dimension["defaultHierarchy"]]

            dimensions[dimension["name"]] = formatted_dimension
        cubes[raw_name] = {
            "name": display_name,
            "measures": measures,
            "dimensions": dimensions
        }
    return cubes


def find_length_positions(positions):
    initial_position = positions[0]
    for (index, position) in enumerate(positions[1:]):
        if position[-1] == initial_position[-1]:
            return index + 1

def get_prefilled_label_from_headers(position, hierarchies, cube):
    global AGGREGATION_FIELD
    label_element = {}
    for (label, hierarchy) in zip(position, hierarchies):
        if hierarchy["hierarchy"] != "Measures":
            if len(label["namePath"]) == 1:
                label_element[hierarchy["hierarchy"]] = AGGREGATION_FIELD
            else:
                levels = cube["dimensions"][hierarchy["dimension"]
                                            ]["hierarchies"][hierarchy["hierarchy"]]["levels"]
                for (index, level) in enumerate(levels[1:]):
                    # ToDo: parsing int, float, str
                    # ToDo: Save formating in "apply formater" of Query
                    value = label["namePath"][index + 1] if len(label["namePath"]) > index + 1 else AGGREGATION_FIELD
                    label_element[level] = value
    return label_element

def get_prefilled_labels_from_headers(headers, cube):
    labels = []
    hierarchies = headers["hierarchies"]
    for position in headers["positions"]:
        labels.append(get_prefilled_label_from_headers(position, hierarchies, cube))
    return labels

def detect_measures_axe_id(dictionary):
    for (axe_index, axe) in enumerate(dictionary["data"]["axes"]):
        for (hierarchy_index, hierarchy) in enumerate(axe["hierarchies"]):
            if hierarchy["hierarchy"] == "Measures":
                return (axe_index, hierarchy_index)
    return (-1, -1)


def convert_mdx_to_dataframe(dictionary, cubes):
    global AGGREGATION_FIELD
    cube = cubes[dictionary["data"]["cube"]]

    nb_rows = len(dictionary["data"]["axes"][1]["positions"])
    nb_cols = len(dictionary["data"]["axes"][0]["positions"])

    cells = [[float('nan') for i in range(nb_cols)] for j in range(nb_rows)]

    for cell in dictionary["data"]["cells"]:
        row = cell["ordinal"] // nb_cols
        col = cell["ordinal"] % nb_cols
        cells[row][col] = cell["value"]

    measures_axe_index, measures_hierarchy_index = detect_measures_axe_id(
        dictionary)

    hashes_rows = {}

    for row_index in range(nb_rows):
        for col_index in range(nb_cols):
            measure = cells[row_index][col_index]
            measure_name = dictionary["data"]["axes"][measures_axe_index][
                "positions"][col_index][measures_hierarchy_index]["namePath"][-1]

            if isnan(measure):
                continue

            this_axes = [col_index, row_index]
            # print(measure_name, measure)
            raw_row = [
                [
                    [
                        hierarchy["namePath"]
                        for (hierarchy_index, hierarchy) in enumerate(position)
                        if axe_index != measures_axe_index or hierarchy_index != measures_hierarchy_index
                    ]
                    for (position_index, position) in enumerate(axe["positions"])
                    if position_index == this_axes[axe_index]
                ]
                for (axe_index, axe) in enumerate(dictionary["data"]["axes"])
            ]
            # hash_row = "____".join([
            hash_row = "___".join([
                # "___".join([
                    "__".join([
                        "_".join(hierarchy)
                        # for hierarchy in position
                        for hierarchy in axe[0]
                    ])
                    # for position in axe
                # ])
                for axe in raw_row
            ])
            # print(hash_row, raw_row)
            if hash_row not in hashes_rows:
                row = {}
                hashes_rows[hash_row] = row
                for (axe_index, axe) in enumerate(raw_row):
                    # print("axe", axe)
                    this_position_index = this_axes[axe_index]
                    for _ in axe[0]:
                        headers = get_prefilled_label_from_headers(dictionary["data"]["axes"][axe_index]["positions"][this_position_index], dictionary["data"]["axes"][axe_index]["hierarchies"], cube)
                        row.update(headers)

            hashes_rows[hash_row][measure_name] = measure

    # print(hashes_rows)
    data = [hashes_rows[hash] for hash in hashes_rows]
    return pd.DataFrame(data=data)


def convert_store_to_dataframe(headers, rows):
    datastore = [
        {header: element for (header, element) in zip(headers, row)}
        for row in rows
    ]
    return pd.DataFrame(data=datastore)


def detect_error(response):
    if response['status'] == 'error':
        error = ''
        for err in response['error']['errorChain']:
            error += err['message'] + '\n'
        raise Exception(error)


def parse_type(element):
    if element == 'int':
        return int
    if element == 'String':
        return str


def parse_headers(headers):
    return {header["name"]: parse_type(header["type"]) for header in headers}


def list_to_dict(l):
    return {element["name"]: element["caption"] for element in l}
