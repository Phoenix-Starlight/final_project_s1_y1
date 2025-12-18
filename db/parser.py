import re
import typing
from typing import Any, Callable

# Match content and stop at commas, and capture arrays by matching for content inbetween [] ending with a comma
# Also capture uncaptured contents up to end of string (Catch "Y,X\n")
# For example 1,2,2,[2],
data_regex = r"(\[.*?\])|(.*?)(,|$)"


def try_parse(cell_data: str, type: Callable[..., Any], row_number: int) -> list[str]:
    try:
        result = parse_array(cell_data, type) or type(cell_data)
        if result is None:
            raise ValueError()
        return result
    except ValueError as e:
        err = ValueError(f"Could not parse {cell_data} as `{type}`")
        err.add_note(f"at row {row_number}")
        raise err from e


def parse_array(arr: str, type: Callable[..., Any]) -> list | None:
    if arr[0] == "[" and arr[-1] == "]":
        if arr[1:-1][:-2:-1] == ",":
            raise ValueError("Bad array: expected element after ,")
        array = arr[1:-1].split(",")
        # convert array to list[T]
        if typing.get_origin(type) is not list:
            raise TypeError("Bad schema: expected parameterized list")
        element_type: Callable[[str], list] = typing.get_args(type)[0]
        return [element_type(e) for e in array]
    return None


def parse_row(datum: str) -> list[str]:
    return [
        stripped
        for match in re.finditer(data_regex, datum)
        for item in match.groups()
        if item and (stripped := item.rstrip(","))
    ]


def validate_table(table: list[str]):
    for row_number, row in enumerate(table):
        if row[-1] == ",":
            e = ValueError("Bad database file: expected element after ,")
            e.add_note(f"at row {row_number}")
            raise e