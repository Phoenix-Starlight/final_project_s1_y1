import os
import traceback
from pathlib import Path
from typing import Any, Callable, cast

import db
from db.schema import letter_grade

# Change path to tests/db (parent of test.py) to not contaminate
os.chdir(Path(__file__).parent)

test_results: dict[str, bool] = {}


def catch_and_log(x: Callable[..., Any]):
    def log(*args):
        try:
            try:
                x(*args)
            except ExceptionGroup as e:
                print(e)
                for e in e.exceptions:
                    print(e)
                print("Task failed successfully")
                raise e
            except (TypeError, ValueError) as db_error:
                if any("function" in str(msg) for msg in db_error.args):
                    raise Exception(db_error)
                print(db_error)
                print("Task failed successfully")
                raise db_error
        except (ExceptionGroup, TypeError, ValueError):
            test_results[x.__name__] = True

    return log


def succeed(x: Callable):
    def should_pass(*args):
        try:
            x(*args)
            test_results[x.__name__] = True
        except Exception:
            test_results[x.__name__] = False
            traceback.print_exc()

    return should_pass


@catch_and_log
def load_duplicate_data():
    db.Database("invalid-students.txt", db.Student)


@succeed
def load_database():
    db.Database("valid-students.txt", db.Student)


@succeed
def insert_first_record(students):
    with students:
        students.insert(db.Student(0, "John", "example@example.com"))
        email_identifier = ("email", "example@example.com")
        print(
            f"students.read(id_identifier) == students.read(email_identifier)? {students.read(id_identifier) == students.read(email_identifier)}"
        )


@succeed
def insert_second_record(students):
    with students:
        students.insert(db.Student(1, "John", "john@example.com"))


@succeed
def read_second_record(students):
    with students:
        record = students.read(("id", 1))
        print(f"{record} is not None? {record is not None}")


@catch_and_log
def insert_non_unique_email(students):
    with students:
        students.insert(db.Student(1, "Jane", "example@example.com"))


@catch_and_log
def insert_twice(students):
    with students:
        students.insert(cast(db.Student, students.read(("id", 0))))


@catch_and_log
def update_unique_key(students):
    with students:
        students.update(id_identifier, db.Student(1, "John", "example@example.com"))


@succeed
def update_name(students):
    with students:
        students.update(id_identifier, db.Student(0, "Jane", "example@example.com"))
        jane = students.read(id_identifier)
    # Reopen to flush changes
    print("Close and reopen database")
    with students:
        same_jane = students.read(("id", 0))
        print(f"jane == same_jane? {jane == same_jane}")


@succeed
def delete_jane(students):
    success = False
    with students:
        attempt = students.delete(id_identifier)
        repeat_attempt = students.delete(id_identifier)

        result = students.read(id_identifier) is None
        print(f"students.read({id_identifier}) is None? {result}")
        success |= attempt and not repeat_attempt and result
    # Reopen to flush changes and use new database to ensure it is in sync with disk
    print("Close and reopen database")
    with db.students() as students:
        result = students.read(id_identifier) is None
        print(f"students.read({id_identifier}) is None? {result}")
        success &= result
    if not success:
        raise AssertionError()


load_duplicate_data()
load_database()

try:
    Path.unlink(Path(f"{db.data_dir}/students.txt"))
except Exception:
    pass

print(f"Creating {db.data_dir}/students.txt")
succeed(db.students)()
id_identifier = ("id", 0)
for test in [
    insert_first_record,
    insert_non_unique_email,
    insert_twice,
    update_unique_key,
]:
    test(db.students())
print("Deleting students.txt")
Path.unlink(Path(f"{db.data_dir}/students.txt"))


@succeed
def test_update_then_delete():
    # This is a terrible solution for integration tests.
    global test_results
    original_test_results = test_results.copy()

    test_results.clear()

    print(f"Creating {db.data_dir}/students.txt")
    for test in [insert_first_record, update_name, insert_second_record, delete_jane]:
        test(db.students())
    tests = test_results
    test_results = original_test_results
    if any(not v for v in tests.values()):
        raise AssertionError()


test_update_then_delete()
print("Deleting students.txt")
Path.unlink(Path(f"{db.data_dir}/students.txt"))


@succeed
def test_course_db(courses):
    with courses:
        courses.insert(db.Course("CSC1204", "Programming Principles"))


try:
    Path.unlink(Path(f"{db.data_dir}/courses.txt"))
except Exception:
    pass

print(f"Creating {db.data_dir}/courses.txt")
test_course_db(db.courses())
print("Deleting courses.txt")
Path.unlink(Path(f"{db.data_dir}/courses.txt"))


@succeed
def test_grade_insertion():
    # This is a terrible solution for integration tests.
    global test_results
    original_test_results = test_results.copy()

    print(f"Creating {db.data_dir}/courses.txt")
    print(f"Creating {db.data_dir}/students.txt")
    students = db.students()
    courses = db.courses()

    # Already tested
    insert_first_record(students)
    with courses:
        courses.insert(db.Course("CSC1204", "Programming Principles"))

    print(f"Creating {db.data_dir}/grades.txt")
    grades = db.grades()

    test_results = original_test_results

    with grades:
        marks = [0, 100]
        grades.insert(db.Grade(0, "Programming Principles", marks, letter_grade(marks)))


test_grade_insertion()
print("Deleting students.txt, courses.txt, grades.txt")
for path in [
    f"{db.data_dir}/students.txt",
    f"{db.data_dir}/courses.txt",
    f"{db.data_dir}/grades.txt",
]:
    Path.unlink(Path(path))


@catch_and_log
def test_grade_insertion_fail():
    # This is a terrible solution for integration tests.
    global test_results
    original_test_results = test_results.copy()

    print(f"Creating {db.data_dir}/courses.txt")
    print(f"Creating {db.data_dir}/students.txt")
    students = db.students()
    courses = db.courses()

    # Aready tested
    insert_first_record(students)
    with courses:
        courses.insert(db.Course("CSC1204", "Programming Principles"))

    print(f"Creating {db.data_dir}/grades.txt")
    grades = db.grades()

    with grades:
        marks = [0, 100]
        grades.insert(db.Grade(f"{0}+CSC1204", marks, letter_grade(marks)))

    test_results = original_test_results
    if any(not v for v in test_results.values()):
        raise AssertionError()


test_grade_insertion_fail()
print("Deleting students.txt, courses.txt, grades.txt")
for path in [
    f"{db.data_dir}/students.txt",
    f"{db.data_dir}/courses.txt",
    f"{db.data_dir}/grades.txt",
]:
    Path.unlink(Path(path))

categorized_test_results: dict[bool, list[str]] = {True: [], False: []}
for name, success in test_results.items():
    categorized_test_results[success].append(name)
if (failed_tests := len(categorized_test_results[False])) == 0:
    print(f"{len(test_results)} TESTS PASSED")
    exit()

print(f"{failed_tests}/{len(test_results)} TESTS FAILED")
print(*[f"- Test `{failed_test}`\n" for failed_test in categorized_test_results[False]])
