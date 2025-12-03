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
2. A newline indicates the end of a row.
```csv
A,B
C,D
```
Represents row 1 and 2, whose contents are `A,B` and `C,D`
3. The first row labels the columns.
```csv
A,B,C
1,2,3
```
This means the second row is the first real row, of which A = 1, B = 2, and C = 3.

Turning the rows into data of appropriate types is the responsibility of the user.
Enforcing any other constraints is also the responsibility of the user.

Note that this is a further specification based upon the CSV format.

## Arrays
Arrays are defined as follow:
1. `[` is the opening marker of an array
2. `]` is the closing marker of an array
3. `,` within the opening and closing marker seperates data.