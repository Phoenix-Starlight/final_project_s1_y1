import db

students = db.Database("students.txt", db.Student)
with students:
    students.insert(db.Student(0, "John", "example@example.com"))
    students.insert(db.Student(1, "Jane", "example@example.com"))
