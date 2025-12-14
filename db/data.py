from pathlib import Path
from types import MethodType
from typing import Callable

from db import Database, Student, Course, Grade

data_dir = "data"


def data(x):
    def func():
        Path(data_dir).mkdir(exist_ok=True)
        return x()

    return func


@data
def students() -> Database[Student]:
    return Database("data/students.txt", Student)


@data
def courses() -> Database[Course]:
    return Database("data/courses.txt", Course)


@data
def grades() -> Database[Grade]:
    def enforce_dependence(insert: Callable[[Grade], None]):
        def hold_insert_func(self: Database[Grade], object: Grade):
            student_db = students()
            course_db = courses()

            if "+" not in object.student_id_and_course_name:
                raise ValueError(f"Record {object} does not have a composite key represented by `id+name` where id is in `students.txt` and name belongs to `courses.txt`")

            student_id, course_name = tuple(object.student_id_and_course_name.split("+"))
            id = int(student_id)
            if not student_db.read(("id", id)) or not course_db.read(
                ("name", course_name)
            ):
                raise ValueError(
                    f"Record {object} does not have respective keys {(student_id, course_name)} present in `students.txt` or `courses.txt`"
                )
            insert(object)

        return hold_insert_func

    # Enforce dependency on students and courses
    db = Database("data/grades.txt", Grade)
    db.insert = MethodType(enforce_dependence(db.insert), db)
    return db
