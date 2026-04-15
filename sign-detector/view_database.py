#!/usr/bin/env python3
"""
Database Viewer for Sign Language Study System
View all tables and data in the SQLite database
"""

import sqlite3
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.environ.get('DATABASE_PATH', os.path.join(BASE_DIR, 'studysystem.db'))

def print_separator(title=""):
    print("\n" + "="*70)
    if title:
        print(f"  {title}")
        print("="*70)

def view_database():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print_separator("📊 SIGN LANGUAGE STUDY SYSTEM - DATABASE VIEWER")
    print(f"Database: {DATABASE}")
    print(f"Viewed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\nTables: {len(tables)} ({', '.join(tables)})")
    
    # View each table
    for table in tables:
        print_separator(f"TABLE: {table.upper()}")
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Get data
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        
        print(f"Columns: {', '.join(columns)}")
        print(f"Rows: {len(rows)}")
        
        if len(rows) == 0:
            print("\n  [No data in this table]")
        else:
            print()
            # Print header
            header = " | ".join([f"{col:15}" for col in columns])
            print("  " + header)
            print("  " + "-" * len(header))
            
            # Print rows
            for row in rows:
                row_data = " | ".join([f"{str(row[col])[:15]:15}" for col in columns])
                print("  " + row_data)
    
    # Summary statistics
    print_separator("📈 STATISTICS")
    
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM study_sessions")
    session_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM lessons")
    lesson_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM user_progress")
    progress_count = cursor.fetchone()[0]
    
    print(f"Total Users: {user_count}")
    print(f"Total Study Sessions: {session_count}")
    print(f"Total Lessons: {lesson_count}")
    print(f"Total Progress Records: {progress_count}")
    
    if user_count > 0:
        cursor.execute("SELECT username, email, created_at FROM users ORDER BY created_at DESC")
        print("\nRecent Users:")
        for row in cursor.fetchall():
            print(f"  - {row['username']} ({row['email']}) - joined {row['created_at']}")
    
    if session_count > 0:
        cursor.execute("""
            SELECT u.username, s.topic, s.duration, s.scheduled_time, s.completed 
            FROM study_sessions s 
            JOIN users u ON s.user_id = u.id 
            ORDER BY s.scheduled_time DESC 
            LIMIT 5
        """)
        print("\nRecent Study Sessions:")
        for row in cursor.fetchall():
            status = "✓ Completed" if row['completed'] else "⏳ Pending"
            print(f"  - {row['username']}: {row['topic']} ({row['duration']}min) - {status}")
    
    print_separator()
    conn.close()

if __name__ == "__main__":
    view_database()
