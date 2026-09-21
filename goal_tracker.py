"""A terminal-based daily goal tracker.

Run with: python goal_tracker.py
The tracker stores its data in goals.json in this same folder.
"""

import json
from datetime import date, timedelta
from pathlib import Path


DATA_FILE = Path(__file__).with_name("goals.json")
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DAY_PROMPT = "Mon Tue Wed Thu Fri Sat Sun"


def load_goals():
    """Return saved goals, or an empty list when no data file exists yet."""
    if not DATA_FILE.exists():
        return []
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        print("Could not read goals.json. Starting with an empty goal list.")
        return []


def save_goals(goals):
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(goals, file, indent=2)


def next_id(goals):
    return max((goal["id"] for goal in goals), default=0) + 1


def parse_days(answer):
    """Convert comma/space separated weekday names into weekday numbers."""
    aliases = {
        "mon": 0, "monday": 0, "tue": 1, "tues": 1, "tuesday": 1,
        "wed": 2, "wednesday": 2, "thu": 3, "thur": 3, "thurs": 3,
        "thursday": 3, "fri": 4, "friday": 4, "sat": 5, "saturday": 5,
        "sun": 6, "sunday": 6,
    }
    words = answer.lower().replace(",", " ").split()
    if not words:
        return None
    try:
        return sorted({aliases[word] for word in words})
    except KeyError:
        return None


def scheduled_label(goal):
    return ", ".join(DAY_NAMES[day] for day in goal["schedule"])


def find_goal(goals, goal_id):
    return next((goal for goal in goals if goal["id"] == goal_id), None)


def ask_goal_id(goals):
    try:
        goal_id = int(input("Goal number: ").strip())
    except ValueError:
        print("Please enter a number.")
        return None
    goal = find_goal(goals, goal_id)
    if not goal:
        print("That goal does not exist.")
    return goal


def add_goal(goals):
    title = input("Goal name: ").strip()
    if not title:
        print("A goal needs a name.")
        return
    print(f"Schedule days, separated by spaces or commas ({DAY_PROMPT})")
    while True:
        schedule = parse_days(input("Days: ").strip())
        if schedule is not None:
            break
        print("Use weekday names such as: Mon Wed Fri")
    goals.append({
        "id": next_id(goals),
        "title": title,
        "schedule": schedule,
        "completed_dates": [],
    })
    save_goals(goals)
    print(f'Added "{title}".')


def delete_goal(goals):
    list_goals(goals)
    if not goals:
        return
    goal = ask_goal_id(goals)
    if not goal:
        return
    confirmation = input(f'Delete "{goal["title"]}"? (y/n): ').strip().lower()
    if confirmation == "y":
        goals.remove(goal)
        save_goals(goals)
        print("Goal deleted.")
    else:
        print("Delete canceled.")


def list_goals(goals):
    print("\nALL GOALS")
    if not goals:
        print("No goals yet. Choose Add a goal to create one.")
        return
    for goal in goals:
        print(f'  {goal["id"]}. {goal["title"]}  [{scheduled_label(goal)}]')


def today_view(goals):
    today = date.today()
    today_string = today.isoformat()
    due = [goal for goal in goals if today.weekday() in goal["schedule"]]
    pending = [goal for goal in due if today_string not in goal["completed_dates"]]
    completed = [goal for goal in due if today_string in goal["completed_dates"]]

    print(f"\nTODAY — {today.strftime('%A, %B %d, %Y')}")
    print("To complete:")
    if pending:
        for goal in pending:
            print(f'  {goal["id"]}. {goal["title"]}')
    else:
        print("  Nothing left — great work!")
    print("Completed:")
    if completed:
        for goal in completed:
            print(f'  [x] {goal["id"]}. {goal["title"]}')
    else:
        print("  No goals completed yet.")


def show_remaining_on_menu(goals):
    """Show a compact reminder of goals that are still due today."""
    today = date.today()
    today_string = today.isoformat()
    remaining = [
        goal for goal in goals
        if today.weekday() in goal["schedule"]
        and today_string not in goal["completed_dates"]
    ]
    print(f"\nSTILL TO COMPLETE TODAY ({today.strftime('%a, %b %d')})")
    if remaining:
        for goal in remaining:
            print(f'  {goal["id"]}. {goal["title"]}')
    else:
        print("  Nothing remaining — all scheduled goals are complete!")


def mark_complete(goals):
    today = date.today()
    today_string = today.isoformat()
    today_view(goals)
    goal = ask_goal_id(goals)
    if not goal:
        return
    if today.weekday() not in goal["schedule"]:
        print("That goal is not scheduled for today.")
        return
    if today_string in goal["completed_dates"]:
        print("That goal is already marked complete today.")
        return
    goal["completed_dates"].append(today_string)
    save_goals(goals)
    print(f'Marked "{goal["title"]}" complete for today.')


def show_schedule(goals):
    print("\nGOAL SCHEDULE")
    if not goals:
        print("No goals yet.")
        return
    for day_number, day_name in enumerate(DAY_NAMES):
        scheduled = [goal["title"] for goal in goals if day_number in goal["schedule"]]
        print(f"{day_name}: {', '.join(scheduled) if scheduled else 'No goals scheduled'}")


def weekly_visualization(goals):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_dates = [week_start + timedelta(days=offset) for offset in range(7)]

    print(f"\nWEEKLY PROGRESS — {week_start:%b %d} to {week_dates[-1]:%b %d, %Y}")
    print("Legend: X completed, - scheduled but not completed, . not scheduled")
    print("Goal                       " + " ".join(DAY_NAMES))
    print("-" * 60)
    if not goals:
        print("No goals yet.")
        return
    for goal in goals:
        marks = []
        for day in week_dates:
            if day.weekday() not in goal["schedule"]:
                marks.append(".")
            elif day.isoformat() in goal["completed_dates"]:
                marks.append("X")
            else:
                marks.append("-")
        name = goal["title"][:25]
        print(f"{name:<27}" + " ".join(marks))

    completed = sum(
        1 for goal in goals for day in week_dates
        if day.weekday() in goal["schedule"] and day.isoformat() in goal["completed_dates"]
    )
    scheduled = sum(1 for goal in goals for day in week_dates if day.weekday() in goal["schedule"])
    print(f"\nCompleted this week: {completed}/{scheduled} scheduled goals")


def main():
    goals = load_goals()
    actions = {
        "1": add_goal,
        "2": delete_goal,
        "3": list_goals,
        "4": mark_complete,
        "5": show_schedule,
        "6": weekly_visualization,
    }
    while True:
        print("\n=== GOAL LOGGER ===")
        show_remaining_on_menu(goals)
        print("1. Add a goal\n2. Delete a goal\n3. Show all goals")
        print("4. Mark a goal complete today\n5. Show schedule")
        print("6. Visualize this week\n7. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "7":
            print("Your goals have been saved. Goodbye!")
            break
        action = actions.get(choice)
        if action:
            action(goals)
        else:
            print("Choose a number from 1 to 7.")


if __name__ == "__main__":
    main()
