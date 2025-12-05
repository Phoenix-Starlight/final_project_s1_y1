from collections import Counter
from dataclasses import dataclass, fields
from os import PathLike
from types import GenericAlias
from typing import Any, Callable, Iterable, Protocol, TextIO, Type, cast

from parser import parse_row, try_parse, validate_table


@dataclass
class Unique(Protocol):
    pass


@dataclass
class Student(Unique):
    id: int
    name: str
    email: str


@dataclass
class Course(Unique):
    id: str
    name: str


@dataclass
class Grade(Unique):
    student_id: int
    course_name: str
    marks: list[int]
    letter_grade: str


unique_keys: dict[type, list[str]] = {
    Student: ["id", "email"],
    Course: ["id", "name"],
    Grade: ["student_id", "course_name"],
}


def verify_table_headers(structure: Iterable[str], headers: Iterable[str]) -> bool:
    return has_duplicate_headers(headers) or set(structure) == set(headers)


def has_duplicate_headers(headers: Iterable[str]) -> bool:
    return any(count != 1 for count in Counter(headers).values())


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

    validate_table(table)

    for row in table:
        [
            try_parse(cell, column_type)
            for column_type, cell in zip(
                [structure[header] for header in headers], parse_row(row)
            )
        ]

    return [
        constructor(
            **{
                header: try_parse(cell, structure[header])
                for header, cell in zip(headers, parse_row(row))
            }
        )
        for row in table
    ]


class Database[T: Unique]:
    def __init__(self, file: PathLike, structure: T) -> None:
        self.type = type(structure)
        self.structure = dict(
            [(field.name, resolve_type(field.type)) for field in fields(structure)]
        )
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


def resolve_type(t: Type[Any] | str | Any) -> Callable[..., Any]:
    match t:
        # We have some class T
        case GenericAlias():
            return cast(Callable, t)
        case type():
            return t
        # We got a forward reference here.
        case str():
            if (func := globals().get(t)) is None:
                raise ValueError(f"{t} could not be resolved")
            return func
        # This is an illogical type; there is no use for a solely empty column
        case None:
            raise ValueError("'None' is not a valid type")
        # Still has something that returns an object of type t.
        case _:
            return t
