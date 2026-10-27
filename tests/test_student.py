import tempfile
import unittest
from pathlib import Path
import storage
import student


class StudentTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_data_file = storage.DATA_FILE
        self.old_data_dir = storage.DATA_DIR
        storage.DATA_DIR = Path(self.temp_dir.name)
        storage.DATA_FILE = storage.DATA_DIR / "students.json"
        storage.save_students([])

    def tearDown(self):
        storage.DATA_FILE = self.old_data_file
        storage.DATA_DIR = self.old_data_dir
        self.temp_dir.cleanup()

    def sample(self, student_id="S1"):
        return {
            "student_id": student_id, "name": "Asha Patel",
            "class_name": "BCA Semester 2",
            "subjects": {"Python": 88, "Math": 76}
        }

    def test_add_and_find_student(self):
        student.add_student(self.sample())
        self.assertEqual(student.find_student_by_id("s1")["name"], "Asha Patel")

    def test_duplicate_id_is_rejected(self):
        student.add_student(self.sample())
        with self.assertRaises(ValueError):
            student.add_student(self.sample())

    def test_invalid_marks_are_rejected(self):
        data = self.sample()
        data["subjects"]["Python"] = 101
        with self.assertRaises(ValueError):
            student.add_student(data)

    def test_delete_student(self):
        student.add_student(self.sample())
        student.delete_student("S1")
        self.assertIsNone(student.find_student_by_id("S1"))


if __name__ == "__main__":
    unittest.main()
