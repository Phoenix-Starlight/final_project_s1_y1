import re
import typing
from collections import Counter
from dataclasses import dataclass, fields
from os import PathLike
from typing import Any, Callable, Iterable, Protocol, TextIO, Type

@dataclass
class Unique(Protocol):
    unique: list[str]


@dataclass
class Student(Unique):
    id: int
    name: str
    email: str
    unique = ["id", "email"]


@dataclass
class Course(Unique):
    id: str
    name: str
    unique = ["id", "name"]


@dataclass
class Grade(Unique):
    student_id: int
    course_name: str
    marks: list[int]
    letter_grade: str
    unique = ["student_id", "course_name"]


def verify_table_headers(structure: Iterable[str], headers: Iterable[str]) -> bool:
    return has_duplicate_headers(headers) or set(structure) == set(headers)


def has_duplicate_headers(headers: Iterable[str]) -> bool:
    return any(count != 1 for count in Counter(headers).values())


# Match content and stop at commas, and capture arrays by matching for content inbetween [] ending with a comma
# For example 1,2,2,[2],
data_regex = r"(\[.*?\])|(.*?),"


def try_parse(cell_data: str, type: Callable[..., Any]):
    try:
        result = parse_array(cell_data, type) or type(cell_data)
        if result is None:
            raise ValueError()
        return result
    except ValueError as e:
        raise ValueError(f"Could not parse {cell_data} as `{type}`") from e


def parse_array(arr: str, type: Callable[..., Any]) -> list | None:
    if arr[0] == "[" and arr[-1] == "]":
        if arr[1:-1][-1] == ",":
            raise ValueError("Bad array: expected element after ,")
        array = arr[1:-1].split(",")
        # convert array to list[T]
        if typing.get_origin(type) is not list:
            raise TypeError("Bad schema: expected parameterized list")
        element_type: Callable[[str],] = typing.get_args(type)[0]
        return [element_type(e) for e in array]
    return None


def parse_data_row(datum: str) -> list[str]:
    return [
        item.rstrip(",")
        for match in re.finditer(data_regex, datum)
        for item in match.groups()
        if item is not None
    ]
