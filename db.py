from dataclasses import dataclass, fields
from os import PathLike
from typing import TYPE_CHECKING, TextIO, Type

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

@dataclass
class Student:
    id: int
    name: str
    email: str
    unique = ["id", "email"]
    
@dataclass
class Course:
    id: str
    name: str
    unique = ["id", "name"]

@dataclass
class Grade:
    student_id: int
    course_name: str
    marks: list[int]
    letter_grade: str
    unique = ["student_id", "course_name"]
