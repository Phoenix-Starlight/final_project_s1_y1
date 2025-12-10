import statistics
from dataclasses import dataclass
from typing import Protocol


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


def letter_grade(marks: list[int]):
    try:
        grade = statistics.fmean(marks)
        if grade >= 80:
            return "A+"
        elif grade >= 75:
            return "A"
        elif grade >= 70:
            return "A-"
        elif grade >= 65:
            return "B+"
        elif grade >= 60:
            return "B"
        elif grade >= 55:
            return "B-"
        elif grade >= 50:
            return "C"
        elif grade >= 45:
            return "C-"
        elif grade >= 40:
            return "D"
        else:
            return "F"
    except Exception:
        return ""


unique_keys: dict[type, list[str]] = {
    Student: ["id", "email"],
    Course: ["id", "name"],
    Grade: ["student_id", "course_name"],
}
