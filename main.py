"""Student Result Management System - application entry point."""
from student import (
    add_student, delete_student, get_student, list_students,
    update_student, find_student_by_id
)
from result import (
    build_result, class_statistics, ranked_students, print_result,
    export_results_csv, generate_report_card
)
from storage import load_students


def read_nonempty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")


def display_menu():
    print("\n" + "=" * 54)
    print("       STUDENT RESULT MANAGEMENT SYSTEM")
    print("=" * 54)
    print("1. Add student")
    print("2. View all students")
    print("3. Search student")
    print("4. Update student")
    print("5. Delete student")
    print("6. View student result")
    print("7. Rank students")
    print("8. Class statistics")
    print("9. Export results to CSV")
    print("10. Generate report card")
    print("0. Exit")
    print("-" * 54)


def show_all():
    students = list_students()
    if not students:
        print("No student records found.")
        return
    print(f"\n{'ID':<12} {'Name':<24} {'Class':<20}")
    print("-" * 58)
    for student in students:
        print(f"{student['student_id']:<12} {student['name'][:23]:<24} {student['class_name'][:19]:<20}")


def prompt_marks(subjects):
    marks = {}
    for subject in subjects:
        while True:
            raw = input(f"Marks for {subject} (0-100): ").strip()
            try:
                mark = float(raw)
                if not 0 <= mark <= 100:
                    print("Marks must be between 0 and 100.")
                    continue
                marks[subject] = mark
                break
            except ValueError:
                print("Enter a valid number.")
    return marks


def run():
    # Initialize/load once so missing data files are created.
    load_students()
    while True:
        display_menu()
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                student_id = read_nonempty("Student ID: ")
                name = read_nonempty("Student name: ")
                class_name = read_nonempty("Class / semester: ")
                raw_subjects = read_nonempty(
                    "Subjects separated by commas (Enter for defaults is not supported here): "
                )
                subjects = [s.strip() for s in raw_subjects.split(",") if s.strip()]
                if len(subjects) != len(set(s.casefold() for s in subjects)):
                    print("Subject names must be unique.")
                    continue
                marks = prompt_marks(subjects)
                add_student({
                    "student_id": student_id,
                    "name": name,
                    "class_name": class_name,
                    "subjects": marks,
                })
                print("Student added successfully.")
            elif choice == "2":
                show_all()
            elif choice == "3":
                student_id = read_nonempty("Enter student ID: ")
                student = find_student_by_id(student_id)
                if student:
                    print(f"\nID: {student['student_id']}\nName: {student['name']}\nClass: {student['class_name']}")
                    print_result(student)
                else:
                    print("Student not found.")
            elif choice == "4":
                student_id = read_nonempty("Student ID to update: ")
                student = find_student_by_id(student_id)
                if not student:
                    print("Student not found.")
                    continue
                print("Press Enter to keep the existing value.")
                name = input(f"Name [{student['name']}]: ").strip() or student["name"]
                class_name = input(f"Class [{student['class_name']}]: ").strip() or student["class_name"]
                print("Enter new marks for each existing subject.")
                marks = prompt_marks(list(student["subjects"].keys()))
                update_student(student_id, name=name, class_name=class_name, subjects=marks)
                print("Student updated successfully.")
            elif choice == "5":
                student_id = read_nonempty("Student ID to delete: ")
                student = find_student_by_id(student_id)
                if not student:
                    print("Student not found.")
                    continue
                confirm = input(f"Delete {student['name']} ({student_id})? Type YES to confirm: ")
                if confirm == "YES":
                    delete_student(student_id)
                    print("Student deleted.")
                else:
                    print("Deletion cancelled.")
            elif choice == "6":
                student_id = read_nonempty("Student ID: ")
                student = find_student_by_id(student_id)
                if student:
                    print_result(student)
                else:
                    print("Student not found.")
            elif choice == "7":
                ranked = ranked_students()
                if not ranked:
                    print("No student records found.")
                else:
                    print("\nCLASS RANKING")
                    print("-" * 72)
                    for rank, student in enumerate(ranked, start=1):
                        result = build_result(student)
                        print(f"{rank:>2}. {student['name']:<24} {student['student_id']:<12} "
                              f"{result['percentage']:>6.2f}%  {result['status']}")
            elif choice == "8":
                stats = class_statistics()
                if not stats["count"]:
                    print("No student records found.")
                else:
                    print("\nCLASS STATISTICS")
                    print(f"Students: {stats['count']}")
                    print(f"Pass: {stats['pass_count']} | Fail: {stats['fail_count']}")
                    print(f"Class average: {stats['average_percentage']:.2f}%")
                    print(f"Highest percentage: {stats['highest_percentage']:.2f}%")
                    print(f"Lowest percentage: {stats['lowest_percentage']:.2f}%")
            elif choice == "9":
                path = export_results_csv()
                print(f"CSV exported to: {path}")
            elif choice == "10":
                student_id = read_nonempty("Student ID: ")
                student = find_student_by_id(student_id)
                if not student:
                    print("Student not found.")
                    continue
                path = generate_report_card(student)
                print(f"Report card saved to: {path}")
                print_result(student)
            elif choice == "0":
                print("Thank you for using Student Result Management System.")
                break
            else:
                print("Invalid choice. Select one of the listed options.")
        except (ValueError, KeyError) as exc:
            print(f"Could not complete operation: {exc}")
        except OSError as exc:
            print(f"File operation failed: {exc}")


if __name__ == "__main__":
    run()
