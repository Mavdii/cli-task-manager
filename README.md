# CLI Task Manager 📝

A practical command-line task manager built in Python for personal productivity. Made by **Umar**

Perfect for developers who live in the terminal and want a simple but powerful way to manage their daily tasks.

## Features

- ✅ **Add tasks** with natural language due dates ("tomorrow", "next week", "2026-01-20")
- 📋 **List and filter** tasks by priority, category, status, or overdue items
- ✏️ **Update tasks** - change description, status, due date, priority, category
- 🗑️ **Delete tasks** by ID or delete the last added task
- 🔍 **Search tasks** by keyword in description
- 📊 **Generate reports** - completion stats, overdue tasks, etc.
- 💾 **Export/Import** tasks to/from JSON or CSV
- ⏰ **Background reminders** - get notified about due tasks
- ⚙️ **Configuration** - set defaults via `.taskrc` file
- 🎨 **Colored output** - priorities and status are color-coded

## Installation

```bash
# Clone the repo
git clone https://github.com/Mavdii/cli-task-manager.git
cd cli-task-manager

# Install dependencies
pip install -r requirements.txt

# Make it executable (optional)
chmod +x task_manager.py
```

## Quick Start

```bash
# Add a task
python task_manager.py add "Buy groceries" --due tomorrow --priority high --category personal

# List all tasks
python task_manager.py list

# List high priority tasks
python task_manager.py list --priority high

# Update a task status
python task_manager.py update 1 --status done

# Search for tasks
python task_manager.py search "groceries"

# Generate a report
python task_manager.py report

# Start interactive mode (no arguments)
python task_manager.py
```

## Usage Examples

### Adding Tasks

```bash
# Basic task
python task_manager.py add "Finish the project documentation"

# Task with due date and priority
python task_manager.py add "Call dentist" --due "next week" --priority medium

# Work task with category
python task_manager.py add "Review pull requests" --due today --priority high --category work
```

### Listing Tasks

```bash
# All tasks
python task_manager.py list

# Filter by priority
python task_manager.py list --priority high

# Show overdue tasks only
python task_manager.py list --overdue

# Sort by priority instead of due date
python task_manager.py list --sort priority
```

### Updating Tasks

```bash
# Mark task as in progress
python task_manager.py update 5 --status in-progress

# Change due date and priority
python task_manager.py update 3 --due "2026-01-25" --priority low

# Update description
python task_manager.py update 2 --description "Updated task description"
```

### Other Operations

```bash
# Delete specific task
python task_manager.py delete 4

# Delete last added task
python task_manager.py delete --last

# Search tasks
python task_manager.py search "meeting"

# Export to JSON
python task_manager.py export --format json --file my_tasks.json

# Start reminder system (runs in background)
python task_manager.py reminders
```

## Configuration

Create a `.taskrc` file in your home directory to set defaults:

```ini
[DEFAULT]
default_priority = medium
default_category = personal
reminder_interval = 60
```

## Interactive Mode

Run without arguments to enter interactive mode:

```bash
python task_manager.py
```

This gives you a menu-driven interface - great for when you don't remember all the command options.

## Natural Language Dates

The task manager understands these date formats:
- `today`, `tomorrow`
- `next week`, `next month`
- Standard dates: `2026-01-20`, `Jan 20`, `January 20, 2026`
- Relative dates: `in 3 days`, `in 2 weeks`

## Database

Tasks are stored in a local SQLite database (`tasks.db`). The database is created automatically on first run.

## Task Status Options

- `todo` - Not started (default)
- `in-progress` - Currently working on it
- `done` - Completed

## Priority Levels

- `high` - Urgent/important (red)
- `medium` - Normal priority (yellow) 
- `low` - Nice to have (green)

## Export/Import

Export your tasks to JSON or CSV for backup or sharing:

```bash
# Export to JSON (recommended)
python task_manager.py export --format json

# Export to CSV
python task_manager.py export --format csv --file backup.csv

# Import from JSON
python task_manager.py import tasks_backup.json
```

## Background Reminders

Start the reminder system to get notifications about due tasks:

```bash
python task_manager.py reminders
```

The system checks every minute (configurable) and shows notifications for tasks due today.

## Screenshots

```
📝 Umar's Task Manager
======================

ID   Description                    Due          Priority Category     Status    
--------------------------------------------------------------------------------
1    Buy groceries                  2026-01-17   high     personal     todo      
2    Finish project docs            2026-01-20   medium   work         in-progress
3    Call dentist                   2026-01-24   medium   personal     todo      

📊 Task Report (all)
========================================
Total tasks: 15
Completed: 8
In Progress: 2
Pending: 5
Completion Rate: 53.3%
```

## About the Developer

Hi! I'm **Umar**, a 17-year-old developer from Egypt 🇪🇬. I built this task manager during my summer vacation because I was getting tired of forgetting my daily tasks and wanted to practice Python. 

This is one of my first "real" projects that I actually use daily. It started simple but I kept adding features whenever I got bored or needed something new.

## Contributing

This is a personal project, but feel free to fork it and make it your own! Some ideas for improvements:

- Add task dependencies  
- Email/SMS notifications
- Web interface
- Sync with external services
- Time tracking
- Recurring tasks
- Arabic language support (might add this later إن شاء الله)

## License

MIT License - do whatever you want with it!

---

**This CLI task manager is my go-to for daily stuff. It's solid but expandable — fork it and add your features! Made with ❤️ from Egypt 🇪🇬**