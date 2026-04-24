---
name: course-learning
description: Track learning progress for multiple courses including Spanish, Boxing, and more. Use when the user wants to log lessons, track payments, view statistics for any type of course or training.
---

# Course Learning Tracker

Track learning progress for multiple courses: Spanish, Boxing, Yoga, Piano, and more.

## Supported Courses

- `spanish` - Spanish language lessons
- `boxing` - Boxing training
- `yoga` - Yoga classes
- `piano` - Piano lessons
- `dance` - Dance classes
- `swimming` - Swimming lessons
- `cooking` - Cooking classes

## Quick Start

1. **Log a lesson**: `/course <course> lesson [date] [content]`
2. **Record payment**: `/course <course> pay [date] <amount> <lessons> [notes]`
3. **View stats**: `/course stats [course]`
4. **List lessons**: `/course list [course]`
5. **List payments**: `/course payments [course]`

Date format: `YYYY-MM-DD` (optional, defaults to today)

## Examples

### Spanish Lessons

```
/course spanish lesson                           # Log today's Spanish lesson
/course spanish lesson "Learned past tense"      # Log with notes
/course spanish lesson 2026-02-08 "Review"       # Log for specific date

/course spanish pay 3000 10                      # Buy 10 Spanish lessons for 3000 CNY
/course spanish pay 2026-01-10 1500 5            # Record past payment
/course spanish pay 2000 20 "New student package" # With notes
```

### Boxing Training

```
/course boxing lesson                            # Log today's boxing session
/course boxing lesson "Heavy bag workout"        # With notes

/course boxing pay 2500 20                       # Buy 20 boxing sessions
/course boxing pay 3000 30 "3-month package"     # With notes
```

### View Statistics

```
/course stats                                    # Show all courses summary
/course stats spanish                            # Show only Spanish stats
/course stats boxing                             # Show only Boxing stats
```

### List Records

```
/course list                                     # List all lessons
/course list spanish                             # List Spanish lessons only
/course list boxing                              # List Boxing lessons only

/course payments                                 # List all payments
/course payments spanish                         # List Spanish payments only
```

## Database Schema

SQLite database at `~/.openclaw/course-learning.db`

### Table: lessons
- `id` (INTEGER PRIMARY KEY)
- `course_type` (TEXT) - Course type (spanish, boxing, yoga, etc.)
- `date` (TEXT) - ISO date (YYYY-MM-DD)
- `content` (TEXT) - Lesson notes
- `created_at` (TEXT) - ISO timestamp

### Table: payments
- `id` (INTEGER PRIMARY KEY)
- `course_type` (TEXT) - Course type
- `date` (TEXT) - ISO date (YYYY-MM-DD)
- `amount` (REAL) - Payment amount
- `currency` (TEXT) - Currency code (default: CNY)
- `lessons_bought` (INTEGER) - Number of lessons purchased
- `notes` (TEXT) - Additional notes
- `created_at` (TEXT) - ISO timestamp

## Management Commands

```
/course lesson-show <id>        # Show lesson details
/course lesson-update <id> <content>  # Update lesson notes
/course lesson-delete <id>      # Delete a lesson
/course payment-delete <id>     # Delete a payment
```

## Migration from Old Database

If you have data from the old `spanish-learning.db`, run:

```
/course migrate
```

This will migrate all Spanish lessons and payments to the new database.

## Scripts

- `scripts/course.py` - Main course management script
