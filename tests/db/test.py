import os
import traceback
from pathlib import Path
from typing import Any, Callable

import db

# Change path to tests/db (parent of test.py) to not contaminate
os.chdir(Path(__file__).parent)


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


students = db.Database("valid-students.txt", db.Student)


@catch_and_log
def insert_non_unique_email():
    with students:
        students.insert(db.Student(1, "Jane", "example@example.com"))


@catch_and_log
def insert_twice():
    students.read(("id", 0))


load_duplicate_data()
insert_non_unique_email()
