import os

# define data
class Student:
    def __init__(self, student_id, name, email):
        self.id = student_id
        self.name = name
        self.email = email

class Course:
    def __init__(self, course_id, name):
        self.id = course_id
        self.name = name

class Grade:
    def __init__(self, student_id, course_name, marks, letter_grade):
        self.student_id = student_id
        self.course_name = course_name
        self.marks = marks  
        self.letter_grade = letter_grade

# database

def read_students():
   
    students = []
    try:
        with open("students.txt", "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(", ")
                    if len(parts) >= 3:
                        student_id = parts[0]
                        name = parts[1]
                        email = parts[2]
                        students.append(Student(student_id, name, email))
    except FileNotFoundError:
        
        open("students.txt", "w").close()
    return students

def write_student(student):
    with open("students.txt", "a") as f:
        f.write(f"{student.id}, {student.name}, {student.email}\n")

def read_courses():
    courses = []
    try:
        with open("courses.txt", "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(", ")
                    if len(parts) >= 2:
                        course_id = parts[0]
                        course_name = parts[1]
                        courses.append(Course(course_id, course_name))
    except FileNotFoundError:
        open("courses.txt", "w").close()
    return courses

def write_course(course):
    with open("courses.txt", "a") as f:
        f.write(f"{course.id}, {course.name}\n")

def read_grades():
    grades = []
    try:
        with open("grades.txt", "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(", ")
                    if len(parts) >= 4:
                        student_id = parts[0]
                        course_name = parts[1]
                        marks_str = parts[2]
                        letter_grade = parts[3]
                        
                        
                        marks = []
                        if marks_str:
                            marks = [int(mark) for mark in marks_str.split()]
                        
                        grades.append(Grade(student_id, course_name, marks, letter_grade))
    except FileNotFoundError:
        open("grades.txt", "w").close()
    return grades

def write_grade(grade):
    with open("grades.txt", "a") as f:
        marks_str = " ".join(str(mark) for mark in grade.marks)
        f.write(f"{grade.student_id}, {grade.course_name}, {marks_str}, {grade.letter_grade}\n")

def update_grade(student_id, course_name, new_marks, new_letter_grade):
    grades = read_grades()
    updated = False
    
    with open("grades.txt", "w") as f:
        for grade in grades:
            if grade.student_id == student_id and grade.course_name == course_name:
                f.write(f"{student_id}, {course_name}, {' '.join(str(m) for m in new_marks)}, {new_letter_grade}\n")
                updated = True
            else:
                marks_str = " ".join(str(mark) for mark in grade.marks)
                f.write(f"{grade.student_id}, {grade.course_name}, {marks_str}, {grade.letter_grade}\n")
    
    if not updated:
        grade = Grade(student_id, course_name, new_marks, new_letter_grade)
        write_grade(grade)

#tools

def calculate_letter_grade(marks):
    if not marks:
        return "N/A"
    
    average = sum(marks) / len(marks)
    
    if average >= 90:
        return "A"
    elif average >= 80:
        return "B"
    elif average >= 70:
        return "C"
    elif average >= 60:
        return "D"
    else:
        return "F"

def get_student_by_id(student_id):
    students = read_students()
    for student in students:
        if student.id == student_id:
            return student
    return None

def get_course_by_id(course_id):
    courses = read_courses()
    for course in courses:
        if course.id == course_id:
            return course
    return None

def get_course_by_name(course_name):
    courses = read_courses()
    for course in courses:
        if course.name == course_name:
            return course
    return None

# main function

def add_new_student():
    print("Option 1: Add New Student")
    print("Input Student Details:\n")
    
    student_id = input("Student ID: ").strip()
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    
    existing = get_student_by_id(student_id)
    if existing:
        print(f"Error: Student ID {student_id} already exists!")
        return
    
    student = Student(student_id, name, email)
    write_student(student)
    print(f"Student {name} added successfully!")

def add_new_course():
    print("Option 2: Add New Course")
    print("Input Course Details:\n")
    
    course_id = input("Course ID: ").strip()
    course_name = input("Course Name: ").strip()
    
    courses = read_courses()
    for course in courses:
        if course.id == course_id:
            print(f"Error: Course ID {course_id} already exists!")
            return
    
    course = Course(course_id, course_name)
    write_course(course)
    print(f"Course {course_name} added successfully!")

def record_student_marks():
    print("Option 3: Record Student Marks")
    print("Select Student and Course\n")
    
    student_id = input("Student ID: ").strip()
    course_id = input("Course ID: ").strip()
    
    student = get_student_by_id(student_id)
    if not student:
        print(f"Error: Student ID {student_id} not found!")
        return
    
    course = get_course_by_id(course_id)
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
    
    letter_grade = calculate_letter_grade(marks)
    
    update_grade(student_id, course.name, marks, letter_grade)
    
    print(f"Marks recorded successfully! Letter Grade: {letter_grade}")

def display_student_performance():
    print("Option 4: Display Student Performance")
    print("Select Student\n")
    
    student_id = input("Student ID: ").strip()
    
    student = get_student_by_id(student_id)
    if not student:
        print(f"Error: Student ID {student_id} not found!")
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
    
    course = get_course_by_id(course_id)
    if not course:
        print(f"Error: Course ID {course_id} not found!")
        return
    
    print(f"\nCourse: {course.name} ({course.id})")
    print("=" * 40)
    
    grades = read_grades()
    course_grades = [g for g in grades if g.course_name == course.name]
    
    if not course_grades:
        print("No grades recorded yet.")
        return
    
    all_marks = []
    enrolled_students = set()
    
    print("\nStudent Performance:")
    for grade in course_grades:
        student = get_student_by_id(grade.student_id)
        student_name = student.name if student else grade.student_id
        enrolled_students.add(student_name)
        
        if grade.marks:
            all_marks.extend(grade.marks)
            average = sum(grade.marks)/len(grade.marks)
            marks_str = ", ".join(str(mark) for mark in grade.marks)
            print(f"  {student_name}: Marks={marks_str}, Avg={average:.2f}, Grade={grade.letter_grade}")
        else:
            print(f"  {student_name}: No marks recorded")
    
    print("\nCourse Statistics:")
    print(f"  Enrolled Students: {len(enrolled_students)}")
    if all_marks:
        print(f"  Total Marks Recorded: {len(all_marks)}")
        print(f"  Overall Average: {sum(all_marks)/len(all_marks):.2f}")
        print(f"  Highest Mark: {max(all_marks)}")
        print(f"  Lowest Mark: {min(all_marks)}")

def export_report():
    
    print("Option 6: Export Report")
    print("Select Report Type\n")
    
    report_type = input("A. Student Report\nB. Course Report\n\nEnter A or B: ").strip().upper()
    
    if report_type == "A":
        student_id = input("Select Student ID: ").strip()
        
        student = get_student_by_id(student_id)
        if not student:
            print(f"Error: Student ID {student_id} not found!")
            return
        
        grades = read_grades()
        student_grades = [g for g in grades if g.student_id == student_id]
        
        filename = f"student_report_{student_id}.txt"
        with open(filename, "w") as f:
            f.write(f"STUDENT REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Student ID: {student.id}\n")
            f.write(f"Name: {student.name}\n")
            f.write(f"Email: {student.email}\n")
            f.write("=" * 50 + "\n\n")
            
            if student_grades:
                f.write("COURSE GRADES:\n")
                f.write("-" * 40 + "\n")
                
                for grade in student_grades:
                    course = get_course_by_name(grade.course_name)
                    course_id = course.id if course else "N/A"
                    
                    marks_str = ", ".join(str(mark) for mark in grade.marks) if grade.marks else "No marks"
                    average = sum(grade.marks)/len(grade.marks) if grade.marks else 0
                    
                    f.write(f"Course: {grade.course_name} ({course_id})\n")
                    f.write(f"  Marks: {marks_str}\n")
                    if grade.marks:
                        f.write(f"  Average: {average:.2f}\n")
                    f.write(f"  Final Grade: {grade.letter_grade}\n")
                    f.write("-" * 40 + "\n")
            else:
                f.write("No grades recorded.\n")
        
        print(f"Student report exported to {filename}")
        
    elif report_type == "B":
        course_id = input("Select Course ID: ").strip()
        
        course = get_course_by_id(course_id)
        if not course:
            print(f"Error: Course ID {course_id} not found!")
            return
        
        grades = read_grades()
        course_grades = [g for g in grades if g.course_name == course.name]
        
        filename = f"course_report_{course_id}.txt"
        with open(filename, "w") as f:
            f.write(f"COURSE REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Course ID: {course.id}\n")
            f.write(f"Course Name: {course.name}\n")
            f.write("=" * 50 + "\n\n")
            
            if course_grades:
                all_marks = []
                f.write("ENROLLED STUDENTS:\n")
                f.write("-" * 40 + "\n")
                
                for grade in course_grades:
                    student = get_student_by_id(grade.student_id)
                    student_name = student.name if student else grade.student_id
                    
                    if grade.marks:
                        marks_str = ", ".join(str(mark) for mark in grade.marks)
                        average = sum(grade.marks)/len(grade.marks)
                        all_marks.extend(grade.marks)
                        
                        f.write(f"Student: {student_name} ({grade.student_id})\n")
                        f.write(f"  Marks: {marks_str}\n")
                        f.write(f"  Average: {average:.2f}\n")
                        f.write(f"  Final Grade: {grade.letter_grade}\n")
                    else:
                        f.write(f"Student: {student_name} ({grade.student_id})\n")
                        f.write(f"  No marks recorded\n")
                    
                    f.write("-" * 40 + "\n")
                
                f.write("\nCOURSE STATISTICS:\n")
                f.write("-" * 40 + "\n")
                f.write(f"Total Enrolled Students: {len(course_grades)}\n")
                if all_marks:
                    f.write(f"Total Marks Recorded: {len(all_marks)}\n")
                    f.write(f"Overall Average: {sum(all_marks)/len(all_marks):.2f}\n")
                    f.write(f"Highest Mark: {max(all_marks)}\n")
                    f.write(f"Lowest Mark: {min(all_marks)}\n")
            else:
                f.write("No students enrolled or no grades recorded.\n")
        
        print(f"Course report exported to {filename}")
        
    else:
        print("Invalid Input!")
        return

# main menu

def main():
    for filename in ["students.txt", "courses.txt", "grades.txt"]:
        if not os.path.exists(filename):
            open(filename, "w").close()
    
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
        
        if selection == 1:
            add_new_student()
        elif selection == 2:
            add_new_course()
        elif selection == 3:
            record_student_marks()
        elif selection == 4:
            display_student_performance()
        elif selection == 5:
            display_course_summary()
        elif selection == 6:
            export_report()
        elif selection == 7:
            print("Option 7: Exit Program")
            print("Program End.")
            break
        else:
            print("Invalid input! Please enter a number between 1 and 7.")
            continue

if __name__ == "__main__":
    main()
    

