from collections import Counter
from dataclasses import dataclass, fields
from os import PathLike
from typing import Any, Iterable, Protocol, TextIO, Type

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
