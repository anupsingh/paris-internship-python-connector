import pandas as pd


def parse_key(key):
    if key == 0:
        return "Total"
    return key

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
                        "levels": list_to_dict(hierarchy["levels"])
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

def convert_mdx_to_dataframe(dictionary):
    cols = dictionary.get("data").get("axes")[0].get("positions")
    nb_cols = len(cols)

    datastore = {}

    rows = [
        " | ".join(position[0].get("namePath")[1:])
        for position in dictionary.get("data").get("axes")[1].get("positions")
    ]
    nb_rows = len(rows)

    for (index, col) in enumerate(cols):
        datastore[parse_key(index)] = { rows[index]:float('nan') for index in range(nb_rows) }
    
    for cell in dictionary.get("data").get("cells"):
        datastoreId = rows[cell.get("ordinal") // nb_cols]
        col = cell.get("ordinal") % nb_cols
        datastore[parse_key(col)][datastoreId] = cell.get("value")

    return pd.DataFrame(data=datastore)

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
# def convert_mdx_to_dataframe(dictionary):
#     nb_cols = len(dictionary.get("data").get("axes")[0].get("positions"))
#     datastore = {}
#     rows = [
#         " | ".join(position[0].get("namePath")[1:])
#         for position in dictionary.get("data").get("axes")[1].get("positions")
#     ]
#     nb_rows = len(rows)
#     for row in rows:
#         datastore[row] = [float('nan')] * nb_cols
    
#     for cell in dictionary.get("data").get("cells"):
#         datastoreId = rows[cell.get("ordinal") // nb_cols]
#         col = cell.get("ordinal") % nb_cols
#         datastore[datastoreId][col] = cell.get("value")

#     return pd.DataFrame(data=datastore)

