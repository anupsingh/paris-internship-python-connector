import pandas as pd


def parse_key(key):
    if key == 0:
        return "Total"
    return key

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

