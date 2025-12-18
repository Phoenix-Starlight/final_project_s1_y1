from .reports import generate_course_summary, generate_student_performance_report


def export_student_report(students, courses, grades, student_id):
    filename = f"Report_{student_id}.txt"
    with open(filename, "w") as f:
        f.write(generate_student_performance_report(students, courses, grades, student_id))
    print(f"Report saved as {filename}")
    return True

def export_course_report(students, courses, grades, course_id):
    filename = f"Report_{course_id}.txt"
    with open(filename, "w") as f:
        f.write(generate_course_summary(students, courses, grades, course_id))
    print(f"Report saved as {filename}")
    return True
