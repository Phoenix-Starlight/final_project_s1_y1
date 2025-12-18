import os
from pathlib import Path
from typing import cast
import unittest

import db
import db.data
from db import SchemaError
from db.errors import BadIndex
from db.schema import letter_grade

# Change path to tests/db (parent of test.py) to not contaminate
os.chdir(Path(__file__).parent)

test_results: dict[str, bool] = {}

class UnitTests(unittest.TestCase):
    def load_duplicate_data(self):
        db.Database("invalid-students.txt", db.Student)

    def load_database(self):
        db.Database("valid-students.txt", db.Student)

id_identifier = ("id", 0)

class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.students = db.data.students()
        self.courses = db.data.courses()
        self.grades = db.data.grades()

    def tearDown(self):
        for path in [
            f"{db.data.data_dir}/students.txt",
            f"{db.data.data_dir}/courses.txt",
            f"{db.data.data_dir}/grades.txt",
        ]:
            try:
                Path.unlink(Path(path))
            except FileNotFoundError:
                pass


    def insert_first_record(self):
        with self.students as students:
            students.insert(db.Student(0, "John", "example@example.com"))
            email_identifier = ("email", "example@example.com")
            return students.read(id_identifier) == students.read(email_identifier)

    def update_unique_key(self):
        with self.students as students:
            students.update(id_identifier, db.Student(1, "John", "example@example.com"))

    def insert_second_record(self):
        with self.students as students:
            students.insert(db.Student(1, "John", "john@example.com"))

    def read_second_record(self):
        with self.students as students:
            record = students.read(("id", 1))
            print(f"{record} is not None? {record is not None}")
    
    def insert_non_unique_email(self):
        with self.students as students:
            students.insert(db.Student(1, "Jane", "example@example.com"))

    def insert_twice(self):
        with self.students as students:
            students.insert(cast(db.Student, students.read(("id", 0))))

    def delete_first_record(self):
        with self.students as students:
            return students.delete(id_identifier)

    def test_insert(self):
        self.assertTrue(self.insert_first_record())

    def test_non_unique_insert(self):
        self.test_insert()
        self.assertRaises(BadIndex, self.insert_non_unique_email)

    def test_identical_insert(self):
        self.test_insert()
        self.assertRaises(BadIndex, self.insert_twice)

    def test_updating_unique_key(self):
        self.test_insert()
        with self.assertRaises(ExceptionGroup) as capture:
            self.update_unique_key()
        self.assertTrue(all(isinstance(e, SchemaError) for e in capture.exception.exceptions))

    def test_flushed_update(self):
        self.test_insert()
        with self.students as students:
            students.update(id_identifier, db.Student(0, "Jane", "example@example.com"))
            jane = students.read(id_identifier)
        with self.students as students:
            same_jane = students.read(("id", 0))
            self.assertEqual(jane, same_jane)

    def test_deletion(self):
        self.test_insert()
        self.insert_second_record()
        self.assertTrue(self.delete_first_record())

    def test_deletion_consistency(self):
        self.test_deletion()
        self.assertFalse(self.delete_first_record())

    def test_flushed_deletion(self):
        self.test_deletion_consistency()
        with self.students as students:
            self.assertTrue(students.read(id_identifier) is None)

    def test_grade_insertion(self):
        self.test_insert()
        with self.courses as courses:
            courses.insert(db.Course("CSC1204", "Programming Principles"))
            courses.insert(db.Course("CSC1205", "Programming"))

        with self.grades as grades:
            marks = [0, 100]
            grades.insert(db.Grade(f"{0}+Programming Principles", marks, letter_grade(marks)))
            grades.insert(db.Grade(f"{0}+Programming", marks, letter_grade(marks)))

    def test_grade_insertion_fail(self):
        self.test_insert()
        with self.courses as courses:
            courses.insert(db.Course("CSC1204", "Programming Principles"))

        with self.grades as grades:
            marks = [0, 100]
            self.assertRaises(SchemaError, lambda: grades.insert(db.Grade(f"{0}+CSC1204", marks, letter_grade(marks))))

if __name__ == "__main__":
    unittest.main()