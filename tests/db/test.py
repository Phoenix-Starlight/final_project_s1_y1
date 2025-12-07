import os
from pathlib import Path
from typing import Any, Callable, cast

import db

# Change path to tests/db (parent of test.py) to not contaminate
os.chdir(Path(__file__).parent)

test_results: dict[str, bool] = {}


def catch_and_log(x: Callable[..., Any]):
    def log():
        try:
            try:
                x()
            except ExceptionGroup as e:
                print(e)
                for e in e.exceptions:
                    print(e)
                print("Task failed successfully")
                raise e
            except Exception as e:
                print(e)
                print("Task failed successfully")
                raise e
        except Exception:
            test_results[x.__name__] = True

    return log


def succeed(x: Callable):
    def should_pass():
        try:
            x()
            test_results[x.__name__] = True
        except Exception:
            test_results[x.__name__] = False

    return should_pass


@catch_and_log
def load_duplicate_data():
    db.Database("invalid-students.txt", db.Student)


@succeed
def load_database():
    db.Database("valid-students.txt", db.Student)


@succeed
def insert_first_record():
    with students:
        students.insert(db.Student(0, "John", "example@example.com"))
        email_identifier = ("email", "example@example.com")
        print(
            f"students.read(id_identifier) == students.read(email_identifier)? {students.read(id_identifier) == students.read(email_identifier)}"
        )


@succeed
def insert_second_record():
    with students:
        students.insert(db.Student(1, "John", "john@example.com"))


@succeed
def read_second_record():
    with students:
        record = students.read(("id", 1))
        print(f"{record} is not None? {record is not None}")


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


@succeed
def update_name():
    with students:
        students.update(id_identifier, db.Student(0, "Jane", "example@example.com"))
        jane = students.read(id_identifier)
    # Reopen to flush changes
    with students:
        same_jane = students.read(("id", 0))
        print(f"jane == same_jane? {jane == same_jane}")


@succeed
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

try:
    Path.unlink(Path("students.txt"))
except Exception:
    pass

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
insert_first_record()
update_name()
insert_second_record()
delete_jane()

Path.unlink(Path("students.txt"))

categorized_test_results: dict[bool, list[str]] = {True: [], False: []}
for name, success in test_results.items():
    categorized_test_results[success].append(name)
if (failed_tests := len(categorized_test_results[False])) == 0:
    print("TESTS PASSED")
    exit()

print(f"{failed_tests}/{len(test_results)} TESTS FAILED")
