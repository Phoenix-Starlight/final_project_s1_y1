import re
import typing
from collections import Counter
from dataclasses import dataclass, fields
from os import PathLike
from types import GenericAlias
from typing import Any, Callable, Iterable, Protocol, TextIO, Type, TypeGuard, cast


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


def load_db[T](
    file: TextIO,
    constructor: Callable[..., T],
    structure: dict[str, Callable[..., Any]],
) -> list[T]:
    content = file.readlines()
    headers = content[0].split(",")
    table = content[1:]

    if verify_table_headers(structure, headers):
        raise ValueError("Bad database format")

    for row in table:
        if row[-1] == ",":
            raise ValueError("Bad database file: expected element after ,")
        [
            try_parse(cell, column_type)
            for column_type, cell in zip(
                [structure[header] for header in headers], parse_data_row(row)
            )
        ]
    if any(row[-1] == "," for row in table):
        raise ValueError("Bad database file: expected element after ,")

    return [
        constructor(
            **{
                header: try_parse(cell, structure[header])
                for header, cell in zip(headers, parse_data_row(row))
            }
        )
        for row in table
    ]


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


class Database[T: Unique]:
    def __init__(self, file: PathLike, structure: T) -> None:
        self.type = type(structure)
        self.structure = dict(
            filter(
                remove_unique_attribute,
                [(field.name, resolve_type(field.type)) for field in fields(structure)],
            )
        )
        self.unique = structure.unique
        self.file = file
        with open(file, "r") as csv:
            self.db: list[T] = load_db(csv, self.type, self.structure)

    def insert(self, object: T):
        if type(object) is not self.type:
            raise TypeError()
        self.db.append(object)

    def update(self, id: dict[str, str], obj: T):
        pass

    def delete(self, id: dict[str, str]):
        pass

    def read(self, id: dict[str, str]):
        pass


def return_tuple(structure: Unique):
    return [(field.name, resolve_type(field.type)) for field in fields(structure)]


def remove_unique_attribute[V](
    dict_tuple: tuple[str, V | None],
) -> TypeGuard[tuple[str, V]]:
    return dict_tuple[0] != "unique" and dict_tuple[1] is not None


def resolve_type(t: Type[Any] | str | Any) -> Callable[..., Any] | None:
    match t:
        # We have some class T
        case GenericAlias():
            return cast(Callable, t)
        case type():
            return t
        # We got a forward reference here.
        case str():
            return globals().get(t)
        # Don't know, give nothing.
        case _:
            return None
