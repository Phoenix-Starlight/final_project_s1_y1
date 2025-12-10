import os

from db import students, Student, courses, Course, grades
from db.schema import letter_grade as grade


# main function

def add_new_student():
    print("Option 1: Add New Student")
    print("Input Student Details:\n")
    
    student_id = input("Student ID: ").strip()
    name = input("Name: ").strip()
    email = input("Email: ").strip()

    with students() as db:
        existing = db.read(("id", student_id))
        if existing:
            print(f"Error: Student ID {student_id} already exists!")
            return

        student = Student(student_id, name, email)
        db.insert(student)
    print(f"Student {name} added successfully!")

def add_new_course():
    print("Option 2: Add New Course")
    print("Input Course Details:\n")
    
    course_id = input("Course ID: ").strip()
    course_name = input("Course Name: ").strip()

    # Want to differentiate
    with courses() as db:
        course = Course(course_id, course_name)
        db.insert(course)

    print(f"Course {course_name} added successfully!")

def record_student_marks():
    print("Option 3: Record Student Marks")
    print("Select Student and Course\n")

    student_db = students()
    course_db = courses()
    grade_db = grades()

    student_id = input("Student ID: ").strip()
    course_id = input("Course ID: ").strip()

                student = student_db.read(("id", student_id))
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

                grade_db.insert(student_id, course.name, marks, letter_grade)

                print(f"Marks recorded successfully! Letter Grade: {letter_grade}")

def display_student_performance():
    print("Option 4: Display Student Performance")
    print("Select Student\n")
    
    student_id = input("Student ID: ").strip()

    if not students().read(("id", student_id)):
        print("Student not found, please enter again.")
        return
    
    print(f"\nStudent: {student.name} ({student.id})")
    print("=" * 40)
    
    grades = read_grades()
    student_grades = [g for g in grades if g.student_id == student_id]
    
    if not student_grades:
        print("No grades recorded yet.")
        return
    
    for grade in student_grades:
        course = get_course_by_name(grade.course_name)
        course_id = course.id if course else "N/A"
        
        marks_str = ", ".join(str(mark) for mark in grade.marks) if grade.marks else "No marks"
        average = sum(grade.marks)/len(grade.marks) if grade.marks else 0
        
        print(f"\nCourse: {grade.course_name} ({course_id})")
        print(f"  Marks: {marks_str}")
        if grade.marks:
            print(f"  Average: {average:.2f}")
        print(f"  Letter Grade: {grade.letter_grade}")

def display_course_summary():
    print("Option 5: Display Course Summary")
    print("Select Course\n")
    
    course_id = input("Course ID: ").strip()

    course_db = courses()

    course = course_db.read(("id", course_id))

    if not course:
        print(f"Error: Course ID {course_id} not found!")
        return

    print(generate_course_summary(course_id))


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
                return export_student_report(students(), courses(), grades())
            case "2":
                return export_course_report(students(), courses(), grades())
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

if __name__ == "__main__":
    main()
    

