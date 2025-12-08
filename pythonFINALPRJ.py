# All the file-reading functions
def read_students():
    """Read students.txt and return a list of student dicts."""
    students = []
    with open("students.txt", "r") as f:
        for line in f:
            parts = line.strip().split(",")  # id,name,email
            if len(parts) < 3:
                continue
            students.append({
                "id": parts[0].strip(),
                "name": parts[1].strip(),
                "email": parts[2].strip()
            })
    return students


def read_grades():
    grades = []
    with open("grades.txt", "r") as f:
        for line in f:
            parts = line.strip().split(",")  # student_id,course_name,marks,letter_grade
            if len(parts) < 4:
                continue
            marks_field = parts[2].strip()
            
            if ";" in marks_field:
                marks = [float(x) for x in marks_field.split(";") if x.strip() != ""]
            else:
                try:
                    marks = [float(marks_field)]
                except:
                    marks = []

            grades.append({
                "student_id": parts[0].strip(),
                "course_name": parts[1].strip(),
                "marks": marks,
                "letter_grade": parts[3].strip()
            })
    return grades


def read_courses():
    courses = []
    with open("courses.txt", "r") as f:
        for line in f:
            parts = line.strip().split(",")  # id,name
            if len(parts) < 2:
                continue
            courses.append({
                "id": parts[0].strip(),
                "name": parts[1].strip()
            })
    return courses

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
