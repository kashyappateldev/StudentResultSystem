"""JSON persistence helpers for student records."""
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
DATA_FILE = DATA_DIR / "students.json"


def load_students():
    """Load student records, creating an empty data file when needed."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        save_students([])
        return []
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{DATA_FILE} contains invalid JSON. Restore a valid backup or fix the file."
        ) from exc
    if not isinstance(data, list):
        raise ValueError("Student data must be a JSON list.")
    return data


def save_students(students):
    """Save records using a temporary file before replacing the main file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temp_file = DATA_FILE.with_suffix(".tmp")
    with temp_file.open("w", encoding="utf-8") as file:
        json.dump(students, file, indent=4, ensure_ascii=False)
    temp_file.replace(DATA_FILE)


def find_record(student_id):
    """Return a record matching an ID, or None."""
    target = student_id.strip().casefold()
    return next(
        (student for student in load_students()
         if student.get("student_id", "").strip().casefold() == target),
        None
    )
