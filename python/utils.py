import pandas as pd


def convert_dict_to_mdx(dictionary):
    nb_cols = len(dictionary.get("data").get("axes")[0].get("positions"))
    datastore = {}
    rows = [
        " | ".join(position[0].get("namePath")[1:])
        for position in dictionary.get("data").get("axes")[1].get("positions")
    ]
    nb_rows = len(rows)
    for row in rows:
        datastore[row] = [float('nan')] * nb_cols
    
    for cell in dictionary.get("data").get("cells"):
        datastoreId = rows[cell.get("ordinal") // nb_cols]
        col = cell.get("ordinal") % nb_cols
        datastore[datastoreId][col] = cell.get("value")

    return pd.DataFrame(data=datastore)

