from reports import generate_course_summary, generate_student_performance_report


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
def export_student_report(students, courses, grades, student_id):
    filename = "Report_" + student_id + ".txt"
    with open(filename, "w") as f:
        f.write(generate_student_performance_report(students, courses, grades, student_id))
    return True

def export_course_report(students, courses, grades, course_id):
    filename = f"Report_{course_id}.txt"
    with open(filename, "w") as f:
        f.write(generate_course_summary(students, courses, grades, course_id))
    print(f"Report saved as {filename}")
    return True
