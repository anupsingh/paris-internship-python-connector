from typing import Any, Callable, Union, List, Dict

from .mdx import AGGREGATION_FIELD

Type = Union[Callable[[Any], Any], None]
Types = Dict[str, Type]


def type_priority(type: Type = None):
    return [type, int, float, str]


def auto_type(value: Any, type: Type = None) -> Any:
    """
    Try to detect the type of the given value.

    If the type is specified and if the value respects it, the type will be returned.
    Otherwise, it will check if the value is an int, then a float and if the value isn't one of those types,
    auto_type will return str
    """
    types = type_priority(type)
    if value == AGGREGATION_FIELD:
        return type
    for t in types:
        try:
            if t is not None:
                t(value)
                return t
        except:
            pass
    return types[-1]


def auto_type_list(values: List[Any], type: Type = None) -> List[Any]:
    """
    Try to detect the type that matches every values.

    If the type is specified and if the every values respects it, the type will be returned.
    Otherwise, it will check for int, then float and the default type is str.

    If one of the values doesn't match the specified type, it will check the next type.
    """
    types = type_priority(type)
    return types[max([types.index(auto_type(value, type)) for value in values])]
