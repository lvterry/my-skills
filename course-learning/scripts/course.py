#!/usr/bin/env python3
"""
Course Learning Tracker
Manage multiple courses: Spanish, Boxing, etc.
Track payments and lesson attendance by course type.
"""

import sqlite3
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

# Database path
DB_DIR = Path.home() / ".openclaw"
DB_PATH = DB_DIR / "course-learning.db"

# Supported course types
COURSE_TYPES = {
    'spanish': 'Spanish',
    'boxing': 'Boxing',
    'yoga': 'Yoga',
    'piano': 'Piano',
    'dance': 'Dance',
    'swimming': 'Swimming',
    'cooking': 'Cooking'
}

def init_db():
    """Initialize the database with required tables"""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Lessons table - each lesson is 1 count, with course type
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_type TEXT NOT NULL,
            date TEXT NOT NULL,
            content TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Payments table - record lessons bought by course type
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_type TEXT NOT NULL,
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

def validate_course(course_type):
    """Validate course type"""
    course_type = course_type.lower()
    if course_type not in COURSE_TYPES:
        print(f"Unknown course type: {course_type}")
        print(f"Supported: {', '.join(COURSE_TYPES.keys())}")
        return None
    return course_type

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

def add_lesson(course_type, content="", date=None):
    """Add a new lesson record"""
    if date is None:
        date = get_today()
    
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO lessons (course_type, date, content, created_at)
        VALUES (?, ?, ?, ?)
    ''', (course_type, date, content, get_now()))
    
    lesson_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    course_name = COURSE_TYPES.get(course_type, course_type.title())
    print(f"✅ {course_name} lesson logged on {date}")
    if content:
        print(f"   Content: {content}")
    return lesson_id

def add_payment(course_type, amount, lessons_bought, currency="CNY", notes="", date=None):
    """Add a new payment record"""
    if date is None:
        date = get_today()
    
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO payments (course_type, date, amount, currency, lessons_bought, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (course_type, date, amount, currency, lessons_bought, notes, get_now()))
    
    payment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    course_name = COURSE_TYPES.get(course_type, course_type.title())
    print(f"✅ {course_name} payment recorded: {currency} {amount:.2f} for {lessons_bought} lessons on {date}")
    if notes:
        print(f"   Notes: {notes}")
    return payment_id

def get_total_lessons(course_type=None):
    """Get total lessons taken"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if course_type:
        cursor.execute('SELECT COUNT(*) FROM lessons WHERE course_type = ?', (course_type,))
    else:
        cursor.execute('SELECT COUNT(*) FROM lessons')
    
    count = cursor.fetchone()[0] or 0
    conn.close()
    return count

def get_total_lessons_by_course():
    """Get lesson counts grouped by course"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT course_type, COUNT(*) as count 
        FROM lessons 
        GROUP BY course_type
        ORDER BY count DESC
    ''')
    
    results = cursor.fetchall()
    conn.close()
    return results

def get_total_lessons_bought(course_type=None):
    """Get total lessons purchased"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if course_type:
        cursor.execute('SELECT SUM(lessons_bought) FROM payments WHERE course_type = ?', (course_type,))
    else:
        cursor.execute('SELECT SUM(lessons_bought) FROM payments')
    
    count = cursor.fetchone()[0] or 0
    conn.close()
    return count

def get_total_paid(course_type=None):
    """Get total amount paid"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if course_type:
        cursor.execute('SELECT SUM(amount) FROM payments WHERE course_type = ?', (course_type,))
    else:
        cursor.execute('SELECT SUM(amount) FROM payments')
    
    amount = cursor.fetchone()[0] or 0
    conn.close()
    return amount

def list_lessons(course_type=None, limit=10):
    """List recent lessons"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if course_type:
        cursor.execute('''
            SELECT id, date, content, course_type
            FROM lessons
            WHERE course_type = ?
            ORDER BY date DESC, id DESC
            LIMIT ?
        ''', (course_type, limit))
    else:
        cursor.execute('''
            SELECT id, date, content, course_type
            FROM lessons
            ORDER BY date DESC, id DESC
            LIMIT ?
        ''', (limit,))
    
    lessons = cursor.fetchall()
    conn.close()
    
    if not lessons:
        print("No lessons recorded yet.")
        return
    
    title = f"Recent Lessons (last {len(lessons)})"
    if course_type:
        course_name = COURSE_TYPES.get(course_type, course_type.title())
        title += f" - {course_name}"
    
    print(f"\n📚 {title}:")
    print("-" * 60)
    for lesson in lessons:
        id_, date, content, course = lesson
        course_name = COURSE_TYPES.get(course, course.title())
        print(f"#{id_} | {date} | {course_name}")
        if content:
            print(f"    {content}")
    print()

def list_payments(course_type=None, limit=10):
    """List recent payments"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if course_type:
        cursor.execute('''
            SELECT id, date, amount, currency, lessons_bought, notes, course_type
            FROM payments
            WHERE course_type = ?
            ORDER BY date DESC, id DESC
            LIMIT ?
        ''', (course_type, limit))
    else:
        cursor.execute('''
            SELECT id, date, amount, currency, lessons_bought, notes, course_type
            FROM payments
            ORDER BY date DESC, id DESC
            LIMIT ?
        ''', (limit,))
    
    payments = cursor.fetchall()
    conn.close()
    
    if not payments:
        print("No payments recorded yet.")
        return
    
    title = "Payment History"
    if course_type:
        course_name = COURSE_TYPES.get(course_type, course_type.title())
        title += f" - {course_name}"
    
    print(f"\n💰 {title} (last {len(payments)}):")
    print("-" * 60)
    for payment in payments:
        id_, date, amount, currency, lessons, notes, course = payment
        course_name = COURSE_TYPES.get(course, course.title())
        print(f"#{id_} | {date} | {course_name} | {currency} {amount:.2f} | {lessons} lessons")
        if notes:
            print(f"    {notes}")
    print()

def show_stats(course_type=None):
    """Show learning statistics"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if course_type:
        # Single course stats
        total_lessons = get_total_lessons(course_type)
        total_paid = get_total_paid(course_type)
        total_lessons_bought = get_total_lessons_bought(course_type)
        lessons_remaining = total_lessons_bought - total_lessons
        
        course_name = COURSE_TYPES.get(course_type, course_type.title())
        
        print(f"\n📊 {course_name} Statistics")
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
    else:
        # All courses summary
        print("\n📊 All Courses Summary")
        print("=" * 40)
        
        # Get stats by course
        cursor.execute('''
            SELECT course_type, COUNT(*) as count 
            FROM lessons 
            GROUP BY course_type
        ''')
        lesson_counts = dict(cursor.fetchall())
        
        cursor.execute('''
            SELECT course_type, SUM(lessons_bought) as total, SUM(amount) as paid
            FROM payments 
            GROUP BY course_type
        ''')
        payment_stats = cursor.fetchall()
        
        if not payment_stats:
            print("No data recorded yet.")
            conn.close()
            return
        
        print()
        for course, bought, paid in payment_stats:
            course_name = COURSE_TYPES.get(course, course.title())
            completed = lesson_counts.get(course, 0)
            remaining = bought - completed
            progress = (completed / bought * 100) if bought > 0 else 0
            
            print(f"📌 {course_name}")
            print(f"   Completed: {completed} | Remaining: {remaining} | Total: {bought}")
            print(f"   Paid: CNY {paid:.2f} | Progress: {progress:.1f}%")
            print()
        
        # Overall totals
        total_completed = sum(lesson_counts.values())
        total_bought = sum(b for _, b, _ in payment_stats)
        total_paid = sum(p for _, _, p in payment_stats)
        
        print("=" * 40)
        print(f"Total across all courses:")
        print(f"   Lessons: {total_completed} completed / {total_bought} purchased")
        print(f"   Total Paid: CNY {total_paid:.2f}")
    
    print()
    conn.close()

def show_lesson(lesson_id):
    """Show specific lesson details"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, date, content, course_type, created_at
        FROM lessons WHERE id = ?
    ''', (lesson_id,))
    
    lesson = cursor.fetchone()
    conn.close()
    
    if not lesson:
        print(f"Lesson #{lesson_id} not found.")
        return
    
    id_, date, content, course, created = lesson
    course_name = COURSE_TYPES.get(course, course.title())
    print(f"\n📖 Lesson #{id_}")
    print("-" * 40)
    print(f"Course:   {course_name}")
    print(f"Date:     {date}")
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

def migrate_from_old():
    """Migrate data from old spanish-learning.db"""
    old_db = DB_DIR / "spanish-learning.db"
    if not old_db.exists():
        print("No old database found to migrate.")
        return
    
    init_db()
    conn_old = sqlite3.connect(old_db)
    conn_new = sqlite3.connect(DB_PATH)
    
    cursor_old = conn_old.cursor()
    cursor_new = conn_new.cursor()
    
    # Migrate lessons
    try:
        cursor_old.execute("SELECT date, content, created_at FROM lessons")
        lessons = cursor_old.fetchall()
        for lesson in lessons:
            cursor_new.execute('''
                INSERT INTO lessons (course_type, date, content, created_at)
                VALUES (?, ?, ?, ?)
            ''', ('spanish', lesson[0], lesson[1], lesson[2]))
        print(f"✅ Migrated {len(lessons)} Spanish lessons")
    except Exception as e:
        print(f"Could not migrate lessons: {e}")
    
    # Migrate payments
    try:
        cursor_old.execute("SELECT date, amount, currency, lessons_bought, notes, created_at FROM payments")
        payments = cursor_old.fetchall()
        for payment in payments:
            cursor_new.execute('''
                INSERT INTO payments (course_type, date, amount, currency, lessons_bought, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', ('spanish', payment[0], payment[1], payment[2], payment[3], payment[4], payment[5]))
        print(f"✅ Migrated {len(payments)} Spanish payments")
    except Exception as e:
        print(f"Could not migrate payments: {e}")
    
    conn_new.commit()
    conn_old.close()
    conn_new.close()
    print("✅ Migration complete!")

def main():
    if len(sys.argv) < 2:
        print("Usage: course.py <command> [args...]")
        print("\nCommands:")
        print("  <course> lesson [date] [content]     - Log a lesson")
        print("  <course> pay [date] <amount> <lessons> [notes] - Record payment")
        print("  stats [course]                       - Show statistics")
        print("  list [course]                        - List lessons")
        print("  payments [course]                    - List payments")
        print("  lesson-show <id>                     - Show lesson details")
        print("  lesson-update <id> <content>         - Update lesson")
        print("  lesson-delete <id>                   - Delete lesson")
        print("  payment-delete <id>                  - Delete payment")
        print("  migrate                              - Migrate from old database")
        print("\nCourses: spanish, boxing, yoga, piano, dance, swimming, cooking")
        sys.exit(1)
    
    command = sys.argv[1]
    
    # Handle non-course commands first
    if command == "stats":
        course = sys.argv[2] if len(sys.argv) > 2 else None
        if course:
            course = validate_course(course)
            if not course:
                sys.exit(1)
        show_stats(course)
    
    elif command == "list":
        course = sys.argv[2] if len(sys.argv) > 2 else None
        if course:
            course = validate_course(course)
            if not course:
                sys.exit(1)
        list_lessons(course)
    
    elif command == "payments":
        course = sys.argv[2] if len(sys.argv) > 2 else None
        if course:
            course = validate_course(course)
            if not course:
                sys.exit(1)
        list_payments(course)
    
    elif command == "lesson-show":
        if len(sys.argv) < 3:
            print("Usage: course.py lesson-show <id>")
            sys.exit(1)
        show_lesson(int(sys.argv[2]))
    
    elif command == "lesson-update":
        if len(sys.argv) < 4:
            print("Usage: course.py lesson-update <id> <content>")
            sys.exit(1)
        update_lesson(int(sys.argv[2]), " ".join(sys.argv[3:]))
    
    elif command == "lesson-delete":
        if len(sys.argv) < 3:
            print("Usage: course.py lesson-delete <id>")
            sys.exit(1)
        delete_lesson(int(sys.argv[2]))
    
    elif command == "payment-delete":
        if len(sys.argv) < 3:
            print("Usage: course.py payment-delete <id>")
            sys.exit(1)
        delete_payment(int(sys.argv[2]))
    
    elif command == "migrate":
        migrate_from_old()
    
    else:
        # Check if it's a course type command
        course_type = validate_course(command)
        
        if course_type:
            # Course-specific commands
            if len(sys.argv) < 3:
                print(f"Usage: course.py {command} <subcommand> [args...]")
                print(f"  lesson [date] [content]              - Log a {command} lesson")
                print(f"  pay [date] <amount> <lessons> [notes] - Record {command} payment")
                sys.exit(1)
            
            subcommand = sys.argv[2]
            args = sys.argv[3:] if len(sys.argv) > 3 else []
            
            if subcommand == "lesson":
                date, content = parse_lesson_args(args)
                add_lesson(course_type, content, date=date)
            
            elif subcommand == "pay":
                if len(args) < 2:
                    print(f"Usage: course.py {command} pay [date] <amount> <lessons> [notes]")
                    sys.exit(1)
                date, amount, lessons, notes = parse_payment_args(args)
                if amount is None or lessons is None:
                    print(f"Usage: course.py {command} pay [date] <amount> <lessons> [notes]")
                    sys.exit(1)
                add_payment(course_type, amount, lessons, notes=notes, date=date)
            
            else:
                print(f"Unknown subcommand: {subcommand}")
                sys.exit(1)
        else:
            print(f"Unknown command: {command}")
            print(f"Supported courses: {', '.join(COURSE_TYPES.keys())}")
            print("Or use: stats, list, payments, lesson-show, lesson-update, lesson-delete, payment-delete, migrate")
            sys.exit(1)

if __name__ == "__main__":
    main()
