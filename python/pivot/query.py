from pandas import DataFrame

from typing import Callable


from .autotype import auto_type_list, Types
from .mdx import AGGREGATION_FIELD


class Query:
    method: Callable[[], DataFrame] = None
    dataframe: DataFrame = None
    types: Types = {}

    def __init__(self, method, types={}):
        self.method = method
        self.types = types
        self.refresh()
        self.detect_type()
        self.apply_types()

    def refresh(self):
        """
        Refresh the dataframe
        """
        self.dataframe = self.method()
        self.apply_types()

    def detect_type(self):
        """
        Auto detect types of the current dataframe (will omit the detection on columns that already have their types in self.types)
        """

        def detect_type(values):
            type = auto_type_list(values)
            name = values.name
            if type is not None and name not in self.types:
                self.types[name] = type

        self.dataframe.apply(detect_type)

    def apply_types(self):
        """
        Format the dataframe based on the inner types
        """
        if self.dataframe is None:
            return

        def format_dataframe(values):
            type = self.types.get(values.name)
            if type is None:
                type = lambda x: x
            return [
                type(value) if value != AGGREGATION_FIELD else AGGREGATION_FIELD for value in values
            ]

        self.dataframe.update(self.dataframe.apply(format_dataframe))


def refreshed(query: Query) -> Query:
    """
    Create a new Query with a refreshed dataframe
    """
    return Query(query.method, query.types)
