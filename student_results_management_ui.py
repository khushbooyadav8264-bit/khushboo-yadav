import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

FILE_NAME = "students.json"


def load_students():
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_students():
    with open(FILE_NAME, "w") as file:
        json.dump(students, file, indent=4)


def calculate_result(marks):
    total = sum(marks)
    percentage = total / 3

    if min(marks) < 40:
        grade = "F"
        result = "Fail"
    else:
        result = "Pass"
        if percentage >= 90:
            grade = "A+"
        elif percentage >= 75:
            grade = "A"
        elif percentage >= 60:
            grade = "B"
        else:
            grade = "C"

    return total, percentage, grade, result


def clear_form():
    global editing_roll
    editing_roll = None
    roll_entry.config(state="normal")
    roll_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    python_entry.delete(0, tk.END)
    maths_entry.delete(0, tk.END)
    english_entry.delete(0, tk.END)
    results_table.selection_remove(results_table.selection())


def add_or_update_student():
    roll = roll_entry.get().strip()
    name = name_entry.get().strip()

    if not roll or not name:
        messagebox.showwarning("Missing Details", "Enter roll number and student name.")
        return

    try:
        marks = [
            int(python_entry.get()),
            int(maths_entry.get()),
            int(english_entry.get())
        ]
    except ValueError:
        messagebox.showerror("Invalid Marks", "Please enter whole numbers for all marks.")
        return

    if any(mark < 0 or mark > 100 for mark in marks):
        messagebox.showerror("Invalid Marks", "Marks must be between 0 and 100.")
        return

    existing = next((s for s in students if s["roll"] == roll), None)
    if existing and editing_roll != roll:
        messagebox.showerror("Duplicate Roll Number", "This roll number already exists.")
        return

    total, percentage, grade, result = calculate_result(marks)
    student = {
        "roll": roll,
        "name": name,
        "python": marks[0],
        "maths": marks[1],
        "english": marks[2],
        "total": total,
        "percentage": round(percentage, 2),
        "grade": grade,
        "result": result
    }

    if existing:
        students[students.index(existing)] = student
    else:
        students.append(student)

    save_students()
    refresh_table()
    update_statistics()
    clear_form()
    messagebox.showinfo("Success", "Student result saved successfully.")


def refresh_table(records=None):
    for item in results_table.get_children():
        results_table.delete(item)

    for student in (students if records is None else records):
        results_table.insert("", tk.END, values=(
            student["roll"], student["name"], student["python"],
            student["maths"], student["english"], student["total"],
            f'{student["percentage"]:.2f}%', student["grade"], student["result"]
        ))


def select_student(event=None):
    global editing_roll
    selected = results_table.selection()
    if not selected:
        return

    values = results_table.item(selected[0], "values")
    editing_roll = values[0]
    roll_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    python_entry.delete(0, tk.END)
    maths_entry.delete(0, tk.END)
    english_entry.delete(0, tk.END)
    roll_entry.insert(0, values[0])
    name_entry.insert(0, values[1])
    python_entry.insert(0, values[2])
    maths_entry.insert(0, values[3])
    english_entry.insert(0, values[4])


def delete_student():
    roll = roll_entry.get().strip()
    if not roll:
        messagebox.showwarning("Select Student", "Select a student from the table first.")
        return

    student = next((s for s in students if s["roll"] == roll), None)
    if not student:
        messagebox.showerror("Not Found", "Student not found.")
        return

    if messagebox.askyesno("Confirm Delete", f'Delete result for {student["name"]}?'):
        students.remove(student)
        save_students()
        refresh_table()
        update_statistics()
        clear_form()


def search_student():
    roll = search_entry.get().strip()
    found = [s for s in students if s["roll"] == roll]

    if found:
        refresh_table(found)
        student = found[0]
        messagebox.showinfo(
            "Student Found",
            f'Name: {student["name"]}\n'
            f'Total: {student["total"]}/300\n'
            f'Percentage: {student["percentage"]:.2f}%\n'
            f'Grade: {student["grade"]}\n'
            f'Result: {student["result"]}'
        )
    else:
        messagebox.showinfo("Search Result", "No student found with this roll number.")
        refresh_table()


def show_all_students():
    refresh_table()
    search_entry.delete(0, tk.END)


def update_statistics():
    total = len(students)
    passed = sum(1 for s in students if s["result"] == "Pass")
    failed = total - passed
    average = sum(s["percentage"] for s in students) / total if total else 0

    total_label.config(text=f"Total Students: {total}")
    passed_label.config(text=f"Passed: {passed}")
    failed_label.config(text=f"Failed: {failed}")
    average_label.config(text=f"Average: {average:.2f}%")


students = load_students()
editing_roll = None

root = tk.Tk()
root.title("Student Results Management System")
root.geometry("1100x700")
root.minsize(900, 600)
root.configure(bg="#eef3f8")

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", rowheight=28, font=("Arial", 10))
style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
style.configure("TButton", font=("Arial", 10), padding=6)

header = tk.Label(
    root,
    text="Student Results Management System",
    font=("Arial", 22, "bold"),
    bg="#17365d",
    fg="white",
    pady=18
)
header.pack(fill="x")

form = ttk.LabelFrame(root, text="Student Details", padding=12)
form.pack(fill="x", padx=15, pady=12)

tk.Label(form, text="Roll Number:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
roll_entry = ttk.Entry(form, width=22)
roll_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(form, text="Student Name:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
name_entry = ttk.Entry(form, width=25)
name_entry.grid(row=0, column=3, padx=5, pady=5)

tk.Label(form, text="Python Marks:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
python_entry = ttk.Entry(form, width=22)
python_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(form, text="Maths Marks:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
maths_entry = ttk.Entry(form, width=25)
maths_entry.grid(row=1, column=3, padx=5, pady=5)

tk.Label(form, text="English Marks:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
english_entry = ttk.Entry(form, width=22)
english_entry.grid(row=2, column=1, padx=5, pady=5)

ttk.Button(form, text="Save Result", command=add_or_update_student).grid(
    row=2, column=2, padx=5, pady=5, sticky="ew"
)
ttk.Button(form, text="Clear Form", command=clear_form).grid(
    row=2, column=3, padx=5, pady=5, sticky="ew"
)
ttk.Button(form, text="Delete Selected", command=delete_student).grid(
    row=3, column=2, columnspan=2, padx=5, pady=5, sticky="ew"
)

search_frame = ttk.Frame(root, padding=(15, 0, 15, 8))
search_frame.pack(fill="x")
tk.Label(search_frame, text="Search by Roll Number:").pack(side="left", padx=(0, 8))
search_entry = ttk.Entry(search_frame, width=22)
search_entry.pack(side="left", padx=4)
ttk.Button(search_frame, text="Search", command=search_student).pack(side="left", padx=4)
ttk.Button(search_frame, text="Show All", command=show_all_students).pack(side="left", padx=4)

table_frame = ttk.LabelFrame(root, text="Student Results (select a row to edit)", padding=8)
table_frame.pack(fill="both", expand=True, padx=15, pady=5)

columns = ("roll", "name", "python", "maths", "english", "total", "percentage", "grade", "result")
results_table = ttk.Treeview(table_frame, columns=columns, show="headings")

headings = {
    "roll": "Roll No", "name": "Student Name", "python": "Python",
    "maths": "Maths", "english": "English", "total": "Total",
    "percentage": "Percentage", "grade": "Grade", "result": "Result"
}
widths = {
    "roll": 75, "name": 170, "python": 75, "maths": 75,
    "english": 80, "total": 75, "percentage": 95, "grade": 65, "result": 70
}

for column in columns:
    results_table.heading(column, text=headings[column])
    results_table.column(column, width=widths[column], anchor="center")

scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=results_table.yview)
results_table.configure(yscrollcommand=scrollbar.set)
results_table.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")
results_table.bind("<<TreeviewSelect>>", select_student)

stats_frame = ttk.LabelFrame(root, text="Class Statistics", padding=10)
stats_frame.pack(fill="x", padx=15, pady=10)

total_label = tk.Label(stats_frame, font=("Arial", 11, "bold"), bg="#eef3f8")
total_label.pack(side="left", expand=True)
passed_label = tk.Label(stats_frame, font=("Arial", 11, "bold"), fg="green", bg="#eef3f8")
passed_label.pack(side="left", expand=True)
failed_label = tk.Label(stats_frame, font=("Arial", 11, "bold"), fg="red", bg="#eef3f8")
failed_label.pack(side="left", expand=True)
average_label = tk.Label(stats_frame, font=("Arial", 11, "bold"), bg="#eef3f8")
average_label.pack(side="left", expand=True)

refresh_table()
update_statistics()

root.mainloop()
