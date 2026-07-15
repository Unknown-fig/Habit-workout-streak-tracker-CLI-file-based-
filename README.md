# 🔥 Habit & Workout Streak Tracker CLI

A beautiful, interactive, file-based command line application built in Python to help you log habits/workouts, track your streaks (current and longest), and view your progress on a custom monthly calendar.

---

## 🌟 Features

* **Interactive CLI Menu**: Navigation using colorized prompts and inputs (emojis, status signs).
* **Console Compatibility**: Automatic console encoding detection (safely falls back to ASCII icons if the terminal doesn't support full Unicode/UTF-8 symbols like `✔` and `★`).
* **Active Streak Calculator**: Dynamically tracks active streaks (consecutive days). The current streak remains active if logged today or yesterday, allowing you to log workouts at any time of day.
* **Text-Based Monthly Calendar**: Custom 4-character column monthly calendar grid rendering completion markers and coloring today's date (Green for completed, Blue for today, Gray for unlogged).
* **Logs & Habit CRUD**: Add new habits to track, log completions with custom notes, view complete history tables, and delete specific logs.

---

## 🚀 Installation & Usage

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Unknown-fig/Habit-workout-streak-tracker-CLI-file-based-.git
   cd Habit-workout-streak-tracker-CLI-file-based-
   ```

2. **Run the tracker**:
   ```bash
   python workout_tracker.py
   ```

No external dependencies are required—only Python 3.

---

## 📂 File Structure

* `workout_tracker.py`: Main executable containing all logic, interactive menus, streak formulas, and calendar layout rendering.
* `workout_logs.json`: Local JSON database where active habits and history logs are persisted.

---

## 🛠 Streak Calculation Rules

* **Current Streak**: Active if today has a completion log OR if yesterday has a completion log (to allow completing today's habit later in the day). If neither today nor yesterday is completed, the streak resets to 0.
* **Longest Streak**: The maximum number of consecutive completed days recorded in the database.
