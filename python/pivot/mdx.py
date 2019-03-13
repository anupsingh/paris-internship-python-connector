import pandas as pd
from math import isnan

from .utils import detect_measures_axe_id

AGGREGATION_FIELD = "All"


def get_prefilled_label_from_headers(position, hierarchies, cube):
    global AGGREGATION_FIELD
    label_element = {}
    for (label, hierarchy) in zip(position, hierarchies):
        if hierarchy["hierarchy"] != "Measures":
            if len(label["namePath"]) == 1:
                label_element[hierarchy["hierarchy"]] = AGGREGATION_FIELD
            else:
                levels = cube["dimensions"][hierarchy["dimension"]]["hierarchies"][
                    hierarchy["hierarchy"]
                ]["levels"]
                for (index, level) in enumerate(levels[1:]):
                    value = (
                        label["namePath"][index + 1]
                        if len(label["namePath"]) > index + 1
                        else AGGREGATION_FIELD
                    )
                    label_element[level] = value
    return label_element


def get_prefilled_labels_from_headers(headers, cube):
    labels = []
    hierarchies = headers["hierarchies"]
    for position in headers["positions"]:
        labels.append(get_prefilled_label_from_headers(position, hierarchies, cube))
    return labels


def convert_mdx_to_dataframe(dictionary, cubes):
    global AGGREGATION_FIELD
    cube = cubes[dictionary["data"]["cube"]]

    if len(dictionary["data"]["axes"]) != 2:
        raise Exception("Can only process 2 axes")

    nb_rows = len(dictionary["data"]["axes"][1]["positions"])
    nb_cols = len(dictionary["data"]["axes"][0]["positions"])

    cells = [[float("nan") for i in range(nb_cols)] for j in range(nb_rows)]

    for cell in dictionary["data"]["cells"]:
        row = cell["ordinal"] // nb_cols
        col = cell["ordinal"] % nb_cols
        cells[row][col] = cell["value"]

    measures_axe_index, measures_hierarchy_index = detect_measures_axe_id(dictionary)

    hashes_rows = {}

    for row_index in range(nb_rows):
        for col_index in range(nb_cols):
            measure = cells[row_index][col_index]
            measure_name = dictionary["data"]["axes"][measures_axe_index]["positions"][col_index][
                measures_hierarchy_index
            ]["namePath"][-1]

            if isnan(measure):
                continue

            this_axes = [col_index, row_index]
            # print(measure_name, measure)
            raw_row = [
                [
                    [
                        hierarchy["namePath"]
                        for (hierarchy_index, hierarchy) in enumerate(position)
                        if axe_index != measures_axe_index
                        or hierarchy_index != measures_hierarchy_index
                    ]
                    for (position_index, position) in enumerate(axe["positions"])
                    if position_index == this_axes[axe_index]
                ]
                for (axe_index, axe) in enumerate(dictionary["data"]["axes"])
            ]
            hash_row = "___".join(
                ["__".join(["_".join(hierarchy) for hierarchy in axe[0]]) for axe in raw_row]
            )

            if hash_row not in hashes_rows:
                row = {}
                hashes_rows[hash_row] = row
                for (axe_index, axe) in enumerate(raw_row):
                    this_position_index = this_axes[axe_index]
                    for _ in axe[0]:
                        headers = get_prefilled_label_from_headers(
                            dictionary["data"]["axes"][axe_index]["positions"][this_position_index],
                            dictionary["data"]["axes"][axe_index]["hierarchies"],
                            cube,
                        )
                        row.update(headers)

            hashes_rows[hash_row][measure_name] = measure

    data = [hashes_rows[hash] for hash in hashes_rows]
    return pd.DataFrame(data=data)
