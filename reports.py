from typing import Iterable

from .db import Course, Database, Grade


def generate_course_summary(students, courses, grades: Database[Grade], course_name):
    all_scores = [
        m for g in grades if g.student_id_and_course_name.split("+")[1] == course_name for m in g.marks
    ]

    if not all_scores:
        return "\n".join([
            "======= Course Summary Report =======",
            f"Course ID  : {courses.read(("name", course_name))}",
            "Course Name: " + course_name,
            "------- Student Results -------",
            "====================================="
        ])

    averages = [get_average(grade.marks) for grade in grades]
    average = round(sum(averages) / len(averages), 2)
    highest = get_highest_mark(averages)
    lowest = get_lowest_mark(averages)

    return "\n".join([
        "======= Course Summary Report =======",
        f"Course ID  : {courses.read(("name", course_name))}",
        "Course Name: " + course_name,
        "\n------- Student Results -------\n"
    ]
    + [f'{g["student_id"]} - {students.read(("id", g["student_id"]))["name"]}: {g["mark"]} - ({g["letter_grade"]})\n' for g in grades]
    + [
        "\n------- Statistics -------\n",
        f"Average Mark: {average}",
        f"Highest Mark: {highest}",
        f"Lowest Mark: {lowest}",
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
        ])

    return "\n".join(
        [
            "======= Student Performance Report =======",
            f"Student ID: {student_id}",
            f"Name      : {students.read(("id", student_id)).name}",
            f"Email     : {students.read(("id", student_id)).name}",
            "------- Course & Grades -------",
        ]
        + [
            f"{courses.read(("name", course_name)).id} - {course_name}: {g.marks} - {get_average(g.marks)} ({g.letter_grade})"
            for g in student_grades
            for student_id, course_name in [tuple(g.student_id_and_course_name.split("+"))]
        ] + [
            "==========================================",
        ]
    )


def get_average(grades):
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
