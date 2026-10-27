"""Student CRUD operations and input validation."""
from storage import load_students, save_students


def _validate_student(student):
    required = ("student_id", "name", "class_name", "subjects")
    for key in required:
        if key not in student:
            raise ValueError(f"Missing required field: {key}")
    for key in ("student_id", "name", "class_name"):
        if not isinstance(student[key], str) or not student[key].strip():
            raise ValueError(f"{key.replace('_', ' ').title()} cannot be empty.")
    subjects = student["subjects"]
    if not isinstance(subjects, dict) or not subjects:
        raise ValueError("At least one subject and its marks are required.")
    seen = set()
    clean_subjects = {}
    for subject, mark in subjects.items():
        if not isinstance(subject, str) or not subject.strip():
            raise ValueError("Subject names cannot be empty.")
        key = subject.strip().casefold()
        if key in seen:
            raise ValueError("Subject names must be unique.")
        seen.add(key)
        try:
            numeric_mark = float(mark)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Marks for {subject} must be numeric.") from exc
        if not 0 <= numeric_mark <= 100:
            raise ValueError(f"Marks for {subject} must be between 0 and 100.")
        clean_subjects[subject.strip()] = numeric_mark
    return {
        "student_id": student["student_id"].strip(),
        "name": student["name"].strip(),
        "class_name": student["class_name"].strip(),
        "subjects": clean_subjects,
    }


def add_student(student):
    student = _validate_student(student)
    students = load_students()
    if any(s["student_id"].casefold() == student["student_id"].casefold() for s in students):
        raise ValueError(f"Student ID {student['student_id']} already exists.")
    students.append(student)
    save_students(students)
    return student


def list_students():
    return load_students()


def find_student_by_id(student_id):
    target = student_id.strip().casefold()
    return next((s for s in load_students()
                 if s["student_id"].casefold() == target), None)


def get_student(student_id):
    student = find_student_by_id(student_id)
    if student is None:
        raise ValueError(f"Student {student_id} was not found.")
    return student


def update_student(student_id, **changes):
    students = load_students()
    target = student_id.strip().casefold()
    for index, current in enumerate(students):
        if current["student_id"].casefold() == target:
            updated = dict(current)
            updated.update({k: v for k, v in changes.items() if v is not None})
            updated = _validate_student(updated)
            if updated["student_id"].casefold() != target and any(
                s["student_id"].casefold() == updated["student_id"].casefold()
                for s in students
            ):
                raise ValueError(f"Student ID {updated['student_id']} already exists.")
            students[index] = updated
            save_students(students)
            return updated
    raise ValueError(f"Student {student_id} was not found.")


def delete_student(student_id):
    students = load_students()
    target = student_id.strip().casefold()
    remaining = [s for s in students if s["student_id"].casefold() != target]
    if len(remaining) == len(students):
        raise ValueError(f"Student {student_id} was not found.")
    save_students(remaining)
    return True
