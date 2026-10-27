import unittest
from result import build_result, grade_for_percentage


class ResultTests(unittest.TestCase):
    def test_percentage_and_grade(self):
        student = {
            "student_id": "T1", "name": "Test", "class_name": "BCA",
            "subjects": {"Python": 90, "Math": 80}
        }
        result = build_result(student)
        self.assertEqual(result["total"], 170)
        self.assertEqual(result["maximum"], 200)
        self.assertEqual(result["percentage"], 85)
        self.assertEqual(result["grade"], "A")
        self.assertEqual(result["status"], "PASS")

    def test_fail_if_one_subject_below_pass_mark(self):
        student = {
            "student_id": "T2", "name": "Test", "class_name": "BCA",
            "subjects": {"Python": 90, "Math": 20}
        }
        self.assertEqual(build_result(student)["status"], "FAIL")

    def test_grade_boundaries(self):
        self.assertEqual(grade_for_percentage(90), "A+")
        self.assertEqual(grade_for_percentage(80), "A")
        self.assertEqual(grade_for_percentage(49.99), "F")


if __name__ == "__main__":
    unittest.main()
