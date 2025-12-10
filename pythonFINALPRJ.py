# Validating ID
import db

def get_course_summary(course_name):
    grades = db.grades()
    all_scores = [
        m for g in grades if g["course_name"] == course_name for m in g["marks"]
    ]

    if not all_scores:
        return {
            "course": course_name,
            "average": None,
            "highest": None,
            "lowest": None,
            "count": 0,
        }

    return {
        "course": course_name,
        "average": sum(all_scores) / len(all_scores),
        "highest": max(all_scores),
        "lowest": min(all_scores),
        "count": len(all_scores),
    }


def get_student_performance_report(student_id):
    courses = db.courses()
    students = db.students()
    grades = db.grades()

    if not students.read(("id", student_id)):
        (print("Student not found, please enter again."),)
        return None

    student_grades = grades.read(("student_id", student_id))

    total = 0
    for g in student_grades:
        total += g["mark"]
    average = total / len(student_grades)

    return "\n".join(
        [
            "======= Student Performance Report =======",
            f"Student ID: {student_id}",
            f"Name      : {students[student_id]['name']}",
            f"Email     : {students[student_id]['email']}",
            "------- Course & Grades -------",
        ]
        + [
            f"{g['course_id']} - {courses[g['course_id']]}: {g['mark']} - ({g['letter_grade']})"
            for g in student_grades
        ]
        + [
            "Average Mark: "
            + str(
                round(
                    average,
                    2,
                )
            ),
            "==========================================",
        ]
    )
