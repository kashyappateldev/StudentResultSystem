"""Desktop admin dashboard for the Student Result Management System."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from student import (
    add_student, list_students, get_student, update_student, delete_student
)
from result import (
    build_result, class_statistics, ranked_students,
    export_results_csv, generate_report_card
)

BG = "#f3f6fb"
NAVY = "#172554"
BLUE = "#2563eb"


class StudentForm(tk.Toplevel):
    """Dialog for adding or editing a student with separate subject rows."""

    def __init__(self, parent, record=None):
        super().__init__(parent)
        self.title("Edit Student" if record else "Add Student")
        self.geometry("580x490")
        self.minsize(540, 450)
        self.configure(bg="white")
        self.transient(parent)
        self.grab_set()
        self.data = None

        frame = ttk.Frame(self, padding=18)
        frame.pack(fill="both", expand=True)
        self.vars = {}

        fields = [
            ("Student ID", "student_id"),
            ("Full Name", "name"),
            ("Class / Semester", "class_name"),
        ]

        for row, (label, key) in enumerate(fields):
            ttk.Label(frame, text=label).grid(
                row=row, column=0, sticky="w", pady=7, padx=(0, 12)
            )
            var = tk.StringVar(value=(record or {}).get(key, ""))
            self.vars[key] = var
            entry = ttk.Entry(frame, textvariable=var, width=35)
            entry.grid(row=row, column=1, sticky="ew", pady=7)
            if key == "student_id" and record:
                entry.configure(state="readonly")

        ttk.Separator(frame).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=12
        )
        ttk.Label(
            frame, text="Subject Marks", font=("Segoe UI", 12, "bold")
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(0, 8))

        subjects_frame = ttk.Frame(frame)
        subjects_frame.grid(
            row=5, column=0, columnspan=2, sticky="nsew"
        )
        frame.columnconfigure(1, weight=1)

        canvas = tk.Canvas(subjects_frame, height=140, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            subjects_frame, orient="vertical", command=canvas.yview
        )
        rows_frame = ttk.Frame(canvas)

        rows_frame.bind(
            "<Configure>",
            lambda _event: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas_id = canvas.create_window(
            (0, 0), window=rows_frame, anchor="nw"
        )
        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure(canvas_id, width=event.width)
        )
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Label(rows_frame, text="Subject Name").grid(
            row=0, column=0, padx=5, pady=5
        )
        ttk.Label(rows_frame, text="Marks (0–70)").grid(
            row=0, column=1, padx=5, pady=5
        )

        self.subject_rows = []

        def add_subject(subject="", marks=""):
            row_number = len(self.subject_rows) + 1
            name_var = tk.StringVar(value=subject)
            marks_var = tk.StringVar(value=str(marks))
            name_entry = ttk.Entry(
                rows_frame, textvariable=name_var, width=24
            )
            name_entry.grid(
                row=row_number, column=0, padx=5, pady=5
            )
            marks_entry = ttk.Entry(
                rows_frame, textvariable=marks_var, width=14
            )
            marks_entry.grid(
                row=row_number, column=1, padx=5, pady=5
            )
            self.subject_rows.append({
                "name": name_var,
                "marks": marks_var,
                "name_entry": name_entry,
                "marks_entry": marks_entry,
            })
            rows_frame.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

        existing_subjects = (record or {}).get("subjects", {})
        if existing_subjects:
            for subject, marks in existing_subjects.items():
                add_subject(subject, marks)
        else:
            for _ in range(3):
                add_subject()

        subject_buttons = ttk.Frame(frame)
        subject_buttons.grid(
            row=6, column=0, columnspan=2, sticky="w", pady=8
        )
        ttk.Button(
            subject_buttons, text="+ Add Subject", command=add_subject
        ).pack(side="left", padx=(0, 8))

        def remove_subject():
            if len(self.subject_rows) <= 1:
                messagebox.showwarning(
                    "Subject", "At least one subject is required.", parent=self
                )
                return
            row = self.subject_rows.pop()
            row["name_entry"].destroy()
            row["marks_entry"].destroy()
            rows_frame.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

        ttk.Button(
            subject_buttons, text="Remove Last", command=remove_subject
        ).pack(side="left")

        buttons = ttk.Frame(frame)
        buttons.grid(
            row=7, column=0, columnspan=2, sticky="e", pady=(10, 0)
        )
        ttk.Button(
            buttons, text="Cancel", command=self.destroy
        ).pack(side="left", padx=5)
        ttk.Button(
            buttons, text="Save Student", command=self.save
        ).pack(side="left")

    def save(self):
        try:
            data = {
                key: variable.get().strip()
                for key, variable in self.vars.items()
            }

            if not all(data.values()):
                raise ValueError(
                    "Please fill in Student ID, Full Name, and Class / Semester."
                )

            subjects = {}
            for row in self.subject_rows:
                name = row["name"].get().strip()
                marks_text = row["marks"].get().strip()

                if not name and not marks_text:
                    continue

                if not name or not marks_text:
                    raise ValueError(
                        "Enter both the subject name and marks for each used row."
                    )

                try:
                    marks = float(marks_text)
                except ValueError:
                    raise ValueError(
                        f"Marks for '{name}' must be a valid number."
                    )

                if not 0 <= marks <= 70:
                    raise ValueError(
                        f"Invalid marks for '{name}': {marks_text}. "
                        "Marks must be between 0 and 70."
                    )

                if any(
                    existing.casefold() == name.casefold()
                    for existing in subjects
                ):
                    raise ValueError(f"Duplicate subject: {name}")

                subjects[name] = marks

            if not subjects:
                raise ValueError("Please enter at least one subject.")

            data["subjects"] = subjects
            self.data = data
            self.destroy()

        except ValueError as error:
            messagebox.showerror(
                "Invalid Details", str(error), parent=self
            )


class AdminPanel(tk.Tk):
    """Main dashboard window."""

    def __init__(self):
        super().__init__()
        self.title("Student Result Management | Admin Panel")
        self.geometry("1150x700")
        self.minsize(900, 580)
        self.configure(bg=BG)

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Treeview", rowheight=30, font=("Segoe UI", 10),
            background="white", fieldbackground="white"
        )
        style.configure(
            "Treeview.Heading", font=("Segoe UI", 10, "bold"),
            padding=8, background="#e5eaf5"
        )
        style.configure("TButton", font=("Segoe UI", 10), padding=7)

        header = tk.Frame(self, bg=NAVY, height=68)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text="🎓  STUDENT RESULT MANAGEMENT",
            bg=NAVY, fg="white", font=("Segoe UI", 17, "bold")
        ).pack(side="left", padx=22)
        tk.Label(
            header, text="ADMIN DASHBOARD",
            bg=NAVY, fg="#bfdbfe", font=("Segoe UI", 10, "bold")
        ).pack(side="right", padx=22)

        content = tk.Frame(self, bg=BG)
        content.pack(fill="both", expand=True, padx=20, pady=16)

        top = tk.Frame(content, bg=BG)
        top.pack(fill="x", pady=(0, 14))
        tk.Label(
            top, text="Dashboard", bg=BG, fg=NAVY,
            font=("Segoe UI", 21, "bold")
        ).pack(side="left")
        ttk.Button(
            top, text="+ Add Student", command=self.add
        ).pack(side="right", padx=5)
        ttk.Button(
            top, text="Export CSV", command=self.export
        ).pack(side="right", padx=5)

        cards = tk.Frame(content, bg=BG)
        cards.pack(fill="x", pady=(0, 14))
        self.card = {}
        for key, label in [
            ("count", "TOTAL STUDENTS"),
            ("pass_count", "PASSED"),
            ("fail_count", "FAILED"),
            ("average_percentage", "CLASS AVERAGE"),
        ]:
            card = tk.Frame(
                cards, bg="white",
                highlightbackground="#dce3ef", highlightthickness=1
            )
            card.pack(side="left", fill="x", expand=True, padx=(0, 10))
            tk.Label(
                card, text=label, bg="white", fg="#64748b",
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w", padx=14, pady=(12, 3))
            self.card[key] = tk.Label(
                card, text="0", bg="white", fg=NAVY,
                font=("Segoe UI", 21, "bold")
            )
            self.card[key].pack(anchor="w", padx=14, pady=(0, 12))

        panel = tk.Frame(
            content, bg="white",
            highlightbackground="#dce3ef", highlightthickness=1
        )
        panel.pack(fill="both", expand=True)
        bar = tk.Frame(panel, bg="white")
        bar.pack(fill="x", padx=12, pady=12)
        tk.Label(
            bar, text="Student Records", bg="white", fg=NAVY,
            font=("Segoe UI", 13, "bold")
        ).pack(side="left")

        self.query = tk.StringVar()
        ttk.Entry(bar, textvariable=self.query, width=28).pack(
            side="right", padx=6
        )
        ttk.Button(
            bar, text="Refresh", command=self.refresh
        ).pack(side="right")

        columns = (
            "id", "name", "class", "total", "percentage", "grade", "status"
        )
        self.table = ttk.Treeview(
            panel, columns=columns, show="headings", selectmode="browse"
        )
        for col, title, width in [
            ("id", "STUDENT ID", 110),
            ("name", "STUDENT NAME", 190),
            ("class", "CLASS", 145),
            ("total", "TOTAL MARKS", 120),
            ("percentage", "PERCENTAGE", 115),
            ("grade", "GRADE", 75),
            ("status", "STATUS", 85),
        ]:
            self.table.heading(col, text=title)
            self.table.column(
                col, width=width,
                anchor="w" if col in ("id", "name", "class") else "center"
            )

        scroll = ttk.Scrollbar(
            panel, orient="vertical", command=self.table.yview
        )
        self.table.configure(yscrollcommand=scroll.set)
        self.table.pack(
            side="left", fill="both", expand=True, padx=(12, 0), pady=(0, 10)
        )
        scroll.pack(side="right", fill="y", padx=(0, 12), pady=(0, 10))
        self.table.bind("<Double-1>", lambda _event: self.view())

        actions = tk.Frame(content, bg=BG)
        actions.pack(fill="x", pady=(12, 0))
        for label, function in [
            ("View Result", self.view),
            ("Edit Student", self.edit),
            ("Delete Student", self.delete),
            ("Generate PDF Report", self.report),
            ("Rank Students", self.rank),
        ]:
            ttk.Button(
                actions, text=label, command=function
            ).pack(side="left", padx=(0, 7))

        self.status = tk.StringVar(value="Ready")
        tk.Label(
            self, textvariable=self.status, anchor="w",
            bg="#e5eaf5", fg="#475569", padx=12, pady=5
        ).pack(fill="x", side="bottom")

        self.query.trace_add("write", lambda *_: self.refresh())
        self.refresh()

    def refresh(self, *_):
        try:
            students = list_students()
            stats = class_statistics()
            for key in self.card:
                value = stats[key]
                self.card[key].config(
                    text=f"{value:.1f}%" if key == "average_percentage"
                    else str(value)
                )

            for item in self.table.get_children():
                self.table.delete(item)

            query = self.query.get().strip().casefold()
            for student in students:
                if query and not any(
                    query in str(student.get(key, "")).casefold()
                    for key in ("student_id", "name", "class_name")
                ):
                    continue

                result = build_result(student)
                self.table.insert(
                    "", "end",
                    values=(
                        student["student_id"],
                        student["name"],
                        student["class_name"],
                        f'{result["total"]:.1f}/{result["maximum"]:.0f}',
                        f'{result["percentage"]:.2f}%',
                        result["grade"],
                        result["status"],
                    ),
                    tags=(result["status"],),
                )

            self.table.tag_configure("PASS", foreground="#15803d")
            self.table.tag_configure("FAIL", foreground="#b91c1c")
            self.status.set(f"{len(students)} student record(s) loaded")
        except Exception as error:
            messagebox.showerror("Load Error", str(error), parent=self)

    def selected(self):
        selection = self.table.selection()
        if not selection:
            messagebox.showinfo(
                "Select Student",
                "Please select a student record first.",
                parent=self,
            )
            return None
        return str(self.table.item(selection[0], "values")[0])

    def add(self):
        dialog = StudentForm(self)
        self.wait_window(dialog)
        if dialog.data:
            try:
                add_student(dialog.data)
                self.refresh()
                messagebox.showinfo(
                    "Success", "Student added successfully.", parent=self
                )
            except Exception as error:
                messagebox.showerror(
                    "Could Not Add Student", str(error), parent=self
                )

    def edit(self):
        student_id = self.selected()
        if not student_id:
            return
        try:
            dialog = StudentForm(self, get_student(student_id))
            self.wait_window(dialog)
            if dialog.data:
                update_student(
                    student_id,
                    name=dialog.data["name"],
                    class_name=dialog.data["class_name"],
                    subjects=dialog.data["subjects"],
                )
                self.refresh()
                messagebox.showinfo(
                    "Success", "Student updated successfully.", parent=self
                )
        except Exception as error:
            messagebox.showerror(
                "Could Not Update Student", str(error), parent=self
            )

    def delete(self):
        student_id = self.selected()
        if student_id and messagebox.askyesno(
            "Confirm Deletion",
            f"Delete student {student_id}? This cannot be undone.",
            parent=self,
        ):
            try:
                delete_student(student_id)
                self.refresh()
            except Exception as error:
                messagebox.showerror("Delete Error", str(error), parent=self)

    def view(self):
        student_id = self.selected()
        if not student_id:
            return
        try:
            student = get_student(student_id)
            result = build_result(student)
            lines = [
                f'{student["name"]} ({student_id})',
                f'Class: {student["class_name"]}',
                "",
                "SUBJECT                 MARKS     STATUS",
                "-" * 42,
            ]
            for subject, details in result["subject_results"].items():
                lines.append(
                    f'{subject[:22]:22} {details["marks"]:7.2f} '
                    f'{details["status"]:>9}'
                )
            lines += [
                "-" * 42,
                f'Total: {result["total"]:.2f}/{result["maximum"]:.2f}',
                f'Percentage: {result["percentage"]:.2f}%',
                f'Grade: {result["grade"]}',
                f'Status: {result["status"]}',
            ]
            messagebox.showinfo(
                "Student Result", "\n".join(lines), parent=self
            )
        except Exception as error:
            messagebox.showerror("Result Error", str(error), parent=self)

    def report(self):
        """Generate a printable PDF report card for the selected student."""
        student_id = self.selected()
        if not student_id:
            return

        try:
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import (
                getSampleStyleSheet, ParagraphStyle
            )
            from reportlab.lib.units import mm
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            )
        except ImportError:
            messagebox.showerror(
                "PDF Library Missing",
                "Install the PDF library first:\n\npython -m pip install reportlab",
                parent=self,
            )
            return

        try:
            student = get_student(student_id)
            result = build_result(student)

            path = filedialog.asksaveasfilename(
                parent=self,
                title="Save Student Result as PDF",
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")],
                initialfile=f"Result_{student_id}.pdf",
            )
            if not path:
                return

            document = SimpleDocTemplate(
                path, pagesize=A4,
                rightMargin=18 * mm, leftMargin=18 * mm,
                topMargin=16 * mm, bottomMargin=18 * mm,
            )
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                "ReportTitle", parent=styles["Title"],
                fontName="Helvetica-Bold", fontSize=18, leading=23,
                textColor=colors.HexColor(NAVY), alignment=TA_CENTER,
                spaceAfter=5,
            )
            subtitle_style = ParagraphStyle(
                "ReportSubtitle", parent=styles["Normal"],
                fontSize=10, textColor=colors.HexColor("#64748b"),
                alignment=TA_CENTER, spaceAfter=18,
            )
            section_style = ParagraphStyle(
                "ReportSection", parent=styles["Heading2"],
                fontSize=12, textColor=colors.HexColor(NAVY),
                spaceBefore=12, spaceAfter=8,
            )

            story = [
                Paragraph("STUDENT RESULT MANAGEMENT SYSTEM", title_style),
                Paragraph("STUDENT ACADEMIC REPORT CARD", subtitle_style),
            ]

            student_info = [
                ["Student ID", str(student["student_id"]),
                 "Class / Semester", str(student["class_name"])],
                ["Student Name", str(student["name"]),
                 "Final Status", str(result["status"])],
            ]
            info_table = Table(
                student_info,
                colWidths=[27 * mm, 53 * mm, 33 * mm, 45 * mm],
            )
            info_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8eef8")),
                ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#e8eef8")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor(NAVY)),
                ("TEXTCOLOR", (2, 0), (2, -1), colors.HexColor(NAVY)),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.extend([
                info_table,
                Spacer(1, 12),
                Paragraph("Subject-wise Performance", section_style),
            ])

            marks_data = [[
                "No.", "Subject", "Maximum Marks", "Marks Obtained", "Status"
            ]]
            for index, (subject, details) in enumerate(
                result["subject_results"].items(), start=1
            ):
                marks_data.append([
                    str(index), str(subject), "70",
                    f'{details["marks"]:.2f}', str(details["status"]),
                ])

            marks_table = Table(
                marks_data,
                colWidths=[12 * mm, 53 * mm, 32 * mm, 32 * mm, 29 * mm],
                repeatRows=1,
            )
            marks_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(NAVY)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.white, colors.HexColor("#f1f5f9")]),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (2, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]))
            story.extend([
                marks_table,
                Spacer(1, 16),
                Paragraph("Final Result Summary", section_style),
            ])

            summary_table = Table(
                [
                    ["Total Marks", "Maximum Marks", "Percentage", "Grade"],
                    [
                        f'{result["total"]:.2f}',
                        f'{result["maximum"]:.2f}',
                        f'{result["percentage"]:.2f}%',
                        str(result["grade"]),
                    ],
                ],
                colWidths=[39 * mm, 39 * mm, 39 * mm, 39 * mm],
            )
            summary_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor(NAVY)),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]))
            story.extend([
                summary_table,
                Spacer(1, 15),
                Paragraph(
                    f'<b>Final Result:</b> {result["status"]}',
                    styles["Heading2"],
                ),
                Spacer(1, 28),
            ])

            signature_table = Table(
                [
                    ["________________________", "________________________"],
                    ["Class Teacher", "Authorized Signature"],
                ],
                colWidths=[82 * mm, 82 * mm],
            )
            signature_table.setStyle(TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#475569")),
            ]))
            story.append(signature_table)

            def add_page_number(canvas, doc):
                canvas.saveState()
                canvas.setFont("Helvetica", 8)
                canvas.setFillColor(colors.HexColor("#64748b"))
                canvas.drawCentredString(
                    A4[0] / 2, 10 * mm,
                    f"Student Result Report | Page {doc.page}",
                )
                canvas.restoreState()

            document.build(
                story,
                onFirstPage=add_page_number,
                onLaterPages=add_page_number,
            )
            self.status.set(f"PDF report saved: {path}")
            messagebox.showinfo(
                "PDF Generated",
                f"Student report card saved successfully:\n\n{path}",
                parent=self,
            )
        except Exception as error:
            messagebox.showerror(
                "PDF Generation Error", str(error), parent=self
            )

    def export(self):
        """Export the class results to a CSV file."""
        path = filedialog.asksaveasfilename(
            parent=self,
            title="Export Student Results",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile="student_results.csv",
        )
        if not path:
            return
        try:
            result_path = export_results_csv(path)
            messagebox.showinfo(
                "Export Complete",
                f"Results exported successfully:\n{result_path}",
                parent=self,
            )
        except Exception as error:
            messagebox.showerror("Export Error", str(error), parent=self)

    def rank(self):
        students = ranked_students()
        if not students:
            messagebox.showinfo(
                "Rank Students", "No student records available.", parent=self
            )
            return

        lines = ["CLASS RANKING", "-" * 55]
        for rank_number, student in enumerate(students, start=1):
            result = build_result(student)
            lines.append(
                f'{rank_number:>2}. {student["name"]} '
                f'({student["student_id"]}) — '
                f'{result["percentage"]:.2f}% | '
                f'{result["grade"]} | {result["status"]}'
            )

        window = tk.Toplevel(self)
        window.title("Student Rankings")
        window.geometry("720x440")
        text = tk.Text(
            window, font=("Consolas", 11), padx=15, pady=15
        )
        text.pack(fill="both", expand=True)
        text.insert("1.0", "\n".join(lines))
        text.configure(state="disabled")


if __name__ == "__main__":
    AdminPanel().mainloop()
