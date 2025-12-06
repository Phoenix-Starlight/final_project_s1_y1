import traceback
from typing import Any, Callable

import db


def catch_and_log(x: Callable[..., Any]):
    def log():
        try:
            x()
        except Exception:
            traceback.print_exc()

    return log


@catch_and_log
def load_duplicate_data():
    db.Database("invalid-students.txt", db.Student)


@catch_and_log
def insert_non_unique_email():
    students = db.Database("valid-students.txt", db.Student)
    with students:
        students.insert(db.Student(0, "John", "example@example.com"))
        students.insert(db.Student(1, "Jane", "example@example.com"))


load_duplicate_data()
insert_non_unique_email()
