# Validating ID
import db


def generate_course_summary(students, courses, grades, course_name):
    all_scores = [
        m for g in grades if g["course_name"] == course_name for m in g["marks"]
    ]


    if not all_scores:
        return "\n".join([
            "======= Course Summary Report =======",
            f"Course ID  : {courses.read(("name", course_name))}",
            "Course Name: " + course_name,
            "------- Student Results -------",
            "====================================="
        ])

    average = round(get_average(grades), 2)
    highest = get_highest_mark(grades)
    lowest = get_lowest_mark(grades)

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

def generate_student_performance_report(courses, students, grades, student_id):
    student_grades = grades.read(("student_id", student_id))

    if not student_grades:
        return "\n".join([
            "======= Student Performance Report =======",
            f"Student ID: {student_id}",
            f"Name      : {students.read(("id", student_id)).name}",
            f"Email     : {students.read(("id", student_id)).email}",
            "------- Course & Grades -------",
            "==========================================",
        ])

    total = 0
    for g in student_grades:
        total += g["mark"]
    average = total / len(student_grades)

    return "\n".join(
        [
            "======= Student Performance Report =======",
            f"Student ID: {student_id}",
            f"Name      : {students.read(("id", student_id)).name}",
            f"Email     : {students.read(("id", student_id)).name}",
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


def sum_grades(course_grades):
    total = 0
    for g in course_grades:
        total += g["mark"]
    return total
