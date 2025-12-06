from collections import Counter
from dataclasses import dataclass, fields
from os import PathLike
from types import GenericAlias
from typing import Any, Callable, Iterable, Protocol, TextIO, Type, cast

from parser import parse_row, try_parse, validate_table


@dataclass(frozen=True)
class Unique(Protocol):
    def __getitem__(self, name):
        return getattr(self, name)


@dataclass(frozen=True)
class Student(Unique):
    id: int
    name: str
    email: str


@dataclass(frozen=True)
class Course(Unique):
    id: str
    name: str


@dataclass(frozen=True)
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
        self.index: dict[str, dict[Any, T]] = dict(
            create_indexes(unique_keys[self.type], self.db)
        )

    def insert(self, object: T):
        if type(object) is not self.type:
            raise TypeError()
        self.db.append(object)

    def update(self, id: tuple[str, Any], obj: T):
        # Do in-place replacement of self.db;
        pass

    def delete(self, id: tuple[str, Any]):
        pass

    def read(self, id: tuple[str, str]):
        pass


def create_indexes[T: Unique](
    unique_keys: list[str], db: list[T]
) -> dict[str, dict[Any, T]]:
    indexes: dict[str, dict[Any, T]] = {}
    for key in unique_keys:
        indexes[key] = {}
        for record in db:
            if (index := record[key]) in indexes[key]:
                raise ValueError(
                    f"Bad index for `{key}`: value `{index}` already present"
                )
            indexes[key][record[key]] = record

    return indexes


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
