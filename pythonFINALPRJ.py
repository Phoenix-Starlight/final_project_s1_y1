run_program = 'Y'  #start program, from prac pythontest5

def read_students():
    students = []
    try:
        with open("students.txt", "r") as f:
            for line in f:
                parts = line.strip().split(",")  # id,name,email
                if len(parts) < 3:
                    continue
                students.append({"id": parts[0].strip(), "name": parts[1].strip(), "email": parts[2].strip()})
    except FileNotFoundError:
        print("students.txt file not found. Please create it in the same folder.")
    return students

def read_grades():
    grades = []
    try:
        with open("grades.txt", "r") as f:
            for line in f:
                parts = line.strip().split(",")  # student_id,course_name,marks,letter_grade
                if len(parts) < 4:
                    continue
                # here we assume marks field is either a single number or semicolon-separated numbers:
                marks_field = parts[2].strip()
                if ";" in marks_field:
                    marks = [float(x) for x in marks_field.split(";") if x.strip() != ""]
                else:
                    # single numeric mark
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
    except FileNotFoundError:
        print("grades.txt file not found. Please create it in the same folder.")
    return grades

def read_courses():
    courses = []
    try:
        with open("courses.txt", "r") as f:
            for line in f:
                parts = line.strip().split(",")  # id,name
                if len(parts) < 2:
                    continue
                courses.append({"id": parts[0].strip(), "name": parts[1].strip()})
    except FileNotFoundError:
        print("courses.txt file not found. Please create it in the same folder.")
    return courses

def validateIndividual_ID(student_id):
    students = read_students()
    for s in students:
        if s["id"] == student_id:
            return True
    return False

def view_individual(student_id):
    students = read_students()
    grades = read_grades()
    student = None
    for s in students:
        if s["id"] == student_id:
            student = s
            break
    if not student:
        print("Student not found.")
        return

    print(f"\n=== Student Information ===")
    print(f"ID: {student['id']}")
    print(f"Name: {student['name']}")
    print(f"Email: {student['email']}\n")

    print("--- Grades ---")
    found = False
    for g in grades:
        if g["student_id"] == student_id:
            found = True
            marks_display = ", ".join([str(int(m)) if m.is_integer() else str(m) for m in g["marks"]]) if g["marks"] else "N/A"
            print(f"{g['course_name']}: Marks=[{marks_display}], Letter={g['letter_grade']}")
    if not found:
        print("No grades found for this student")

def view_courseSum():
    grades = read_grades()
    courses = read_courses()
    course_name = input("Enter course name (exact): ").strip()
    # find course existence (optional)
    exists = any(c["name"] == course_name or c["id"] == course_name for c in courses)
    if not exists:
        ok = input("Course not found in courses list. Continue searching grades anyway? [Y/N] ").strip().upper()
        if ok != "Y":
            return

    # collect numeric marks (from marks arrays)
    all_scores = []
    for g in grades:
        if g["course_name"] == course_name:
            all_scores.extend(g["marks"])

    if not all_scores:
        print("No numeric marks found for this course.")
        return

    avg = sum(all_scores) / len(all_scores)
    highest = max(all_scores)
    lowest = min(all_scores)
    print(f"\nCourse: {course_name}")
    print(f"Average: {avg:.2f}")
    print(f"Highest: {highest}")
    print(f"Lowest: {lowest}")
    print(f"Number of marks: {len(all_scores)}")

# Main loop
while run_program.upper() == 'Y':
    choice = input("Would you like to view an specific Individual or Course Summary? (I/C) \n").strip().upper()
    if choice == 'I':
        student_id = input("Enter Student ID to view: \n").strip()
        if not validateIndividual_ID(student_id):
            print("invalid ID, no ID record found.")
            run_program = input("Would u like to try again? [Y/N]")
            continue
        view_individual(student_id)
    elif choice == 'C':
        view_courseSum()
    else:
        print('invalid choice selected')
        run_program = input("Would u like to try again? [Y/N]")
        continue
    print()
