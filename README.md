# Goal Logger CLI

A Python command-line program for creating recurring goals, tracking daily completion, and viewing weekly progress.

## Instructions for Build and Use

Steps to build and/or run the software:

1. Open a terminal in the `HelloWorld` folder.
2. Run `python goal_tracker.py` for the terminal version, or `python goal_tracker_gui.py` for the Tkinter graphical version.
3. Follow the numbered menu prompts.

Instructions for using the software:

1. Add a goal and choose the weekdays it should be completed.
2. The main menu always displays goals that are still scheduled and incomplete today.
3. Use **Mark a goal complete today** when you finish a scheduled task; it also shows which goals you have already completed today.
4. Use **Show schedule** to see every goal organized by weekday.
5. Use **Visualize this week** for a weekly grid: `X` is completed, `-` is due but incomplete, and `.` is not scheduled.

Your goals and completion history are automatically stored in `goals.json` next to the program.

The graphical version has tabs for today's tasks, all goals, the weekly schedule, and a weekly completion grid. It uses Python's built-in Tkinter module, so it needs no third-party packages.

## Development Environment

To recreate the development environment, you need the following software and/or libraries with the specified versions:

* Python 3.8 or newer
* A terminal

## Useful Websites to Learn More

I found these websites useful in developing this software:

* [Python documentation](https://docs.python.org/3/)

## Future Work

The following items I plan to fix, improve, and/or add to this project in the future:

* [ ] Add optional due-time reminders
* [ ] Add goal editing
