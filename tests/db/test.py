import os
import traceback
from pathlib import Path
from typing import Any, Callable, cast

import db

# Change path to tests/db (parent of test.py) to not contaminate
os.chdir(Path(__file__).parent)


def catch_and_log(x: Callable[..., Any]):
    def log():
        try:
            x()
        except ExceptionGroup as e:
            print(e)
            for e in e.exceptions:
                print(e)
            print("Task failed successfully")
        except Exception as e:
            print(e)
            print("Task failed successfully")

    return log


@catch_and_log
def load_duplicate_data():
    db.Database("invalid-students.txt", db.Student)


def load_database():
    db.Database("valid-students.txt", db.Student)


# Not wrapped as this should not fail
def insert_first_record():
    with students:
        students.insert(db.Student(0, "John", "example@example.com"))
        email_identifier = ("email", "example@example.com")
        print(
            f"students.read(id_identifier) == students.read(email_identifier)? {students.read(id_identifier) == students.read(email_identifier)}"
        )


@catch_and_log
def insert_non_unique_email():
    with students:
        students.insert(db.Student(1, "Jane", "example@example.com"))


@catch_and_log
def insert_twice():
    with students:
        students.insert(cast(db.Student, students.read(("id", 0))))


@catch_and_log
def update_unique_key():
    with students:
        students.update(id_identifier, db.Student(1, "John", "example@example.com"))


def update_name():
    with students:
        students.update(id_identifier, db.Student(0, "Jane", "example@example.com"))
        jane = students.read(id_identifier)
    # Reopen to flush changes
    with students:
        same_jane = students.read(("id", 0))
        print(f"jane == same_jane? {jane == same_jane}")


def delete_jane():
    with students:
        students.delete(id_identifier)
        print(
            f"students.read(id_identifier) is None? {students.read(id_identifier) is None}"
        )
    # Reopen to flush changes
    print("Close and reopen database")
    with students:
        students.delete(id_identifier)
        print(
            f"students.read(id_identifier) is None? {students.read(id_identifier) is None}"
        )


load_duplicate_data()
load_database()

print("Creating students.txt")
students = db.Database("students.txt", db.Student)

id_identifier = ("id", 0)


insert_first_record()
load_duplicate_data()
insert_non_unique_email()
insert_twice()
update_unique_key()
update_name()
delete_jane()

Path.unlink(Path("students.txt"))
