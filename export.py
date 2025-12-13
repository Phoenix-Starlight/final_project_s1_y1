from reports import generate_course_summary, generate_student_performance_report


def export_student_report(students, courses, grades):
    student_id = input("Enter Student ID: ")
    if student_id not in students:
        print("Student not found, please enter again.")
        return False
    student_grades = []
    for g in grades:
        if g["student_id"] == student_id:
            student_grades.append(g)
    if len(student_grades) == 0:
        print("No grades found for this student, please enter again.")
        return False
    total = 0
    for g in student_grades:
        total += g["mark"]
    average = total / len(student_grades)
    filename = "Report_" + student_id + ".txt"
    with open(filename, "w") as f:
        f.write(generate_student_performance_report(students, courses, grades, student_id))
    return True


def sum_grades(course_grades):
    total = 0
    for g in course_grades:
        total += g["mark"]
    return total


def export_course_report(students, courses, grades):
    course_id = input("Enter Course ID: ")
    if course_id not in courses:
        print("Course not found, please enter again.")
        return False
    course_grades = []
    for g in grades:
        if g["course_id"] == course_id:
            course_grades.append(g)
    if len(course_grades) == 0:
        print("No grades found for this course, please enter again.")
        return False

    filename = f"Report_{course_id}.txt"
    with open(filename, "w") as f:
        f.write(generate_course_summary(students, courses, grades))
    print(f"Report saved as {filename}")
    return True


def get_average(course_grades):
    return sum_grades(course_grades) / len(course_grades)


def get_highest_mark(course_grades):
    highest = course_grades[0]["mark"]
    for g in course_grades:
        if g["mark"] > highest:
            highest = g["mark"]
    return highest

def get_lowest_mark(course_grades):
    lowest = course_grades[0]["mark"]
    for g in course_grades:
        if g["mark"] < lowest:
            lowest = g["mark"]
    return lowest