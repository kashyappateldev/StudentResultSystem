"""Result calculation, ranking, CSV export, and report-card generation."""

import csv
from pathlib import Path
from storage import load_students

# Passing criteria: at least 23 marks out of 70 in each subject
PASSING_MARK = 23
SUBJECT_MAX_MARK = 70

REPORT_DIR = Path(__file__).resolve().parent / "reports"


def grade_for_percentage(percentage):
    if percentage >= 90:
        return "A+"
    if percentage >= 80:
        return "A"
    if percentage >= 70:
        return "B"
    if percentage >= 60:
        return "C"
    if percentage >= 50:
        return "D"
    return "F"


def build_result(student):
    subjects = student["subjects"]

    marks = [float(mark) for mark in subjects.values()]
    total = sum(marks)
    maximum = len(marks) * SUBJECT_MAX_MARK

    percentage = (total / maximum * 100) if maximum else 0.0

    passed = all(
        PASSING_MARK <= mark <= SUBJECT_MAX_MARK
        for mark in marks
    )

    return {
        "total": total,
        "maximum": maximum,
        "percentage": percentage,
        "grade": grade_for_percentage(percentage),
        "status": "PASS" if passed else "FAIL",
        "subject_results": {
            subject: {
                "marks": float(mark),
                "status": (
                    "PASS"
                    if PASSING_MARK <= float(mark) <= SUBJECT_MAX_MARK
                    else "FAIL"
                ),
            }
            for subject, mark in subjects.items()
        },
    }


def print_result(student):
    result = build_result(student)

    print("\n" + "=" * 58)
    print("                     RESULT REPORT")
    print("=" * 58)
    print(f"Student ID : {student['student_id']}")
    print(f"Name       : {student['name']}")
    print(f"Class      : {student['class_name']}")
    print("-" * 58)
    print(f"{'Subject':<30} {'Marks / 70':>12} {'Status':>10}")
    print("-" * 58)

    for subject, details in result["subject_results"].items():
        print(
            f"{subject[:29]:<30} "
            f"{details['marks']:>12.2f} "
            f"{details['status']:>10}"
        )

    print("-" * 58)
    print(f"Passing marks per subject: {PASSING_MARK}/{SUBJECT_MAX_MARK}")
    print(f"Total      : {result['total']:.2f} / {result['maximum']:.2f}")
    print(f"Percentage : {result['percentage']:.2f}%")
    print(f"Grade      : {result['grade']}")
    print(f"Final      : {result['status']}")
    print("=" * 58)


def ranked_students():
    students = load_students()

    return sorted(
        students,
        key=lambda student: (
            build_result(student)["status"] == "PASS",
            build_result(student)["percentage"],
            student["name"].casefold(),
        ),
        reverse=True,
    )


def class_statistics():
    students = load_students()

    if not students:
        return {
            "count": 0,
            "pass_count": 0,
            "fail_count": 0,
            "average_percentage": 0.0,
            "highest_percentage": 0.0,
            "lowest_percentage": 0.0,
        }

    results = [build_result(student) for student in students]
    percentages = [result["percentage"] for result in results]

    pass_count = sum(
        result["status"] == "PASS"
        for result in results
    )

    return {
        "count": len(students),
        "pass_count": pass_count,
        "fail_count": len(students) - pass_count,
        "average_percentage": sum(percentages) / len(percentages),
        "highest_percentage": max(percentages),
        "lowest_percentage": min(percentages),
    }


def export_results_csv(path=None):
    students = load_students()

    output = (
        Path(path)
        if path
        else REPORT_DIR / "student_results.csv"
    )

    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)

        writer.writerow([
            "Student ID",
            "Name",
            "Class",
            "Total",
            "Maximum",
            "Percentage",
            "Grade",
            "Status",
        ])

        for student in students:
            result = build_result(student)

            writer.writerow([
                student["student_id"],
                student["name"],
                student["class_name"],
                f"{result['total']:.2f}",
                f"{result['maximum']:.2f}",
                f"{result['percentage']:.2f}",
                result["grade"],
                result["status"],
            ])

    return output


def generate_report_card(student, path=None):
    result = build_result(student)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    safe_id = "".join(
        c for c in student["student_id"]
        if c.isalnum() or c in "-_"
    )

    output = (
        Path(path)
        if path
        else REPORT_DIR / f"report_{safe_id}.txt"
    )

    lines = [
        "=" * 58,
        "                 STUDENT REPORT CARD",
        "=" * 58,
        f"Student ID : {student['student_id']}",
        f"Name       : {student['name']}",
        f"Class      : {student['class_name']}",
        "-" * 58,
        f"{'Subject':<30} {'Marks / 70':>12} {'Status':>10}",
        "-" * 58,
    ]

    for subject, details in result["subject_results"].items():
        lines.append(
            f"{subject[:29]:<30} "
            f"{details['marks']:>12.2f} "
            f"{details['status']:>10}"
        )

    lines.extend([
        "-" * 58,
        f"Passing marks per subject: {PASSING_MARK}/{SUBJECT_MAX_MARK}",
        f"Total      : {result['total']:.2f} / {result['maximum']:.2f}",
        f"Percentage : {result['percentage']:.2f}%",
        f"Grade      : {result['grade']}",
        f"Final      : {result['status']}",
        "=" * 58,
    ])

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return output