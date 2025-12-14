# Table of Contents
1. [Usage](#usage)
2. [Records](#records)
3. [Database format](#database-format)
4. [Loading specification](#loading-specification)
5. [Schemas](#schema-declaration)
6. [Database specification](#database-specification)
# Usage

```py
import db.data
import db
from db.schema import letter_grade

students = db.data.students()
courses = db.data.courses()
grades = db.data.grades()
with students:
    students.insert(db.Student(0, "John", "john@example.com"))
    students.update(("id", 0), db.Student(0, "Johnny", "john@example.com"))
students.read(("id", 0))  # Student(id=0, name="Johnny", email="john@example.com")
with students:
    students.delete(("id", 0))
students.read(("id", 0))  # None
with courses:
    courses.insert(db.Course("CSC1204", "Programming Principles"))
with grades:
    marks = [50, 75]
    grades.insert(db.Grade(0, "Programming Principles", marks, letter_grade(marks)))
```

# Records
The following operations on the database is supported:
T is a variable that represents a type of interest.
- Insert: `insert(obj: T) -> None`
- Update: `update(id: tuple[str, Any], obj: T) -> None`
- Read: `read(id: tuple[str, Any]) -> T`
- Delete: `delete(id: tuple[str, Any]) -> bool`
- Iteration: `database.db`, or `for x in database`

The following databases are available to be read:
```
students.txt
courses.txt
grades.txt
```
Each respectively returns the following data for a row:

`students.txt`:`Student ID (Unique), Name, Email (Unique)`

`courses.txt`:`Course ID (Unique), Course Name (Unique)`

`grades.txt`:`Student ID+Course Name (Unique), marks (Array of numbers), Letter Grade`

```py
class Student:
    id: int
    name: str
    email: str
    
class Course:
    id: str
    name: str

class Grade:
    student_id_and_course_name: str # Composite key where we join them as f"{student_id}+{course_name}"
    marks: list[int]
    letter_grade: str
```

# Database format
The database is where student records are kept and maintained. Due to time constraints, the database is not generalized.

The database format specification follows below:
1. A comma separates data in columns. For example `A,B` represents A and B in the first and second column.
2. A newline indicates the end of a record.

   ```csv
   A,B 
   C,D
   ```
   Represents record 1 and 2, whose contents are `A,B` and `C,D`
3. The first row labels the columns.
   ```csv
    A,B,C
    1,2,3
    ```
This means the second row is the first real row, which has `A = 1, B = 2, C = 3`.

## Arrays
Arrays are defined as follow:
1. `[` is the opening marker of an array
2. `]` is the closing marker of an array
3. `,` within the opening and closing marker separates data.

As a note, this is belongs to a collection of CSV formats. We choose a specific delimiter `,` and define arrays to use unescaped commas.

This is also an entirely arbitrary choice.

## Uniqueness
An external source is kept for unique columns. This can be found in [schema.py](../db/schema.py) located before EOF.

It is an error for a unique column to have two rows where they share identical data in a unique column.

A unique column can be used to identify a record. This forms a tuple `(unique_column, id)` used in the `read` function.
Updating unique columns is forbidden.

# Loading specification
In order to load a database file we perform the following algorithm:
1. Obtain header rows from the file.
2. Check the headers match the schema (type)
   This is done via iterating over the field names presented by the type and checking that it matches the headers.
   This is strict equality, if a type structurally is a superset or subset then we raise an error.
3. Split the remaining rows by number 2 in the [spec above](#loading-specification)
4. For each cell (row-column) obtained processing each row, we find the type associated to the header and attempt to construct it using the string contents in the cell. For more on how the type metadata is associated see [below](#schema-declaration)

# Schema declaration
Schemas are declared by subclassing the structural type `Unique` and having a `@dataclass(frozen=True)` decorator.

It is required to make them frozen, else some changes may occur unexpectedly.

Additionally every field in a class representing a schema must be type hinted. Dataclasses and `None` are disallowed from being a type-hint.
```py
from db import Unique
from dataclasses import dataclass

@dataclass(frozen=True)
class Something(Unique):
    a: int
```

Using this code snippet, we have a procedure to extract it into a mapping of headers to types.

Onto type-hinting, Python is extremely free in its rules, exempting functions that require primitive types due to implementation in C.
There is structural (duck) subtyping, unenforced OO and nominal typing, and functions.
All type-hints are references to functions that may return a constructed type.

Let's say we have type `int`. Using the reference `int`, we can call it with `int("2")` to get `2`.
Using a bit of substitution, we can write it as `parameters -> T` which is represented as `Callable[[...], T]` or `Type[T]` or perhaps `GenericAlias(origin, args)`.
All of these functions can raise errors due to a variety of circumstances such as bad input, exceeding machine limitations, etc.

This spec enables step 4 in the [loading spec](#loading-specification).

# Database specification
The database should provide the ability to be iterated over.
As well, it should maintain an index for easy management of records. Operation(s) should be atomic.

We want atomicity as it enables easy rollback and ensures consistency.
For example, a program crashes inserting 3 records. We would rather have no changes, as repeating the operation again may pose problems (Uniqueness violation).

We require the ability to iterate over the database, as we anticipate that not every needed function is supported.
For this, the database should provide means to access a collection and iterate.

An index is not required to satisfy the properties of a database, however it is preferable.
An index enables easy access on unique keys and trivial management of records.

An index holds pointers to records, so if we want to delete a record, we null out the data and then remove the pointer.
It also enables easy insertion and access. We simply append the new record, and create indexes for it.
