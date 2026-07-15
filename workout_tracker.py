#!/usr/bin/env python3
"""
🔥 Habit & Workout Streak Tracker CLI 🔥
========================================
A beautiful, file-based command line application to log habits/workouts,
track current/longest streaks, and view logs on a custom text-based calendar.
Uses standard JSON storage and ANSI colors for a premium CLI experience.
"""

import os
import sys
import json
import datetime
import calendar

# --- Configuration & Styling Constants ---
LOG_FILE = "workout_logs.json"

# ANSI Terminal Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
GRAY = "\033[90m"
RESET = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"

# Safe Symbol Table (falls back to ASCII if stdout encoding doesn't support Unicode)
SYMBOLS = {
    "fire": "🔥",
    "check": "✔",
    "star": "★",
    "cross": "❌",
    "warning": "⚠️",
    "arm": "💪",
    "bullet": "•",
}

try:
    # Attempt encoding check for each rich symbol
    encoding = sys.stdout.encoding or 'ascii'
    for sym in SYMBOLS.values():
        sym.encode(encoding)
except (UnicodeEncodeError, AttributeError):
    # Fallback to standard ASCII symbols if stdout encoding is limited (e.g. cp1252)
    SYMBOLS = {
        "fire": "[HOT]",
        "check": "v",
        "star": "*",
        "cross": "x",
        "warning": "[!]",
        "arm": "",
        "bullet": "-",
    }


# --- Data Management (File I/O) ---

def load_data() -> dict:
    """Load habits and logs from the JSON file. Creates default data if missing."""
    default_data = {
        "habits": {
            "Workout": "Gym, running, or home workout session",
            "Meditation": "10-15 minutes of mindfulness",
            "Reading": "Reading a book or educational articles"
        },
        "logs": []
    }
    
    if not os.path.exists(LOG_FILE):
        return default_data
        
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Ensure keys exist
            if "habits" not in data:
                data["habits"] = default_data["habits"]
            if "logs" not in data:
                data["logs"] = []
            return data
    except Exception as e:
        print(f"\n{RED}{SYMBOLS['warning']} Warning: Error reading {LOG_FILE} ({e}). Starting fresh.{RESET}")
        return default_data


def save_data(data: dict) -> None:
    """Save the state back to the JSON file."""
    try:
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"\n{RED}{SYMBOLS['cross']} Error saving data to {LOG_FILE}: {e}{RESET}")


# --- Business Logic & Calculations ---

def get_completed_dates(logs: list, habit: str) -> set:
    """Extract a set of datetime.date objects for completed days of a given habit."""
    completed = set()
    for log in logs:
        if log.get("habit") == habit and log.get("completed", False):
            try:
                date_obj = datetime.datetime.strptime(log["date"], "%Y-%m-%d").date()
                completed.add(date_obj)
            except ValueError:
                continue
    return completed


def calculate_streaks(logs: list, habit: str) -> tuple:
    """
    Calculate the current streak and longest streak for a given habit.
    
    A current streak is active if logged today OR logged yesterday (allowing the
    user to complete/log today's session later).
    """
    completed_dates = get_completed_dates(logs, habit)
    if not completed_dates:
        return 0, 0

    sorted_dates = sorted(list(completed_dates))
    
    # 1. Longest Streak Calculation
    longest_streak = 0
    current_temp = 0
    prev_date = None
    
    for d in sorted_dates:
        if prev_date is None:
            current_temp = 1
        elif (d - prev_date).days == 1:
            current_temp += 1
        elif (d - prev_date).days > 1:
            if current_temp > longest_streak:
                longest_streak = current_temp
            current_temp = 1
        prev_date = d
        
    if current_temp > longest_streak:
        longest_streak = current_temp
        
    # 2. Current Streak Calculation
    today = datetime.date.today()
    current_streak = 0
    
    if today in completed_dates:
        current_streak = 1
        check_date = today - datetime.timedelta(days=1)
        while check_date in completed_dates:
            current_streak += 1
            check_date -= datetime.timedelta(days=1)
    elif (today - datetime.timedelta(days=1)) in completed_dates:
        current_streak = 1
        check_date = today - datetime.timedelta(days=2)
        while check_date in completed_dates:
            current_streak += 1
            check_date -= datetime.timedelta(days=1)
    else:
        current_streak = 0
        
    return current_streak, longest_streak


# --- Helper Functions ---

def parse_date_input(date_str: str) -> datetime.date:
    """Parse a date string (YYYY-MM-DD, 'today', 'yesterday', or empty)."""
    date_str = date_str.strip().lower()
    today = datetime.date.today()
    
    if date_str == "today" or date_str == "":
        return today
    elif date_str == "yesterday":
        return today - datetime.timedelta(days=1)
        
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD, 'today', or 'yesterday'.")


def select_habit(habits: dict) -> str:
    """Interactive prompt to select a habit from the existing habits list."""
    if not habits:
        print(f"\n{RED}{SYMBOLS['cross']} No habits available. Please create one first!{RESET}")
        return None
        
    print(f"\n{BOLD}Select a Habit:{RESET}")
    habit_keys = list(habits.keys())
    for idx, (h, desc) in enumerate(habits.items(), start=1):
        print(f"  {CYAN}{idx}. {h}{RESET} - {GRAY}{desc}{RESET}")
        
    while True:
        choice = input(f"\n{YELLOW}Choose a number (1-{len(habit_keys)}): {RESET}").strip()
        try:
            val = int(choice)
            if 1 <= val <= len(habit_keys):
                return habit_keys[val - 1]
            print(f"{RED}{SYMBOLS['cross']} Out of range. Enter a number between 1 and {len(habit_keys)}.{RESET}")
        except ValueError:
            print(f"{RED}{SYMBOLS['cross']} Invalid input. Please enter a valid number.{RESET}")


# --- CLI Views & Operations ---

def log_workout(data: dict) -> None:
    """Prompt the user to log progress for a habit."""
    print(f"\n{BOLD}{UNDERLINE}--- LOG HABIT/WORKOUT ---{RESET}")
    habit = select_habit(data["habits"])
    if not habit:
        return
        
    print(f"\nLog date:")
    print(f"  Press {GREEN}Enter{RESET} for today")
    print(f"  Type {CYAN}'yesterday'{RESET} for yesterday")
    print(f"  Or enter specific date as {YELLOW}YYYY-MM-DD{RESET}")
    
    date_input = input(f"{YELLOW}Date: {RESET}").strip()
    try:
        log_date = parse_date_input(date_input)
    except ValueError as e:
        print(f"\n{RED}{SYMBOLS['cross']} Error: {e}{RESET}")
        return
        
    date_str = log_date.strftime("%Y-%m-%d")
    
    # Check if a log already exists for this habit and date
    duplicate = next((l for l in data["logs"] if l["habit"] == habit and l["date"] == date_str), None)
    if duplicate:
        print(f"\n{YELLOW}{SYMBOLS['warning']} A log already exists for {habit} on {date_str}:{RESET}")
        print(f"  Completed: {GREEN if duplicate['completed'] else RED}{duplicate['completed']}{RESET} | Notes: {duplicate.get('notes', '')}")
        overwrite = input(f"{YELLOW}Overwrite this log? (y/n, default: n): {RESET}").strip().lower()
        if overwrite not in ['y', 'yes']:
            print("Log operation cancelled.")
            return
            
    completed_input = input(f"{YELLOW}Did you complete it? (y/n, default: y): {RESET}").strip().lower()
    completed = completed_input not in ['n', 'no']
    
    notes = input(f"{YELLOW}Optional notes/workout detail: {RESET}").strip()
    
    # If overwrite was approved, remove old duplicate in logs
    if duplicate:
        data["logs"] = [l for l in data["logs"] if not (l["habit"] == habit and l["date"] == date_str)]
        
    data["logs"].append({
        "date": date_str,
        "habit": habit,
        "completed": completed,
        "notes": notes
    })
    
    save_data(data)
    print(f"\n{GREEN}{SYMBOLS['check']} Habit logged successfully for {date_str}!{RESET}")
    
    # Calculate and show current streak updates
    curr, longest = calculate_streaks(data["logs"], habit)
    print(f"{SYMBOLS['fire']} Current streak for {habit}: {GREEN}{BOLD}{curr} days{RESET} (Longest: {YELLOW}{longest} days{RESET})")


def view_logs(data: dict) -> None:
    """Display logs in a readable, formatted text layout."""
    print(f"\n{BOLD}{UNDERLINE}--- HABIT LOG HISTORY ---{RESET}")
    if not data["logs"]:
        print(f"{GRAY}No logs recorded yet. Start logging some workouts!{RESET}")
        return
        
    # Sort logs descending by date
    sorted_logs = sorted(data["logs"], key=lambda x: (x["date"], x["habit"]), reverse=True)
    
    print(f"\n{BOLD}{'Date':<12} | {'Habit':<15} | {'Completed':<10} | {'Notes'}{RESET}")
    print("-" * 70)
    for log in sorted_logs:
        status_color = GREEN if log["completed"] else RED
        status_text = f"Yes {SYMBOLS['check']}" if log["completed"] else f"No {SYMBOLS['cross']}"
        notes = log.get("notes", "")
        print(f"{log['date']:<12} | {log['habit']:<15} | {status_color}{status_text:<10}{RESET} | {notes}")
    print("-" * 70)


def view_streaks(data: dict) -> None:
    """Show streak data for all habits."""
    print(f"\n{BOLD}{UNDERLINE}--- STREAK DASHBOARD ---{RESET}")
    if not data["habits"]:
        print(f"{GRAY}No habits created yet.{RESET}")
        return
        
    print(f"\n{BOLD}{'Habit':<18} | {'Current Streak':<16} | {'Longest Streak'}{RESET}")
    print("-" * 55)
    for habit in data["habits"]:
        curr, longest = calculate_streaks(data["logs"], habit)
        curr_text = f"{GREEN}{curr} days{RESET}" if curr > 0 else f"{RED}0 days{RESET}"
        long_text = f"{YELLOW}{longest} days{RESET}" if longest > 0 else f"{GRAY}0 days{RESET}"
        
        # Add flame icon if streak is active
        flame = f" {SYMBOLS['fire']}" if curr > 0 else ""
        
        print(f"{habit:<18} | {curr_text:<25} | {long_text}{flame}")
    print("-" * 55)


def show_calendar(data: dict) -> None:
    """Select a habit and show a text-based monthly calendar grid."""
    print(f"\n{BOLD}{UNDERLINE}--- TEXT CALENDAR VIEW ---{RESET}")
    habit = select_habit(data["habits"])
    if not habit:
        return
        
    today = datetime.date.today()
    print(f"\nEnter Month/Year:")
    print(f"  Press {GREEN}Enter{RESET} for current month ({today.strftime('%B %Y')})")
    print(f"  Or enter format {YELLOW}MM-YYYY{RESET} (e.g., 05-2026)")
    
    month_input = input(f"{YELLOW}Month/Year: {RESET}").strip()
    if not month_input:
        year = today.year
        month = today.month
    else:
        try:
            parts = month_input.split("-")
            if len(parts) != 2:
                raise ValueError
            month = int(parts[0])
            year = int(parts[1])
            if not (1 <= month <= 12):
                raise ValueError
        except ValueError:
            print(f"\n{RED}{SYMBOLS['cross']} Invalid format. Using current month instead.{RESET}")
            year = today.year
            month = today.month
            
    completed_days = get_completed_dates(data["logs"], habit)
    
    # Generate calendar weeks grid
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Print the Calendar Header
    print("\n" + "=" * 30)
    print(f"   {month_name} {year}".center(30))
    print("=" * 30)
    print("  Mo  Tu  We  Th  Fr  Sa  Su")
    print("-" * 30)
    
    for week in cal:
        week_str = ""
        for day in week:
            if day == 0:
                week_str += "    "
            else:
                is_today = (year == today.year and month == today.month and day == today.day)
                is_completed = datetime.date(year, month, day) in completed_days
                
                if is_today:
                    if is_completed:
                        # Completed today (Green bold, with star)
                        week_str += f"{GREEN}{BOLD} {day:2}{SYMBOLS['star']}{RESET}"
                    else:
                        # Not completed today yet (Blue bold, with star)
                        week_str += f"{BLUE}{BOLD} {day:2}{SYMBOLS['star']}{RESET}"
                else:
                    if is_completed:
                        # Completed other day (Green bold, with check)
                        week_str += f"{GREEN}{BOLD} {day:2}{SYMBOLS['check']}{RESET}"
                    else:
                        # Unlogged/Incomplete (Normal spacing)
                        week_str += f"  {day:2}"
        print(week_str)
        
    print("-" * 30)
    print(f"Legend: {GREEN}{SYMBOLS['check']}{RESET} = Completed | {BLUE}{SYMBOLS['star']}{RESET} = Today (Not Done) | {GREEN}{SYMBOLS['star']}{RESET} = Today (Done)")
    print("=" * 30 + "\n")


def remove_log(data: dict) -> None:
    """Allows user to select and delete an existing log entry."""
    print(f"\n{BOLD}{UNDERLINE}--- REMOVE A LOG ENTRY ---{RESET}")
    if not data["logs"]:
        print(f"{GRAY}No logs found to delete.{RESET}")
        return
        
    # Show last 15 logs for convenience
    sorted_logs = sorted(data["logs"], key=lambda x: (x["date"], x["habit"]), reverse=True)
    display_count = min(15, len(sorted_logs))
    
    print(f"\nShowing the latest {display_count} logs:")
    for idx in range(display_count):
        log = sorted_logs[idx]
        status = f"{GREEN}Completed{RESET}" if log["completed"] else f"{RED}Missed{RESET}"
        print(f"  {CYAN}{idx+1:<2}{RESET}. {log['date']} - {BOLD}{log['habit']}{RESET} ({status}) {GRAY}{log.get('notes', '')[:30]}{RESET}")
        
    print(f"  {CYAN}M   {RESET}. Select habit and enter custom date manually")
    print(f"  {CYAN}Q   {RESET}. Cancel and return to menu")
    
    choice = input(f"\n{YELLOW}Select log to delete (1-{display_count}, M, or Q): {RESET}").strip().upper()
    
    if choice == 'Q':
        print("Operation cancelled.")
        return
        
    target_log = None
    if choice == 'M':
        habit = select_habit(data["habits"])
        if not habit:
            return
        date_in = input(f"{YELLOW}Enter date to remove (YYYY-MM-DD): {RESET}").strip()
        try:
            parsed = datetime.datetime.strptime(date_in, "%Y-%m-%d").date()
            date_str = parsed.strftime("%Y-%m-%d")
        except ValueError:
            print(f"{RED}{SYMBOLS['cross']} Invalid date format. Operation cancelled.{RESET}")
            return
        
        target_log = next((l for l in data["logs"] if l["habit"] == habit and l["date"] == date_str), None)
        if not target_log:
            print(f"{RED}{SYMBOLS['cross']} No log found for {habit} on {date_str}.{RESET}")
            return
    else:
        try:
            val = int(choice)
            if 1 <= val <= display_count:
                target_log = sorted_logs[val - 1]
            else:
                print(f"{RED}{SYMBOLS['cross']} Invalid selection.{RESET}")
                return
        except ValueError:
            print(f"{RED}{SYMBOLS['cross']} Invalid selection.{RESET}")
            return
            
    # Confirm deletion
    confirm = input(f"{RED}{BOLD}{SYMBOLS['warning']} Are you sure you want to delete this log for {target_log['habit']} on {target_log['date']}? (y/n): {RESET}").strip().lower()
    if confirm in ['y', 'yes']:
        data["logs"].remove(target_log)
        save_data(data)
        print(f"\n{GREEN}{SYMBOLS['check']} Log entry deleted successfully!{RESET}")
    else:
        print("Deletion cancelled.")


def manage_habits(data: dict) -> None:
    """Add or remove custom habits to track."""
    while True:
        print(f"\n{BOLD}{UNDERLINE}--- HABITS MANAGEMENT ---{RESET}")
        print("1. List All Active Habits")
        print("2. Add New Habit")
        print("3. Delete Existing Habit")
        print("4. Back to Main Menu")
        
        choice = input(f"\n{YELLOW}Choose option (1-4): {RESET}").strip()
        
        if choice == '1':
            print(f"\n{BOLD}Currently Tracked Habits:{RESET}")
            for h, desc in data["habits"].items():
                print(f"  {SYMBOLS['bullet']} {CYAN}{h:<15}{RESET} - {desc}")
        elif choice == '2':
            new_name = input(f"\n{YELLOW}Enter habit name (e.g. Yoga, Hydration): {RESET}").strip()
            if not new_name:
                print(f"{RED}{SYMBOLS['cross']} Habit name cannot be empty.{RESET}")
                continue
            if new_name in data["habits"]:
                print(f"{RED}{SYMBOLS['cross']} Habit '{new_name}' already exists.{RESET}")
                continue
            desc = input(f"{YELLOW}Short description/goal: {RESET}").strip()
            
            data["habits"][new_name] = desc
            save_data(data)
            print(f"\n{GREEN}{SYMBOLS['check']} Habit '{new_name}' added successfully!{RESET}")
        elif choice == '3':
            print(f"\n{RED}{BOLD}{SYMBOLS['warning']} Note: Deleting a habit removes it from the list, but existing logs will be kept unless manually deleted.{RESET}")
            habit_to_del = select_habit(data["habits"])
            if not habit_to_del:
                continue
            confirm = input(f"{RED}Are you sure you want to delete the habit '{habit_to_del}'? (y/n): {RESET}").strip().lower()
            if confirm in ['y', 'yes']:
                del data["habits"][habit_to_del]
                save_data(data)
                print(f"\n{GREEN}{SYMBOLS['check']} Habit '{habit_to_del}' removed!{RESET}")
        elif choice == '4':
            break
        else:
            print(f"{RED}{SYMBOLS['cross']} Invalid choice. Enter 1-4.{RESET}")


# --- Main Menu loop ---

def main() -> None:
    """Main execution loop for the CLI application."""
    data = load_data()
    
    print("\n" + "=" * 55)
    print(f"      {SYMBOLS['fire']}   WELCOME TO HABIT & WORKOUT TRACKER   {SYMBOLS['fire']}")
    print("=" * 55)
    
    while True:
        print(f"\n{BOLD}Main Menu:{RESET}")
        print(f"  {GREEN}1.{RESET} Log Progress for Today/Custom Date")
        print(f"  {GREEN}2.{RESET} View History Log Table")
        print(f"  {GREEN}3.{RESET} Check Streaks Dashboard")
        print(f"  {GREEN}4.{RESET} Render Calendar Grid")
        print(f"  {GREEN}5.{RESET} Delete a Log Entry")
        print(f"  {GREEN}6.{RESET} Manage Habits (Add/Remove)")
        print(f"  {RED}7. Exit{RESET}")
        
        choice = input(f"\n{YELLOW}Choose operation (1-7): {RESET}").strip()
        
        if choice == '1':
            log_workout(data)
        elif choice == '2':
            view_logs(data)
        elif choice == '3':
            view_streaks(data)
        elif choice == '4':
            show_calendar(data)
        elif choice == '5':
            remove_log(data)
        elif choice == '6':
            manage_habits(data)
        elif choice == '7':
            print(f"\n{GREEN}Goodbye! Keep pushing your limits! {SYMBOLS['arm']}{SYMBOLS['fire']}{RESET}\n")
            break
        else:
            print(f"{RED}{SYMBOLS['cross']} Invalid option! Please select a number between 1 and 7.{RESET}")


if __name__ == "__main__":
    main()
