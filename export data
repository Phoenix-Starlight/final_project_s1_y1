def export_report(students, courses, grades):
    while True:
        print("\n---Export Performance Report---")
        print("1. Export Student Report")
        print("2. Export Course Report")
        print("3. Return to Main Menu")
        choice = input("Select option (1/2/3): ")
        if choice == "1":
            export_student_report(students, courses, grades)
        elif choice == "2":
            export_course_report(students, courses, grades)
        elif choice == "3":
            print("Returning to Main Menu")
            break
        else:
            print("Invalid selection")

def export_student_report(students, courses, grades):
    student_id = input("Enter Student ID: ")
    if student_id not in students:
        print("Student not found, please enter again.")
        return
    student_grades = []
    for g in grades:
        if g["student_id"] == student_id:
            student_grades.append(g)
    if len(student_grades) == 0:
        print("No grades found for this student, please enter again.")
        return
    total = 0
    for g in student_grades:
        total += g["mark"]
    average = total / len(student_grades)
    filename = "Report_" + student_id + ".txt"
    f = open(filename, "w")
    f.write("======= Student Performance Report =======" + "\n")
    f.write("Student ID: " + student_id + "\n")
    f.write("Name      : " + students[student_id]["name"] + "\n")
    f.write("Email     : " + students[student_id]["email"] + "\n")
    f.write("\n------- Course & Grades -------\n")
    for g in student_grades:
        course_name = courses[g["course_id"]]
        f.write(f'{g["course_id"]} - {course_name}: {g["mark"]} ({g["grade"]})\n')
    f.write("Average Mark: " + str(round(average, 2)) + "\n")
    f.write("==========================================")
    print("Student report saved as " + filename)

def export_course_report(students, courses, grades):
    course_id = input("Enter Course ID: ")
    if course_id not in courses:
        print("Course not found, please enter again.")
        return
    course_grades = []
    for g in grades:
        if g["course_id"] == course_id:
            course_grades.append(g)
    if len(course_grades) == 0:
        print("No grades found for this course, please enter again.")
        return
    total = 0
    highest = course_grades[0]["mark"]
    lowest = course_grades[0]["mark"]
    for g in course_grades:
        total += g["mark"]
        if g["mark"] > highest:
            highest = g["mark"]
        if g["mark"] < lowest:
            lowest = g["mark"]
    average = total / len(course_grades)
    filename = "Report_" + course_id + ".txt"
    with open(filename, "w") as f:
    f.write("======= Course Summary Report =======" + "\n")
    f.write("Course ID  : " + course_id + "\n")
    f.write("Course Name: " + courses[course_id] + "\n")
    f.write("\n------- Student Results -------\n")
    for g in course_grades:
        student_name = students[g["student_id"]]["name"]
        f.write(f'{g["student_id"]} - {student_name}: {g["mark"]} ({g["grade"]})\n')
    f.write("\n------- Statistics -------\n")
    f.write("Average Mark: " + str(round(average, 2)) + "\n")
    f.write("Highest Mark: " + str(highest) + "\n")
    f.write("Lowest Mark: " + str(lowest) + "\n")
    f.write("=====================================")
    print("Report saved as " + filename)
