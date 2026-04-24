#!/usr/bin/env python3
"""
Spanish Learning Tracker
Manage Spanish lessons (by count, not hours)
"""

import sqlite3
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

# Database path
DB_DIR = Path.home() / ".openclaw"
DB_PATH = DB_DIR / "spanish-learning.db"

def init_db():
    """Initialize the database with required tables"""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Lessons table - each lesson is 1 count
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            content TEXT,
            teacher TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Payments table - record lessons bought (not hours)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'CNY',
            lessons_bought INTEGER NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def get_now():
    """Get current UTC timestamp"""
    return datetime.now(timezone.utc).isoformat()

def get_today():
    """Get today's date in ISO format"""
    return datetime.now(timezone.utc).strftime('%Y-%m-%d')

def is_valid_date(date_str):
    """Check if string is a valid date (YYYY-MM-DD)"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def parse_lesson_args(args):
    """
    Parse lesson arguments. Format: [date] [content]
    Returns: (date, content)
    """
    if not args:
        return get_today(), ""
    
    # Check if first arg is a date
    if is_valid_date(args[0]):
        date = args[0]
        content = " ".join(args[1:]) if len(args) > 1 else ""
    else:
        date = get_today()
        content = " ".join(args)
    
    return date, content

def parse_payment_args(args):
    """
    Parse payment arguments. Format: [date] <amount> <lessons> [notes]
    Returns: (date, amount, lessons, notes)
    """
    if not args:
        return None, None, None, None
    
    # Check if first arg is a date
    if is_valid_date(args[0]):
        date = args[0]
        args = args[1:]
    else:
        date = get_today()
    
    if len(args) < 2:
        return None, None, None, None
    
    amount = float(args[0])
    lessons = int(args[1])
    notes = " ".join(args[2:]) if len(args) > 2 else ""
    
    return date, amount, lessons, notes

def add_lesson(content="", teacher="", date=None):
    """Add a new lesson record (1 lesson = 1 count)"""
    if date is None:
        date = get_today()
    
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO lessons (date, content, teacher, created_at)
        VALUES (?, ?, ?, ?)
    ''', (date, content, teacher, get_now()))
    
    lesson_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"✅ Lesson logged on {date}")
    if content:
        print(f"   Content: {content}")
    return lesson_id

def add_payment(amount, lessons_bought, currency="CNY", notes="", date=None):
    """Add a new payment record"""
    if date is None:
        date = get_today()
    
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO payments (date, amount, currency, lessons_bought, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (date, amount, currency, lessons_bought, notes, get_now()))
    
    payment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"✅ Payment recorded: {currency} {amount:.2f} for {lessons_bought} lessons on {date}")
    if notes:
        print(f"   Notes: {notes}")
    return payment_id

def list_lessons(limit=10):
    """List recent lessons"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, date, content, teacher
        FROM lessons
        ORDER BY date DESC, id DESC
        LIMIT ?
    ''', (limit,))
    
    lessons = cursor.fetchall()
    conn.close()
    
    if not lessons:
        print("No lessons recorded yet.")
        return
    
    print(f"\n📚 Recent Lessons (last {len(lessons)}) out of {get_total_lessons()} total:")
    print("-" * 60)
    for i, lesson in enumerate(lessons, 1):
        id_, date, content, teacher = lesson
        teacher_info = f" with {teacher}" if teacher else ""
        print(f"#{id_} | {date}{teacher_info}")
        if content:
            print(f"    {content}")
    print()

def list_payments(limit=10):
    """List recent payments"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, date, amount, currency, lessons_bought, notes
        FROM payments
        ORDER BY date DESC, id DESC
        LIMIT ?
    ''', (limit,))
    
    payments = cursor.fetchall()
    conn.close()
    
    if not payments:
        print("No payments recorded yet.")
        return
    
    total_lessons = sum(p[4] for p in payments)
    
    print(f"\n💰 Payment History (last {len(payments)}):")
    print(f"   Total purchased: {get_total_lessons_bought()} lessons")
    print("-" * 60)
    for payment in payments:
        id_, date, amount, currency, lessons, notes = payment
        print(f"#{id_} | {date} | {currency} {amount:.2f} | {lessons} lessons")
        if notes:
            print(f"    {notes}")
    print()

def get_total_lessons():
    """Get total lessons taken"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM lessons')
    count = cursor.fetchone()[0] or 0
    conn.close()
    return count

def get_total_lessons_bought():
    """Get total lessons purchased"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(lessons_bought) FROM payments')
    count = cursor.fetchone()[0] or 0
    conn.close()
    return count

def show_stats():
    """Show learning statistics"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Lesson stats
    total_lessons = get_total_lessons()
    
    # Payment stats
    cursor.execute('SELECT SUM(amount), SUM(lessons_bought) FROM payments')
    total_paid, total_lessons_bought = cursor.fetchone()
    total_paid = total_paid or 0
    total_lessons_bought = total_lessons_bought or 0
    
    # Calculate remaining lessons
    lessons_remaining = total_lessons_bought - total_lessons
    
    conn.close()
    
    print("\n📊 Spanish Learning Statistics")
    print("=" * 40)
    print(f"Lessons Completed: {total_lessons}")
    print(f"Lessons Purchased: {total_lessons_bought}")
    print(f"Lessons Remaining: {lessons_remaining}")
    print()
    print(f"Total Paid:        CNY {total_paid:.2f}")
    if total_lessons_bought > 0:
        cost_per_lesson = total_paid / total_lessons_bought
        print(f"Cost per Lesson:   CNY {cost_per_lesson:.2f}")
    print()
    
    if total_lessons_bought > 0:
        progress_pct = (total_lessons / total_lessons_bought) * 100
        print(f"Progress:          {progress_pct:.1f}% ({total_lessons}/{total_lessons_bought} lessons)")
    print()

def show_lesson(lesson_id):
    """Show specific lesson details"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, date, content, teacher, created_at
        FROM lessons WHERE id = ?
    ''', (lesson_id,))
    
    lesson = cursor.fetchone()
    conn.close()
    
    if not lesson:
        print(f"Lesson #{lesson_id} not found.")
        return
    
    id_, date, content, teacher, created = lesson
    print(f"\n📖 Lesson #{id_}")
    print("-" * 40)
    print(f"Date:     {date}")
    if teacher:
        print(f"Teacher:  {teacher}")
    if content:
        print(f"Content:  {content}")
    print()

def update_lesson(lesson_id, new_content):
    """Update lesson notes"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM lessons WHERE id = ?', (lesson_id,))
    if not cursor.fetchone():
        print(f"Lesson #{lesson_id} not found.")
        conn.close()
        return
    
    cursor.execute('''
        UPDATE lessons SET content = ? WHERE id = ?
    ''', (new_content, lesson_id))
    
    conn.commit()
    conn.close()
    print(f"✅ Lesson #{lesson_id} updated.")

def delete_lesson(lesson_id):
    """Delete a lesson record"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM lessons WHERE id = ?', (lesson_id,))
    
    if cursor.rowcount > 0:
        print(f"✅ Lesson #{lesson_id} deleted.")
    else:
        print(f"Lesson #{lesson_id} not found.")
    
    conn.commit()
    conn.close()

def delete_payment(payment_id):
    """Delete a payment record"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM payments WHERE id = ?', (payment_id,))
    
    if cursor.rowcount > 0:
        print(f"✅ Payment #{payment_id} deleted.")
    else:
        print(f"Payment #{payment_id} not found.")
    
    conn.commit()
    conn.close()

def main():
    if len(sys.argv) < 2:
        print("Usage: spanish.py <command> [args...]")
        print("\nCommands:")
        print("  lesson [date] [content]           - Log a lesson (date: YYYY-MM-DD)")
        print("  pay [date] <amount> <lessons> [notes]  - Record payment (date: YYYY-MM-DD)")
        print("  stats                             - Show statistics")
        print("  lessons [count]                   - List lessons")
        print("  payments [count]                  - List payments")
        print("  lesson-show <id>                  - Show lesson details")
        print("  lesson-update <id> <content>      - Update lesson")
        print("  lesson-delete <id>                - Delete lesson")
        print("  payment-delete <id>               - Delete payment")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "lesson":
        args = sys.argv[2:] if len(sys.argv) > 2 else []
        date, content = parse_lesson_args(args)
        add_lesson(content, date=date)
    
    elif command == "pay":
        if len(sys.argv) < 4:
            print("Usage: spanish.py pay [date] <amount> <lessons> [notes]")
            print("  date: optional, format YYYY-MM-DD, defaults to today")
            sys.exit(1)
        args = sys.argv[2:]
        date, amount, lessons, notes = parse_payment_args(args)
        if amount is None or lessons is None:
            print("Usage: spanish.py pay [date] <amount> <lessons> [notes]")
            sys.exit(1)
        add_payment(amount, lessons, notes=notes, date=date)
    
    elif command == "stats":
        show_stats()
    
    elif command == "lessons":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        list_lessons(limit)
    
    elif command == "payments":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        list_payments(limit)
    
    elif command == "lesson-show":
        if len(sys.argv) < 3:
            print("Usage: spanish.py lesson-show <id>")
            sys.exit(1)
        show_lesson(int(sys.argv[2]))
    
    elif command == "lesson-update":
        if len(sys.argv) < 4:
            print("Usage: spanish.py lesson-update <id> <content>")
            sys.exit(1)
        update_lesson(int(sys.argv[2]), " ".join(sys.argv[3:]))
    
    elif command == "lesson-delete":
        if len(sys.argv) < 3:
            print("Usage: spanish.py lesson-delete <id>")
            sys.exit(1)
        delete_lesson(int(sys.argv[2]))
    
    elif command == "payment-delete":
        if len(sys.argv) < 3:
            print("Usage: spanish.py payment-delete <id>")
            sys.exit(1)
        delete_payment(int(sys.argv[2]))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
