#!/usr/bin/env python3
"""
Database setup script for CLI Task Manager
Made by Umar - 17 years old from Egypt 🇪🇬
Run this if you want to initialize the database manually or add sample data
"""

import sqlite3
from datetime import datetime, timedelta

def setup_database(db_path="tasks.db"):
    """Initialize the database and optionally add sample data"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tasks table
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
    
    print("✓ Database table created successfully")
    
    # Ask if user wants sample data
    add_samples = input("عايز أضيف مهام تجريبية؟ (y/n): ").lower().strip()
    
    if add_samples == 'y':
        # Sample tasks for testing - مهام عادية زي اللي بعملها
        sample_tasks = [
            ("اشتري خضار للأسبوع", (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'), "high", "personal", "todo"),
            ("خلص مشروع البرمجة", (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'), "medium", "work", "in-progress"),
            ("اتصل بالدكتور عشان الموعد", (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'), "medium", "personal", "todo"),
            ("راجع الكود بتاع الفريق", datetime.now().strftime('%Y-%m-%d'), "high", "work", "todo"),
            ("خطط للرحلة الأسبوع الجاي", (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d'), "low", "personal", "todo"),
            ("حدث الـ CV", None, "low", "personal", "todo"),
            ("حضر العرض التقديمي", (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'), "high", "work", "todo"),
            ("اتعلم مكتبة Python جديدة", None, "medium", "learning", "todo"),
        ]
        
        for task in sample_tasks:
            cursor.execute('''
                INSERT INTO tasks (description, due_date, priority, category, status)
                VALUES (?, ?, ?, ?, ?)
            ''', task)
        
        print(f"✓ تم إضافة {len(sample_tasks)} مهمة تجريبية")
    
    conn.commit()
    conn.close()
    
    print(f"✓ Database setup complete: {db_path}")
    print("دلوقتي ممكن تشغل: python task_manager.py list")

if __name__ == "__main__":
    setup_database()