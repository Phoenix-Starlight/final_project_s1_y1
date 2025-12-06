from collections import Counter
from dataclasses import dataclass, fields
from types import GenericAlias
from typing import (
    Any,
    Callable,
    Iterable,
    Protocol,
    TextIO,
    Type,
    TypeVar,
    cast,
)

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
        content = file.read().splitlines()
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


# Maintain a dynamically solved reference for easy updates
# Makes deletion harder
Index = dict[Any, Callable[[], int]]
IndexReference = dict[str, Index]


class Database[T: Unique]:
    def __init__(self, file: str, structure: Type[T]) -> None:
        self.type = structure
        self.structure = dict(
            [(field.name, resolve_type(field.type)) for field in fields(structure)]
        )
        self.file = file
        # CLOSE FILE AFTER OPERATION: DOESN'T UPDATE
        self._initialize_db(file)
        self._db: list[T] = load_db(file, self.type, self.structure)
        self._index: IndexReference = dict(
            create_indexes(unique_keys[self.type], self._db)
        )
        self._fd: TextIO | None = None

    def insert(self, object: T):
        if (t := type(object)) is not self.type:
            raise TypeError(f"{object} of type {t} does not match type {self.type}")
        for k in unique_keys[self.type]:
            if (v := object[k]) in self._index[k]:
                raise BadIndex(k, v)
        self._db.append(object)
        i = len(self._db) - 1
        for k in unique_keys[self.type]:
            self._index[k][object[k]] = lambda: i

    def update(self, id: tuple[str, Any], obj: T):
        exceptions = [
            ValueError(f"Modifying unique column `{k}` is disallowed")
            for k, v in id
            if obj[k] != v
        ]
        if len(exceptions) > 0:
            raise ExceptionGroup(
                "Uniquness was violated",
                exceptions,
            )
        if ref := self._index[id[0]][id[1]]:
            self._db[ref()] = obj

    def delete(self, id: tuple[str, Any]) -> bool:
        if ref := self._index[id[0]][id[1]]:
            del self._db[ref()]
            del self._index[id[0]][id[1]]
            return True
        return False

    def read(self, id: tuple[str, str]) -> T | None:
        if ref := self._index[id[0]][id[1]]:
            return self._db[ref()]

    def _initialize_db(self, path: str):
        with open(path, "a+") as file:
            file.seek(0)
            if not file.read(1):
                self._write_headers(file)

    def _write_headers(self, file: TextIO):
        file.write(self._generate_headers())

    def _generate_headers(self):
        return ",".join([name for name, _ in self.structure.items()])

    def _generate_content(self):
        return [
            ",".join([str(record[field.name]) for field in fields(record)])
            for record in self._db
        ]

    def _write_db(self, file: TextIO) -> None:
        # Have to append \n
        file.writelines(
            map(
                lambda str: str + "\n",
                [self._generate_headers()] + self._generate_content(),
            )
        )

    # Enables `with` syntax
    def __enter__(self):
        self._fd = open(self.file, "r+")
        return self

    def __exit__(self, type, _, __):
        # We know this is safe because __exit__ is only called after __enter__
        fd = cast(TextIO, self._fd)
        self._write_db(fd)
        fd.close()
        self._fd = None


# We say that it can be any subtype of Unique
T = TypeVar("T", bound=Unique, covariant=True)


def BadIndex(k, v):
    return ValueError(f"Bad index `{k}`: value `{v}` already present`")


def create_indexes(unique_keys: list[str], db: list[T]) -> IndexReference:
    return {key: create_index(db, key) for key in unique_keys}


def create_index(db: list[T], key: str):
    index: Index = {}
    for i, record in enumerate(db):
        if (v := record[key]) in index:
            raise BadIndex(key, v)
        index[v] = lambda: (i)
    return index


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
