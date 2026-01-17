#!/usr/bin/env python3
"""
CLI Task Manager - Personal productivity tool
Made by: Umar (17 years old from Egypt) 🇪🇬
Started this project when I was bored in summer vacation lol
"""

import argparse
import sqlite3
import json
import csv
import os
import sys
import threading
import time
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from colorama import init, Fore, Style
import configparser

# Initialize colorama for cross-platform colored output
init()

class TaskManager:
    def __init__(self, db_path="tasks.db"):
        self.db_path = db_path
        self.config = self.load_config()
        self.init_database()
        self.reminder_thread = None
        self.stop_reminders = False
        
    def load_config(self):
        """Load configuration from .taskrc file if it exists"""
        config = configparser.ConfigParser()
        config_path = os.path.expanduser("~/.taskrc")
        
        # Default config values - عشان مش كل حاجة تبقى manual
        defaults = {
            'default_priority': 'medium',
            'default_category': 'personal',
            'reminder_interval': '60'  # seconds
        }
        
        if os.path.exists(config_path):
            try:
                config.read(config_path)
                if 'DEFAULT' in config:
                    return dict(config['DEFAULT'])
            except Exception as e:
                print(f"{Fore.YELLOW}Warning: Could not read config file: {e}{Style.RESET_ALL}")
        
        return defaults
    
    def init_database(self):
        """Initialize SQLite database with tasks table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tasks table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                due_date TEXT,
                priority TEXT DEFAULT 'medium',
                category TEXT DEFAULT 'personal',
                status TEXT DEFAULT 'todo',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_task(self, description, due_date=None, priority=None, category=None):
        """Add a new task to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Use config defaults if not provided - عشان مبقاش أكتب كل مرة
        priority = priority or self.config.get('default_priority', 'medium')
        category = category or self.config.get('default_category', 'personal')
        
        # Parse due date if provided
        parsed_due = None
        if due_date:
            try:
                parsed_due = self.parse_natural_date(due_date)
            except Exception as e:
                print(f"{Fore.RED}Error parsing date '{due_date}': {e}{Style.RESET_ALL}")
                return False
        
        cursor.execute('''
            INSERT INTO tasks (description, due_date, priority, category)
            VALUES (?, ?, ?, ?)
        ''', (description, parsed_due, priority.lower(), category.lower()))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"{Fore.GREEN}✓ Task added with ID {task_id}{Style.RESET_ALL}")
        return True
    
    def parse_natural_date(self, date_str):
        """Parse natural language dates like 'tomorrow', 'next week', etc."""
        date_str = date_str.lower().strip()
        
        # Handle common natural language dates - الحاجات اللي بستخدمها كتير
        if date_str == 'today':
            return datetime.now().strftime('%Y-%m-%d')
        elif date_str == 'tomorrow':
            return (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        elif date_str == 'next week':
            return (datetime.now() + timedelta(weeks=1)).strftime('%Y-%m-%d')
        elif date_str == 'next month':
            return (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        else:
            # Try to parse with dateutil - it's pretty smart والله
            parsed = date_parser.parse(date_str)
            return parsed.strftime('%Y-%m-%d')
    
    def list_tasks(self, filter_by=None, sort_by='due_date'):
        """List tasks with optional filtering and sorting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Base query
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []
        
        # Add filters
        if filter_by:
            if filter_by.get('priority'):
                query += " AND priority = ?"
                params.append(filter_by['priority'].lower())
            if filter_by.get('category'):
                query += " AND category = ?"
                params.append(filter_by['category'].lower())
            if filter_by.get('status'):
                query += " AND status = ?"
                params.append(filter_by['status'].lower())
            if filter_by.get('overdue'):
                today = datetime.now().strftime('%Y-%m-%d')
                query += " AND due_date < ? AND status != 'done'"
                params.append(today)
        
        # Add sorting - مش أسرع query بس كفاية للمشروع ده
        if sort_by == 'priority':
            query += " ORDER BY CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 END"
        elif sort_by == 'due_date':
            query += " ORDER BY due_date ASC"
        else:
            query += " ORDER BY id DESC"
        
        cursor.execute(query, params)
        tasks = cursor.fetchall()
        conn.close()
        
        if not tasks:
            print(f"{Fore.YELLOW}No tasks found.{Style.RESET_ALL}")
            return
        
        # Display tasks with colors
        print(f"\n{Fore.CYAN}{'ID':<4} {'Description':<30} {'Due':<12} {'Priority':<8} {'Category':<12} {'Status':<10}{Style.RESET_ALL}")
        print("-" * 80)
        
        for task in tasks:
            task_id, desc, due, priority, category, status, created, updated = task
            
            # Color coding for priorities and status
            priority_color = Fore.RED if priority == 'high' else Fore.YELLOW if priority == 'medium' else Fore.GREEN
            status_color = Fore.GREEN if status == 'done' else Fore.BLUE if status == 'in-progress' else Fore.WHITE
            
            # Truncate long descriptions
            desc_short = desc[:28] + ".." if len(desc) > 30 else desc
            due_str = due or "No due date"
            
            print(f"{task_id:<4} {desc_short:<30} {due_str:<12} {priority_color}{priority:<8}{Style.RESET_ALL} {category:<12} {status_color}{status:<10}{Style.RESET_ALL}")
    
    def update_task(self, task_id, **kwargs):
        """Update task fields by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if task exists
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        if not cursor.fetchone():
            print(f"{Fore.RED}Task with ID {task_id} not found.{Style.RESET_ALL}")
            conn.close()
            return False
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        for field, value in kwargs.items():
            if field in ['description', 'priority', 'category', 'status']:
                update_fields.append(f"{field} = ?")
                params.append(value.lower() if field in ['priority', 'category', 'status'] else value)
            elif field == 'due_date':
                try:
                    parsed_date = self.parse_natural_date(value) if value else None
                    update_fields.append("due_date = ?")
                    params.append(parsed_date)
                except Exception as e:
                    print(f"{Fore.RED}Error parsing date: {e}{Style.RESET_ALL}")
                    conn.close()
                    return False
        
        if not update_fields:
            print(f"{Fore.YELLOW}No valid fields to update.{Style.RESET_ALL}")
            conn.close()
            return False
        
        # Add updated timestamp
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(task_id)
        
        query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        
        print(f"{Fore.GREEN}✓ Task {task_id} updated successfully.{Style.RESET_ALL}")
        return True
    
    def delete_task(self, task_id=None, delete_last=False):
        """Delete task by ID or delete the last added task"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if delete_last:
            cursor.execute("SELECT id FROM tasks ORDER BY id DESC LIMIT 1")
            result = cursor.fetchone()
            if result:
                task_id = result[0]
            else:
                print(f"{Fore.YELLOW}No tasks to delete.{Style.RESET_ALL}")
                conn.close()
                return False
        
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        if cursor.rowcount > 0:
            conn.commit()
            print(f"{Fore.GREEN}✓ Task {task_id} deleted.{Style.RESET_ALL}")
            result = True
        else:
            print(f"{Fore.RED}Task with ID {task_id} not found.{Style.RESET_ALL}")
            result = False
        
        conn.close()
        return result
    
    def search_tasks(self, keyword):
        """Search tasks by keyword in description"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM tasks WHERE description LIKE ? ORDER BY id DESC", 
                      (f"%{keyword}%",))
        tasks = cursor.fetchall()
        conn.close()
        
        if not tasks:
            print(f"{Fore.YELLOW}No tasks found containing '{keyword}'.{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}Found {len(tasks)} task(s) containing '{keyword}':{Style.RESET_ALL}")
        self._display_tasks_from_results(tasks)
    
    def _display_tasks_from_results(self, tasks):
        """Helper method to display tasks from query results"""
        print(f"\n{Fore.CYAN}{'ID':<4} {'Description':<30} {'Due':<12} {'Priority':<8} {'Category':<12} {'Status':<10}{Style.RESET_ALL}")
        print("-" * 80)
        
        for task in tasks:
            task_id, desc, due, priority, category, status, created, updated = task
            
            priority_color = Fore.RED if priority == 'high' else Fore.YELLOW if priority == 'medium' else Fore.GREEN
            status_color = Fore.GREEN if status == 'done' else Fore.BLUE if status == 'in-progress' else Fore.WHITE
            
            desc_short = desc[:28] + ".." if len(desc) > 30 else desc
            due_str = due or "No due date"
            
            print(f"{task_id:<4} {desc_short:<30} {due_str:<12} {priority_color}{priority:<8}{Style.RESET_ALL} {category:<12} {status_color}{status:<10}{Style.RESET_ALL}")
    
    def generate_report(self, period='all'):
        """Generate task completion reports"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get basic stats
        cursor.execute("SELECT COUNT(*) FROM tasks")
        total_tasks = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'done'")
        completed_tasks = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'todo'")
        pending_tasks = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'in-progress'")
        in_progress_tasks = cursor.fetchone()[0]
        
        # Calculate completion percentage
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        print(f"\n{Fore.CYAN}📊 Task Report ({period}){Style.RESET_ALL}")
        print("=" * 40)
        print(f"Total tasks: {total_tasks}")
        print(f"Completed: {Fore.GREEN}{completed_tasks}{Style.RESET_ALL}")
        print(f"In Progress: {Fore.BLUE}{in_progress_tasks}{Style.RESET_ALL}")
        print(f"Pending: {Fore.YELLOW}{pending_tasks}{Style.RESET_ALL}")
        print(f"Completion Rate: {Fore.GREEN}{completion_rate:.1f}%{Style.RESET_ALL}")
        
        # Get overdue tasks
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE due_date < ? AND status != 'done'", (today,))
        overdue_count = cursor.fetchone()[0]
        
        if overdue_count > 0:
            print(f"⚠️  Overdue tasks: {Fore.RED}{overdue_count}{Style.RESET_ALL}")
        
        conn.close()
    
    def export_tasks(self, format_type='json', filename=None):
        """Export tasks to JSON or CSV"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM tasks ORDER BY id")
        tasks = cursor.fetchall()
        conn.close()
        
        if not tasks:
            print(f"{Fore.YELLOW}No tasks to export.{Style.RESET_ALL}")
            return
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"tasks_export_{timestamp}.{format_type}"
        
        try:
            if format_type.lower() == 'json':
                # Convert to list of dicts for JSON
                task_list = []
                for task in tasks:
                    task_dict = {
                        'id': task[0],
                        'description': task[1],
                        'due_date': task[2],
                        'priority': task[3],
                        'category': task[4],
                        'status': task[5],
                        'created_at': task[6],
                        'updated_at': task[7]
                    }
                    task_list.append(task_dict)
                
                with open(filename, 'w') as f:
                    json.dump(task_list, f, indent=2)
                    
            elif format_type.lower() == 'csv':
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    # Write header
                    writer.writerow(['ID', 'Description', 'Due Date', 'Priority', 'Category', 'Status', 'Created', 'Updated'])
                    # Write tasks
                    writer.writerows(tasks)
            
            print(f"{Fore.GREEN}✓ Tasks exported to {filename}{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}Error exporting tasks: {e}{Style.RESET_ALL}")
    
    def import_tasks(self, filename):
        """Import tasks from JSON or CSV file"""
        if not os.path.exists(filename):
            print(f"{Fore.RED}File {filename} not found.{Style.RESET_ALL}")
            return
        
        try:
            if filename.endswith('.json'):
                with open(filename, 'r') as f:
                    tasks_data = json.load(f)
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                imported_count = 0
                for task in tasks_data:
                    cursor.execute('''
                        INSERT INTO tasks (description, due_date, priority, category, status)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        task.get('description', ''),
                        task.get('due_date'),
                        task.get('priority', 'medium'),
                        task.get('category', 'personal'),
                        task.get('status', 'todo')
                    ))
                    imported_count += 1
                
                conn.commit()
                conn.close()
                print(f"{Fore.GREEN}✓ Imported {imported_count} tasks from {filename}{Style.RESET_ALL}")
                
            elif filename.endswith('.csv'):
                # CSV import logic here - keeping it simple for now
                print(f"{Fore.YELLOW}CSV import not fully implemented yet. Use JSON for now.{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}Error importing tasks: {e}{Style.RESET_ALL}")
    
    def start_reminders(self):
        """Start background reminder thread - الreminders دي كانت صعبة في الأول بصراحة"""
        if self.reminder_thread and self.reminder_thread.is_alive():
            return
        
        self.stop_reminders = False
        self.reminder_thread = threading.Thread(target=self._reminder_loop, daemon=True)
        self.reminder_thread.start()
        print(f"{Fore.GREEN}✓ Reminder system started{Style.RESET_ALL}")
    
    def stop_reminder_system(self):
        """Stop the reminder system"""
        self.stop_reminders = True
        if self.reminder_thread:
            self.reminder_thread.join(timeout=1)
        print(f"{Fore.YELLOW}Reminder system stopped{Style.RESET_ALL}")
    
    def _reminder_loop(self):
        """Background loop to check for due tasks"""
        interval = int(self.config.get('reminder_interval', 60))
        
        while not self.stop_reminders:
            try:
                self._check_due_tasks()
                time.sleep(interval)
            except Exception as e:
                print(f"{Fore.RED}Reminder error: {e}{Style.RESET_ALL}")
                time.sleep(interval)
    
    def _check_due_tasks(self):
        """Check for tasks that are due today and show notifications"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT id, description, due_date FROM tasks 
            WHERE due_date = ? AND status != 'done'
        ''', (today,))
        
        due_tasks = cursor.fetchall()
        conn.close()
        
        if due_tasks:
            print(f"\n{Fore.YELLOW}🔔 يلا يا عم! عندك {len(due_tasks)} مهمة النهاردة!{Style.RESET_ALL}")
            for task_id, desc, due_date in due_tasks:
                print(f"  • [{task_id}] {desc}")
    
    def interactive_menu(self):
        """Interactive menu when no command line args provided"""
        print(f"\n{Fore.CYAN}📝 Umar's Task Manager{Style.RESET_ALL}")
        print("=" * 30)
        
        while True:
            print(f"\n{Fore.CYAN}إيه اللي عايز تعمله؟{Style.RESET_ALL}")
            print("1. Add task")
            print("2. List all tasks")
            print("3. List by priority/category")
            print("4. Update task")
            print("5. Delete task")
            print("6. Search tasks")
            print("7. Generate report")
            print("8. Export tasks")
            print("9. Start reminders")
            print("0. Exit")
            
            try:
                choice = input(f"\n{Fore.YELLOW}اختار رقم (0-9): {Style.RESET_ALL}").strip()
                
                if choice == '0':
                    print(f"{Fore.GREEN}يلا بقى! شوفك على خير 👋{Style.RESET_ALL}")
                    break
                elif choice == '1':
                    desc = input("Task description: ").strip()
                    due = input("Due date (optional, e.g., 'tomorrow', '2026-01-20'): ").strip() or None
                    priority = input("Priority (high/medium/low): ").strip() or None
                    category = input("Category (work/personal/etc.): ").strip() or None
                    self.add_task(desc, due, priority, category)
                elif choice == '2':
                    self.list_tasks()
                elif choice == '3':
                    filter_type = input("Filter by (priority/category/overdue): ").strip().lower()
                    if filter_type in ['priority', 'category']:
                        value = input(f"Enter {filter_type}: ").strip()
                        self.list_tasks(filter_by={filter_type: value})
                    elif filter_type == 'overdue':
                        self.list_tasks(filter_by={'overdue': True})
                elif choice == '4':
                    task_id = int(input("Task ID to update: "))
                    print("Leave blank to keep current value:")
                    desc = input("New description: ").strip()
                    status = input("New status (todo/in-progress/done): ").strip()
                    due = input("New due date: ").strip()
                    priority = input("New priority: ").strip()
                    
                    updates = {}
                    if desc: updates['description'] = desc
                    if status: updates['status'] = status
                    if due: updates['due_date'] = due
                    if priority: updates['priority'] = priority
                    
                    self.update_task(task_id, **updates)
                elif choice == '5':
                    task_id = input("Task ID to delete (or 'last' for last task): ").strip()
                    if task_id.lower() == 'last':
                        self.delete_task(delete_last=True)
                    else:
                        self.delete_task(int(task_id))
                elif choice == '6':
                    keyword = input("Search keyword: ").strip()
                    self.search_tasks(keyword)
                elif choice == '7':
                    self.generate_report()
                elif choice == '8':
                    format_type = input("Export format (json/csv): ").strip().lower()
                    filename = input("Filename (optional): ").strip() or None
                    self.export_tasks(format_type, filename)
                elif choice == '9':
                    self.start_reminders()
                    print("Reminders running in background. اضغط Ctrl+C عشان توقفها.")
                else:
                    print(f"{Fore.RED}رقم غلط يا برو. جرب تاني.{Style.RESET_ALL}")
                    
            except (ValueError, KeyboardInterrupt):
                print(f"\n{Fore.YELLOW}تم الإلغاء.{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")


def main():
    """Main function to handle command line arguments and interactive mode"""
    parser = argparse.ArgumentParser(description="Umar's CLI Task Manager - عشان أنظم حياتي شوية")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add task command
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('description', help='Task description')
    add_parser.add_argument('--due', help='Due date (e.g., tomorrow, 2026-01-20)')
    add_parser.add_argument('--priority', choices=['high', 'medium', 'low'], help='Task priority')
    add_parser.add_argument('--category', help='Task category (e.g., work, personal)')
    
    # List tasks command
    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('--priority', choices=['high', 'medium', 'low'], help='Filter by priority')
    list_parser.add_argument('--category', help='Filter by category')
    list_parser.add_argument('--status', choices=['todo', 'in-progress', 'done'], help='Filter by status')
    list_parser.add_argument('--overdue', action='store_true', help='Show only overdue tasks')
    list_parser.add_argument('--sort', choices=['due_date', 'priority', 'id'], default='due_date', help='Sort by field')
    
    # Update task command
    update_parser = subparsers.add_parser('update', help='Update a task')
    update_parser.add_argument('id', type=int, help='Task ID')
    update_parser.add_argument('--description', help='New description')
    update_parser.add_argument('--due', help='New due date')
    update_parser.add_argument('--priority', choices=['high', 'medium', 'low'], help='New priority')
    update_parser.add_argument('--category', help='New category')
    update_parser.add_argument('--status', choices=['todo', 'in-progress', 'done'], help='New status')
    
    # Delete task command
    delete_parser = subparsers.add_parser('delete', help='Delete a task')
    delete_parser.add_argument('id', nargs='?', help='Task ID (or use --last)')
    delete_parser.add_argument('--last', action='store_true', help='Delete the last added task')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search tasks')
    search_parser.add_argument('keyword', help='Keyword to search for')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate task report')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export tasks')
    export_parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Export format')
    export_parser.add_argument('--file', help='Output filename')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import tasks')
    import_parser.add_argument('file', help='File to import from')
    
    # Reminders command
    reminder_parser = subparsers.add_parser('reminders', help='Start reminder system')
    
    args = parser.parse_args()
    
    # Initialize task manager
    tm = TaskManager()
    
    try:
        if not args.command:
            # No command provided, start interactive mode
            tm.interactive_menu()
        elif args.command == 'add':
            tm.add_task(args.description, args.due, args.priority, args.category)
        elif args.command == 'list':
            filter_by = {}
            if args.priority: filter_by['priority'] = args.priority
            if args.category: filter_by['category'] = args.category
            if args.status: filter_by['status'] = args.status
            if args.overdue: filter_by['overdue'] = True
            
            tm.list_tasks(filter_by if filter_by else None, args.sort)
        elif args.command == 'update':
            updates = {}
            if args.description: updates['description'] = args.description
            if args.due: updates['due_date'] = args.due
            if args.priority: updates['priority'] = args.priority
            if args.category: updates['category'] = args.category
            if args.status: updates['status'] = args.status
            
            tm.update_task(args.id, **updates)
        elif args.command == 'delete':
            if args.last:
                tm.delete_task(delete_last=True)
            elif args.id:
                tm.delete_task(int(args.id))
            else:
                print(f"{Fore.RED}لازم تكتب الـ ID أو تستخدم --last{Style.RESET_ALL}")
        elif args.command == 'search':
            tm.search_tasks(args.keyword)
        elif args.command == 'report':
            tm.generate_report()
        elif args.command == 'export':
            tm.export_tasks(args.format, args.file)
        elif args.command == 'import':
            tm.import_tasks(args.file)
        elif args.command == 'reminders':
            tm.start_reminders()
            try:
                print("Reminder system running. اضغط Ctrl+C عشان توقف...")
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                tm.stop_reminder_system()
                
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}تم الإلغاء بواسطة المستخدم.{Style.RESET_ALL}")
        tm.stop_reminder_system()
    except Exception as e:
        print(f"{Fore.RED}حصل خطأ: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()