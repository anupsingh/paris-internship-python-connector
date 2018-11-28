import pandas as pd


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

def header_to_empty_dict(headers, cube):
    res = []
    aggregation_field = "All"
    for position in headers["positions"]:
        res_element = {}
        for index, hierarchy in enumerate(headers["hierarchies"][:-1]):
            if len(position[index]["namePath"]) == 1:
                res_element[hierarchy["hierarchy"]] = aggregation_field
            else:
                res_element[hierarchy["hierarchy"]] = position[index]["namePath"][1]
        res.append(res_element)
    print(res)
    return res

def convert_mdx_to_dataframe(dictionary, cubes):
    cube = cubes[dictionary["data"]["cube"]]

    nb_rows = len(dictionary["data"]["axes"][0]["positions"])
    nb_cols = len(dictionary["data"]["axes"][1]["positions"])

    cells = [[ float('nan') for i in range(nb_cols)] for j in range(nb_rows)]

    headers = dictionary["data"]["axes"][0]
    positions = headers["positions"]
    number_of_useful_headers = find_length_positions(positions)
    headers["positions"] = positions[::number_of_useful_headers]

    rows_from_headers = header_to_empty_dict(headers, cube)

    for cell in dictionary["data"]["cells"]:
        row = cell["ordinal"] // nb_cols
        col = cell["ordinal"] % nb_cols
        cells[row][col] = cell["value"]

    return pd.DataFrame(data=cells)

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


