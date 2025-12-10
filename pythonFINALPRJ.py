# Validating ID
def is_valid_student(student_id):
    # Any will return True if student_id exists within,it will be false otherwise.
    students = read_students()
    return any(s["id"] == student_id for s in students)

def get_individual(student_id):
    students = read_students()
    grades = read_grades()

    student = next((s for s in students if s["id"] == student_id), None)
    if not student:
        return None

    student_grades = [g for g in grades if g["student_id"] == student_id]

    return {
        "id": student["id"],
        "name": student["name"],
        "email": student["email"],
        "grades": student_grades
    }


def get_course_summary(course_name):
    grades = read_grades()
    all_scores = [m for g in grades if g["course_name"] == course_name for m in g["marks"]]

    if not all_scores:
        return {"course": course_name, "average": None, "highest": None, "lowest": None, "count": 0}

    return {
        "course": course_name,
        "average": sum(all_scores) / len(all_scores),
        "highest": max(all_scores),
        "lowest": min(all_scores),
        "count": len(all_scores)
    }
