from collections import Counter
from dataclasses import fields
from types import GenericAlias
from typing import (
    Any,
    Callable,
    Iterable,
    Self,
    Sequence,
    TextIO,
    Type,
    cast,
)

from .index import BadIndex, IndexReference, T, create_indexes
from .parser import parse_row, try_parse, validate_table
from .schema import Course, Grade, Student, Unique, unique_keys


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


def _validate(db, object):
    for k in db._unique_columns:
        if (v := object[k]) in db._index[k]:
            raise BadIndex(k, v, object, db.insert)


class Database[T: Unique]:
    def __init__(self, file: str, structure: Type[T]) -> None:
        self.type = structure
        self.structure = dict(
            [(field.name, resolve_type(field.type)) for field in fields(structure)]
        )
        self.file = file
        # CLOSE FILE AFTER OPERATION: DOESN'T UPDATE
        self._initialize_db(file)
        cold_storage: Sequence[T] = load_db(file, self.type, self.structure)
        self._db: list[T | None] = list(cold_storage)
        self._unique_columns = unique_keys[self.type]
        self._index: IndexReference = dict(
            create_indexes(self._unique_columns, cold_storage)
        )

    @property
    def db(self):
        return [record for record in self._db if record is not None]

    def insert(self, object: T, validate: Callable[[Self, T], None] = _validate):
        if (t := type(object)) is not self.type:
            raise TypeError(f"{object} of type {t} does not match type {self.type}")
        validate(self, object)
        self._db.append(object)
        i = len(self._db) - 1
        for k in self._unique_columns:
            self._index[k][object[k]] = i

    def update(self, id: tuple[str, Any], obj: T) -> bool:
        if (record := self.read(id)) is None:
            return False
        exceptions = [
            ValueError(f"Modifying unique column `{f.name}` is disallowed")
            for f in fields(obj)
            if f.name in self._unique_columns
            if obj[f.name] != record[f.name]
        ]
        if len(exceptions) > 0:
            raise ExceptionGroup(
                "Uniqueness was violated",
                exceptions,
            )

        # Given that all indexes point to the same record in the list, we access the list and modify in place
        ref = self._index[id[0]][id[1]]

        self._db[ref] = obj

        return True

    def delete(self, id: tuple[str, Any]) -> bool:
        if (record := self.read(id)) is None:
            return False

        index: int = -1
        # Assert our indexes are not mangled and pointing to different records
        for k, v in {k: record[k] for k in self._unique_columns}.items():
            ref = self._index[k][v]
            if index == -1:
                index = ref
            elif index != ref:
                raise BadIndex(id[0], id[1], record, self.delete)
            del self._index[k][v]

        self._db[index] = None
        return True

    def read(self, id: tuple[str, Any]) -> T | None:
        if id[0] in self._index and id[1] in (index := self._index[id[0]]):
            return self._db[index[id[1]]]
        return None

    def _initialize_db(self, path: str):
        with open(path, "a+") as file:
            file.seek(0)
            if not file.read(1):
                self._write_headers(file)

    def _write_headers(self, file: TextIO):
        file.write(self._generate_headers())

    def _generate_headers(self):
        return ",".join([name for name, _ in self.structure.items()])

    def _write_db(self, file: TextIO) -> None:
        # Have to append \n
        file.writelines(
            map(
                lambda str: str + "\n",
                [self._generate_headers()]
                + generate_content(record for record in self._db if record is not None),
            )
        )

    # Enables `with` syntax
    def __enter__(self):
        return self

    def __exit__(self, type, _, __):
        if type:
            print(f"State of database: {self._db}")
            return
        # We know this is not None because __exit__ is only called after __enter__
        with open(self.file, "r+") as fd:
            # Empty database
            fd.truncate(0)
            self._write_db(fd)

    def __iter__(self):
        yield from self.db


def generate_content(db: Iterable[T]):
    return [
        ",".join([str(record[field.name]) for field in fields(record)]) for record in db
    ]


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


