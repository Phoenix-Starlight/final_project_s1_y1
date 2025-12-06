from collections import Counter
from dataclasses import dataclass, fields
from types import GenericAlias
from typing import Any, Callable, Iterable, Protocol, TextIO, Type, TypeVar, cast

from .parser import parse_row, try_parse, validate_table


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
    return has_duplicate_headers(headers) or set(structure) != set(headers)


def has_duplicate_headers(headers: Iterable[str]) -> bool:
    return any(count != 1 for count in Counter(headers).values())


def load_db[T](
    path: str,
    constructor: Callable[..., T],
    structure: dict[str, Callable[..., Any]],
) -> list[T]:
    with open(path, "r") as file:
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
    def __init__(self, file: str, structure: Type[T]) -> None:
        self.type = structure
        self.structure = dict(
            [(field.name, resolve_type(field.type)) for field in fields(structure)]
        )
        self.file = file
        # CLOSE FILE AFTER OPERATION: DOESN'T UPDATE
        self.initialize_db(file)
        self.db: list[T] = load_db(file, self.type, self.structure)
        self.index: dict[str, dict[Any, Callable[[], T]]] = dict(
            create_indexes(unique_keys[self.type], self.db)
        )
        self._fd: TextIO | None = None

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

    def initialize_db(self, path: str):
        with open(path, "a+") as file:
            file.seek(0)
            if not file.read(1):
                self.write_headers(file)

    def write_headers(self, file: TextIO):
        file.write(",".join([name for name, _ in self.structure.items()]))

    def write_content(self, file: TextIO):
        file.writelines(
            [
                ",".join([str(record[field.name]) for field in fields(record)])
                for record in self.db
            ]
        )

    def write_db(self, file: TextIO) -> None:
        self.write_headers(file)
        self.write_content(file)

    def __enter__(self):
        self._fd = open(self.file, "r+")
        return self

    def __exit__(self, type, _, __):
        # We know this is safe because __exit__ is only called after __enter__
        fd = cast(TextIO, self._fd)
        self.write_db(fd)
        fd.close()
        self._fd = None


# We say that it can be any subtype of Unique
T = TypeVar("T", bound=Unique, covariant=True)

# Maintain a dynamically solved reference for easy updates
# Makes deletion harder
IndexReference = dict[str, dict[Any, Callable[[], T]]]


def create_indexes(unique_keys: list[str], db: list[T]) -> IndexReference:
    indexes: IndexReference = {}
    for key in unique_keys:
        indexes[key] = {}
        for index, record in enumerate(db):
            if (index := record[key]) in indexes[key]:
                raise ValueError(
                    f"Bad index for `{key}`: value `{index}` already present"
                )
            indexes[key][record[key]] = lambda: db[index]

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
