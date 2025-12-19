from typing import Iterable

from .db import Course, Database, Grade


def generate_course_summary(students, courses, grades: Database[Grade], course_id):
    course = courses.read(("id", course_id))

    student_lines = []
    averages = []

    for g in grades:
        student_id, course_name = g.student_id_and_course_name.split("+")

        if course_name != course.name:
            continue

        student = students.read(("id", int(student_id)))
        if g.marks:
            avg = get_average(g.marks)
            averages.append(avg)
            student_lines.append(
            f"{student_id} - {student.name}:{g.marks} -  {avg} ({g.letter_grade})"
            )

    if not student_lines:
        return "\n".join([
            "======= Course Summary Report =======",
            f"Course ID  : {course.id}",
            f"Course Name:  {course.name}",
            "------- Student Results -------",
            "====================================="
        ])

    return "\n".join([
        "======= Course Summary Report =======",
        f"Course ID  : {course.id}",
        f"Course Name:  {course.name}",
        "\n------- Student Results -------\n"
    ]
    +student_lines
    + [
        "\n------- Statistics -------\n",
        f"Average Mark: {round(get_average(averages),2)}",
        f"Highest Mark: {get_highest_mark(averages)}",
        f"Lowest Mark: {get_lowest_mark(averages)}",
        "====================================="
    ])

def generate_student_performance_report(students, courses: Database[Course], grades: Database[Grade], student_id):
    student_grades = [grade for grade in grades.db if str(student_id) in grade.student_id_and_course_name]

    if not student_grades:
        return "\n".join([
            "======= Student Performance Report =======",
            f"Student ID: {student_id}",
            f"Name      : {students.read(("id", student_id)).name}",
            f"Email     : {students.read(("id", student_id)).email}",
            "------- Course & Grades -------",
            "==========================================",
            ""
        ])

    return "\n".join(
        [
            "======= Student Performance Report =======",
            f"Student ID: {student_id}",
            f"Name      : {students.read(("id", student_id)).name}",
            f"Email     : {students.read(("id", student_id)).email}",
            "------- Course & Grades -------",
        ]
        + [
            f"{courses.read(("name", course_name)).id} - {course_name}: {g.marks} - {get_average(g.marks) if g.marks else "N/A"} ({g.letter_grade})"
            for g in student_grades
            for student_id, course_name in [tuple(g.student_id_and_course_name.split("+"))]
        ] + [
            "==========================================",
            ""
        ]
    )


def get_average(grades):
    if grades:
        return None
    return sum_grades(grades) / len(grades)


def get_highest_mark(grades):
    highest = grades[0]
    for g in grades:
        if g > highest:
            highest = g
    return highest


def get_lowest_mark(grades):
    lowest = grades[0]
    for g in grades:
        if g < lowest:
            lowest = g
    return lowest


def sum_grades(grades: Iterable[int]):
    total = 0
    for g in grades:
        total += g
    return total
