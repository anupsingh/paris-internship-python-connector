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
                formatted_dimension = { "name": dimension["caption"] }
                
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
    return -1

def get_prefilled_labels_from_headers(headers, cube):
    labels = []
    aggregation_field = "All"
    for position in headers["positions"]:
        label_element = {}
        for (label, hierarchy) in zip(position, headers["hierarchies"]):
            if hierarchy["hierarchy"] != "Measures":
                if len(label["namePath"]) == 1:
                    label_element[hierarchy["hierarchy"]] = aggregation_field
                else:
                    levels = cube["dimensions"][hierarchy["dimension"]]["hierarchies"][hierarchy["hierarchy"]]["levels"]
                    for (index, level) in enumerate(label["namePath"][1:]):
                        # ToDo: parsing int, float, str
                        # ToDo: Save formating in "apply formater" of Query
                        label_element[levels[index + 1]] = level
        labels.append(label_element)
    return labels

def detect_measures_axe_id(dictionary):
    for (axe_index, axe) in enumerate(dictionary["data"]["axes"]):
        for (hierarchy_index, hierarchy) in enumerate(axe["hierarchies"]):
            if hierarchy["hierarchy"] == "Measures":
                return (axe_index, hierarchy_index)
    return (-1, -1)


def convert_mdx_to_dataframe(dictionary, cubes):
    #  ToDo: Support more than 2 axes
    cube = cubes[dictionary["data"]["cube"]]

    nb_rows = len(dictionary["data"]["axes"][1]["positions"])
    nb_cols = len(dictionary["data"]["axes"][0]["positions"])

    cells = [[ float('nan') for i in range(nb_cols)] for j in range(nb_rows)]

    headers = dictionary["data"]["axes"][0]
    positions = headers["positions"]
    number_of_useful_headers = find_length_positions(positions)
    # headers["positions"] = positions[::number_of_useful_headers]

    rows_from_headers = get_prefilled_labels_from_headers(headers, cube)
    cols = get_prefilled_labels_from_headers(dictionary["data"]["axes"][1], cube)
    
    for cell in dictionary["data"]["cells"]:
        row = cell["ordinal"] // nb_cols
        col = cell["ordinal"] % nb_cols
        cells[row][col] = cell["value"]

    rows = []

    measures_axe_id, measures_hierarchy_id = detect_measures_axe_id(dictionary)

    if measures_axe_id == -1:
        # ToDo: Compute later
        return
    
    print(measures_axe_id)
    cardinals_axe_with_measures = [set() for _ in dictionary["data"]["axes"][measures_axe_id]["hierarchies"]]
    for position in dictionary["data"]["axes"][measures_axe_id]["positions"]:
        for (i, p) in enumerate(position):
            cardinals_axe_with_measures[i].add(p["namePath"][-1])
    
    cardinals_axe_with_measures = [len(cardinal) for cardinal in cardinals_axe_with_measures]
    print(cardinals_axe_with_measures, measures_hierarchy_id)

    nb_spikes = cardinals_axe_with_measures[measures_hierarchy_id]
    nb_groups = 1
    for i in range(0, measures_hierarchy_id):
        nb_groups *= cardinals_axe_with_measures[i]
    print(nb_groups)
    
    offset = 1
    for i in range(measures_hierarchy_id + 1, len(cardinals_axe_with_measures)):
        offset *= cardinals_axe_with_measures[i]
    print(offset)
    
    size_group = offset * nb_spikes

    for (row_index, row) in enumerate(cells):
        for index_group in range(nb_groups):
            for index_fork in range(offset):
                index_beginning_fork = index_group * size_group + index_fork
                # print(index_beginning_fork, len(rows_from_headers))
                res = { **rows_from_headers[index_beginning_fork], **cols[row_index] }
                for index_spike in range(nb_spikes):
                    i = index_beginning_fork + offset*index_spike
                    # print(i, len(row))
                    res[positions[i][-1]["namePath"][-1]] = row[i]
                rows.append(res)

    return pd.DataFrame(data=rows)

def convert_store_to_dataframe(headers, rows):
    datastore = [
        { header:element for (header, element) in zip(headers, row) }
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
    return { header["name"]: parse_type(header["type"]) for header in headers }


def list_to_dict(l):
    return { element["name"]:element["caption"] for element in l }


