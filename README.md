# Student Result Management System

A pure-Python, command-line mini project for managing student records and academic results. It uses only the Python standard library.

## Features

- Add, view, search, update, and delete student records
- Enter any number of subjects per student, with marks from 0 to 100
- Automatically calculate total, percentage, grade, and pass/fail
- Subject-wise passing requirement (35/100 by default)
- Rank students and view class statistics
- Export result summaries to CSV
- Generate text report cards
- Save records persistently in JSON
- Unit tests using `unittest`

## Requirements

- Python 3.9 or newer recommended
- No third-party packages

## Run the Admin Panel (Graphical Interface)

Run this from the project root folder:

```bash
python admin_panel.py
```

This opens a desktop dashboard to add, search, edit, and delete students; view results and class statistics; rank students; export CSV; and generate report cards. It uses Python's built-in Tkinter library. The original CLI remains available with `python main.py`.

## Run the application

1. Extract the ZIP file.
2. Open a terminal/command prompt in the `StudentResultSystem` folder.
3. Run:

   ```bash
   python main.py
   ```

   On some systems, use `python3 main.py` or `py main.py`.

## How to use

Choose an option from the menu. To add a student, enter an ID, name, class/semester, comma-separated subject names, and marks for each subject. Example subjects:

`Python, Mathematics, Database, English, Computer Networks`

Records are saved to `data/students.json`. CSV exports and report cards are saved in `reports/`.

## Grading scale

| Percentage | Grade |
|---|---|
| 90–100 | A+ |
| 80–89.99 | A |
| 70–79.99 | B |
| 60–69.99 | C |
| 50–59.99 | D |
| Below 50 | F |

A student must score at least 35 in every subject to pass. These are sample rules; adjust them to your institution's grading policy if required.

## Run tests

From the project root:

```bash
python -m unittest discover -s tests -v
```

## Module overview

- `admin_panel.py`: Tkinter graphical admin dashboard
- `main.py`: command-line menu and application flow
- `student.py`: student CRUD operations and validation
- `result.py`: result calculations, ranking, statistics, CSV export, report cards
- `storage.py`: JSON loading and saving
- `data/students.json`: persistent student records
- `tests/`: automated unit tests
- `reports/`: generated exports and report cards

## Data format

Each student is stored as a JSON object:

```json
{
  "student_id": "STU001",
  "name": "Rahul Patel",
  "class_name": "BCA Semester 2",
  "subjects": {
    "Python": 85,
    "Mathematics": 78,
    "Database": 92
  }
}
```

Results are calculated from subject marks whenever requested, so changes to marks cannot leave stored totals out of date.
