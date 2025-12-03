Contents
# Records
The following operations on the database is supported:
Insert
Update
Read
Delete

The following databases are available to be read:
students.txt
courses.txt
grades.txt

Each respectively returns the following data for a row:

`students.txt` -> `Student ID (Unique), Name, Email (Unique)`

`courses.txt` -> `Course ID (Unique), Course Name (Unique)`

`grades.txt` -> `Student ID, Course Name, marks (Array of numbers), Letter Grade`

```py
class Student:
    id: int
    name: str
    email: str
    
class Course:
    id: str
    name: str

class Grade:
    student_id: int
    course_name: str
    marks: list[int]
    letter_grade: str
```

# Database format
The database is where student records are kept and maintained. Due to time constraints, the database is not general purpose.

The database format specification follows below:
1. A comma seperates data in columns. For example `A,B` represents A and B in the first and second column.
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
This means the second row is the first real row, of which A = 1, B = 2, and C = 3.

## Arrays
Arrays are defined as follow:
1. `[` is the opening marker of an array
2. `]` is the closing marker of an array
3. `,` within the opening and closing marker seperates data.

## Uniqueness
A reserved field `unique` is kept for unique columns.
A unique column may not have two rows where `x = x`.
A unique column can be used to identify a record.

# Internal specification
In order to load a database file we perform the following algorithm:
1. Obtain header rows
2. Check the headers match the type specified
   This is done via iterating over the field names presented by the type and checking that it matches the headers.
   This is strict equality, if a type structurally is a superset or subset then we raise an error.
3. Split the remaining rows by the specification above.
4. For each cell obtained, we find the type associated to the header and attempt to construct it using the string contents in the cell.
