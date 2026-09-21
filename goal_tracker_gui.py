"""Graphical goal tracker built with Tkinter.

Run from this folder with: python goal_tracker_gui.py
This application shares goals.json with goal_tracker.py.
"""

import json
import tkinter as tk
from datetime import date, timedelta
from pathlib import Path
from tkinter import messagebox, ttk


DATA_FILE = Path(__file__).with_name("goals.json")
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def load_goals():
    if not DATA_FILE.exists():
        return []
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_goals(goals):
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(goals, file, indent=2)


class GoalTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.goals = load_goals()
        self.title("Goal Logger")
        self.minsize(780, 525)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        notebook = ttk.Notebook(self)
        notebook.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        self.today_tab = ttk.Frame(notebook, padding=16)
        self.goals_tab = ttk.Frame(notebook, padding=16)
        self.schedule_tab = ttk.Frame(notebook, padding=16)
        self.week_tab = ttk.Frame(notebook, padding=16)
        notebook.add(self.today_tab, text="Today")
        notebook.add(self.goals_tab, text="Goals")
        notebook.add(self.schedule_tab, text="Schedule")
        notebook.add(self.week_tab, text="Weekly Progress")

        self.build_today_tab()
        self.build_goals_tab()
        self.build_schedule_tab()
        self.build_week_tab()
        self.refresh_all()

    def build_today_tab(self):
        self.today_tab.columnconfigure(0, weight=1)
        ttk.Label(self.today_tab, text="Today's Goals", style="Title.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.today_date_label = ttk.Label(self.today_tab)
        self.today_date_label.grid(row=1, column=0, sticky="w", pady=(0, 12))

        ttk.Label(self.today_tab, text="Still to complete", style="Heading.TLabel").grid(
            row=2, column=0, sticky="w"
        )
        self.pending_list = tk.Listbox(self.today_tab, height=7, font=("Segoe UI", 11))
        self.pending_list.grid(row=3, column=0, sticky="nsew", pady=(4, 8))
        self.today_tab.rowconfigure(3, weight=1)
        ttk.Button(self.today_tab, text="Mark selected goal complete", command=self.mark_selected_complete).grid(
            row=4, column=0, sticky="w", pady=(0, 14)
        )

        ttk.Label(self.today_tab, text="Completed today", style="Heading.TLabel").grid(
            row=5, column=0, sticky="w"
        )
        self.completed_list = tk.Listbox(self.today_tab, height=6, font=("Segoe UI", 11))
        self.completed_list.grid(row=6, column=0, sticky="nsew", pady=(4, 0))
        self.today_tab.rowconfigure(6, weight=1)

    def build_goals_tab(self):
        self.goals_tab.columnconfigure(0, weight=1)
        self.goals_tab.rowconfigure(1, weight=1)
        ttk.Label(self.goals_tab, text="All Goals", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        self.goals_tree = ttk.Treeview(self.goals_tab, columns=("name", "schedule"), show="headings")
        self.goals_tree.heading("name", text="Goal")
        self.goals_tree.heading("schedule", text="Schedule")
        self.goals_tree.column("name", width=400)
        self.goals_tree.column("schedule", width=250)
        self.goals_tree.grid(row=1, column=0, sticky="nsew", pady=10)
        buttons = ttk.Frame(self.goals_tab)
        buttons.grid(row=2, column=0, sticky="w")
        ttk.Button(buttons, text="Add Goal", command=self.open_add_goal).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(buttons, text="Delete Selected Goal", command=self.delete_selected_goal).grid(row=0, column=1)

    def build_schedule_tab(self):
        self.schedule_tab.columnconfigure(0, weight=1)
        ttk.Label(self.schedule_tab, text="Weekly Schedule", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        self.schedule_frame = ttk.Frame(self.schedule_tab)
        self.schedule_frame.grid(row=1, column=0, sticky="nsew", pady=(15, 0))
        self.schedule_tab.rowconfigure(1, weight=1)

    def build_week_tab(self):
        self.week_tab.columnconfigure(0, weight=1)
        self.week_tab.rowconfigure(2, weight=1)
        self.week_title = ttk.Label(self.week_tab, style="Title.TLabel")
        self.week_title.grid(row=0, column=0, sticky="w")
        ttk.Label(self.week_tab, text="X = completed     – = scheduled but incomplete     · = not scheduled").grid(
            row=1, column=0, sticky="w", pady=(4, 12)
        )
        self.week_tree = ttk.Treeview(self.week_tab, columns=("goal", *DAY_NAMES), show="headings")
        self.week_tree.heading("goal", text="Goal")
        self.week_tree.column("goal", width=300, anchor="w")
        for day in DAY_NAMES:
            self.week_tree.heading(day, text=day)
            self.week_tree.column(day, width=55, anchor="center")
        self.week_tree.grid(row=2, column=0, sticky="nsew")
        self.week_summary = ttk.Label(self.week_tab)
        self.week_summary.grid(row=3, column=0, sticky="w", pady=(12, 0))

    def due_today(self):
        today = date.today()
        today_string = today.isoformat()
        due = [goal for goal in self.goals if today.weekday() in goal["schedule"]]
        pending = [goal for goal in due if today_string not in goal["completed_dates"]]
        completed = [goal for goal in due if today_string in goal["completed_dates"]]
        return pending, completed

    def refresh_all(self):
        self.refresh_today()
        self.refresh_goals()
        self.refresh_schedule()
        self.refresh_week()

    def refresh_today(self):
        today = date.today()
        pending, completed = self.due_today()
        self.today_date_label.config(text=today.strftime("%A, %B %d, %Y"))
        self.pending_list.delete(0, tk.END)
        self.completed_list.delete(0, tk.END)
        for goal in pending:
            self.pending_list.insert(tk.END, f'{goal["id"]}. {goal["title"]}')
        for goal in completed:
            self.completed_list.insert(tk.END, f'✓  {goal["title"]}')
        if not pending:
            self.pending_list.insert(tk.END, "Nothing remaining — great work!")
        if not completed:
            self.completed_list.insert(tk.END, "No goals completed yet.")

    def refresh_goals(self):
        self.goals_tree.delete(*self.goals_tree.get_children())
        for goal in self.goals:
            schedule = ", ".join(DAY_NAMES[day] for day in goal["schedule"])
            self.goals_tree.insert("", tk.END, iid=str(goal["id"]), values=(goal["title"], schedule))

    def refresh_schedule(self):
        for widget in self.schedule_frame.winfo_children():
            widget.destroy()
        for number, name in enumerate(DAY_NAMES):
            titles = [goal["title"] for goal in self.goals if number in goal["schedule"]]
            ttk.Label(self.schedule_frame, text=f"{name}:", width=8, style="Heading.TLabel").grid(
                row=number, column=0, sticky="nw", pady=5
            )
            ttk.Label(self.schedule_frame, text="\n".join(titles) if titles else "No goals scheduled").grid(
                row=number, column=1, sticky="nw", pady=5
            )

    def refresh_week(self):
        self.week_tree.delete(*self.week_tree.get_children())
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        week = [monday + timedelta(days=offset) for offset in range(7)]
        self.week_title.config(text=f"Weekly Progress: {monday:%b %d} – {week[-1]:%b %d, %Y}")
        completed_count = 0
        scheduled_count = 0
        for goal in self.goals:
            marks = []
            for current_day in week:
                if current_day.weekday() not in goal["schedule"]:
                    marks.append("·")
                elif current_day.isoformat() in goal["completed_dates"]:
                    marks.append("X")
                    completed_count += 1
                    scheduled_count += 1
                else:
                    marks.append("–")
                    scheduled_count += 1
            self.week_tree.insert("", tk.END, values=(goal["title"], *marks))
        self.week_summary.config(text=f"Completed this week: {completed_count}/{scheduled_count} scheduled goals")

    def mark_selected_complete(self):
        selection = self.pending_list.curselection()
        pending, _ = self.due_today()
        if not pending:
            messagebox.showinfo("No goals due", "There are no remaining goals scheduled for today.")
            return
        if not selection:
            messagebox.showwarning("Select a goal", "Select a goal from the 'Still to complete' list first.")
            return
        goal = pending[selection[0]]
        goal["completed_dates"].append(date.today().isoformat())
        save_goals(self.goals)
        self.refresh_all()

    def delete_selected_goal(self):
        selected = self.goals_tree.selection()
        if not selected:
            messagebox.showwarning("Select a goal", "Select a goal to delete first.")
            return
        goal_id = int(selected[0])
        goal = next(goal for goal in self.goals if goal["id"] == goal_id)
        if messagebox.askyesno("Delete goal", f'Delete "{goal["title"]}" and its completion history?'):
            self.goals.remove(goal)
            save_goals(self.goals)
            self.refresh_all()

    def open_add_goal(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add Goal")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        container = ttk.Frame(dialog, padding=18)
        container.grid()
        ttk.Label(container, text="Goal name:").grid(row=0, column=0, sticky="w")
        title_entry = ttk.Entry(container, width=35)
        title_entry.grid(row=1, column=0, sticky="ew", pady=(2, 12))
        ttk.Label(container, text="Repeat on:").grid(row=2, column=0, sticky="w")
        day_frame = ttk.Frame(container)
        day_frame.grid(row=3, column=0, sticky="w", pady=(4, 14))
        day_vars = []
        for index, day_name in enumerate(DAY_NAMES):
            variable = tk.BooleanVar(value=index < 5)
            ttk.Checkbutton(day_frame, text=day_name, variable=variable).grid(row=index // 4, column=index % 4, sticky="w", padx=(0, 10))
            day_vars.append(variable)

        def add():
            title = title_entry.get().strip()
            schedule = [index for index, variable in enumerate(day_vars) if variable.get()]
            if not title:
                messagebox.showwarning("Goal name needed", "Enter a name for the goal.", parent=dialog)
                return
            if not schedule:
                messagebox.showwarning("Schedule needed", "Choose at least one day.", parent=dialog)
                return
            new_id = max((goal["id"] for goal in self.goals), default=0) + 1
            self.goals.append({"id": new_id, "title": title, "schedule": schedule, "completed_dates": []})
            save_goals(self.goals)
            self.refresh_all()
            dialog.destroy()

        ttk.Button(container, text="Add Goal", command=add).grid(row=4, column=0, sticky="e")
        title_entry.focus_set()


if __name__ == "__main__":
    style_root = GoalTrackerApp()
    ttk.Style(style_root).configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
    ttk.Style(style_root).configure("Heading.TLabel", font=("Segoe UI", 11, "bold"))
    style_root.mainloop()
