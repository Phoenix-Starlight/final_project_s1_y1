from db.errors import UniqueError
from .db import Course, Grade, Student
from .db.data import courses, grades, students
from .db.schema import letter_grade as grade
from .export import export_course_report, export_student_report
from .reports import generate_course_summary, generate_student_performance_report

def print_on_duplicate_error(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except UniqueError as e:
            print(f"`{e.record[e.index]}` already exists in column `{e.index}`")
            input("Press enter to continue...")
    return wrapper


def validate_student_details(student_id, name, email):
    bad_id = False
    try:
        int(student_id)
    except ValueError:
        bad_id = True
    return {"email": "@" in email and "." in email.split("@")[1], "name": bool(name), "id": bad_id}

@print_on_duplicate_error
def add_new_student():
    print("Option 1: Add New Student")
    print("Input Student Details:\n")

    student_id = input("Student ID: ").strip()
    name = input("Name: ").strip()
    email = input("Email: ").strip()

    if not (validated := validate_student_details(student_id, name, email)):
        message = []
        for item in [k for k, v in validated.items() if not v]:
            match item:
                case "email":
                    message.append(f"Invalid email {email}!")
                case "name":
                    message.append(f"Invalid name {name}!")
                case "id":
                    message.append(f"Invalid ID {student_id}!")
        return

    id = int(student_id)

    db = students()
    existing = db.read(("id", student_id))
    if existing:
        print(f"Error: Student ID {student_id} already exists!")
        return

    student = Student(id, name, email)
    with db:
        db.insert(student)
    print(f"Student {name} added successfully!")

@print_on_duplicate_error
def add_new_course():
    print("Option 2: Add New Course")
    print("Input Course Details:\n")

    course_id = input("Course ID: ").strip()
    course_name = input("Course Name: ").strip()

    if not course_id.isalnum():
        print("Invalid Course ID! Should be alphanumeric.")
        return

    if not course_name.isascii():
        print("Invalid Course Name! Must use ASCII and not be empty.")
        return

    with courses() as db:
        course = Course(course_id, course_name)
        db.insert(course)

    print(f"Course {course_name} added successfully!")

@print_on_duplicate_error
def record_student_marks():
    print("Option 3: Record Student Marks")
    print("Select Student and Course\n")

    student_db = students()
    course_db = courses()
    grade_db = grades()

    student_id = input("Student ID: ").strip()
    course_id = input("Course ID: ").strip()

    try:
        id = int(student_id)
    except ValueError:
        print("Invalid student ID! Should be a number.")
        return

    if not course_id.isalnum():
        print("Invalid Course ID! Should be alphanumeric.")
        return

    student = student_db.read(("id", id))
    if not student:
        print(f"Error: Student ID {student_id} not found!")
        return

    course = course_db.read(("id", course_id))
    if not course:
        print(f"Error: Course ID {course_id} not found!")
        return

    marks_input = input("Enter marks (separate multiple marks with spaces): ").strip()

    if marks_input:
        try:
            marks = [int(mark) for mark in marks_input.split()]
        except ValueError:
            print("Error: Please enter valid numbers!")
            return
    else:
        marks = []

    letter_grade = grade(marks)

    with grade_db:
        grade_db.insert(Grade(f"{student_id}+{course.name}", marks, grade(marks)))

    print(f"Marks recorded successfully! Letter Grade: {letter_grade}")


def display_student_performance():
    print("Option 4: Display Student Performance")
    print("Select Student\n")

    student_id = input("Student ID: ").strip()

    try:
        id = int(student_id)
    except ValueError:
        print("Invalid student ID! Should be a number.")
        return

    if not students().read(("id", id)):
        print("Student not found, please enter again.")
        return

    print(generate_student_performance_report(students(), courses(), grades(), id))


def display_course_summary():
    print("Option 5: Display Course Summary")
    print("Select Course\n")

    course_id = input("Course ID: ").strip()

    if not course_id.isalnum():
        print("Invalid Course ID! Should be alphanumeric.")
        return

    course_db = courses()

    course = course_db.read(("id", course_id))

    if not course:
        print(f"Error: Course ID {course_id} not found!")
        return

    print(generate_course_summary(students(), courses(), grades(), course_id))


def export_report():
    print("Option 6: Export Report")
    print("Select Report Type\n")

    while True:
        print("1. Export Student Report")
        print("2. Export Course Report")
        print("3. Return to Main Menu")
        choice = input("Select option (1/2/3): ")
        match choice:
            case "1":
                student_id = input("Enter Student ID: ")

                try:
                    id = int(student_id)
                except ValueError:
                    print("Invalid student ID! Should be a number.")
                    return

                if not students().read(("id", id)):
                    print("Student not found, please enter again.")
                    return

                return export_student_report(students(), courses(), grades(), id)
            case "2":
                course_id = input("Enter Course ID: ")

                if not course_id.isalnum():
                    print("Invalid Course ID! Should be alphanumeric.")
                    return

                course_db = courses()

                course = course_db.read(("id", course_id))

                if not course:
                    print(f"Error: Course ID {course_id} not found!")
                    return

                return export_course_report(students(), courses(), grades(), course_id)
            case "3":
                print("Returning to Main Menu")
                break
            case _:
                print("Invalid selection")


# main menu


def main():
    print("Student Grading System\n")

    while True:
        print("\nMain Menu:")
        print("1. Add New Student")
        print("2. Add New Course")
        print("3. Record Student Marks")
        print("4. Display Student Performance")
        print("5. Display Course Summary")
        print("6. Export Report")
        print("7. Exit Program")

        selection = input("\nPlease Enter Your Selection (1-7): ").strip()

        if not selection.isdigit():
            print("Invalid Input! Please enter an integer (1-7).")
            continue

        selection = int(selection)

        match selection:
            case 1:
                add_new_student()
            case 2:
                add_new_course()
            case 3:
                record_student_marks()
            case 4:
                display_student_performance()
            case 5:
                display_course_summary()
            case 6:
                export_report()
            case 7:
                print("Option 7: Exit Program")
                print("Program End.")
                break
            case _:
                print("Invalid input! Please enter a number between 1 and 7.")
                continue


# Export only main function in wildcard
__all__ = ["main", "tests"]
