#!/usr/bin/env python3
"""
Populate the database with American Sign Language (ASL) lessons
"""

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.environ.get('DATABASE_PATH', os.path.join(BASE_DIR, 'studysystem.db'))

# ASL Alphabet and common signs with descriptions
lessons_data = [
    # Alphabet (A-Z)
    ("Letter A", "Make a fist with thumb resting on the side", "alphabet", "beginner"),
    ("Letter B", "Flat hand, fingers together pointing up, thumb across palm", "alphabet", "beginner"),
    ("Letter C", "Curve fingers and thumb to form a C shape", "alphabet", "beginner"),
    ("Letter D", "Touch index finger to thumb, other fingers up", "alphabet", "beginner"),
    ("Letter E", "Curl all fingers down touching thumb", "alphabet", "beginner"),
    ("Letter F", "Touch index and thumb tips, other fingers up", "alphabet", "beginner"),
    ("Letter G", "Point index finger and thumb horizontally", "alphabet", "beginner"),
    ("Letter H", "Extend index and middle fingers horizontally", "alphabet", "beginner"),
    ("Letter I", "Extend pinky finger up, other fingers down", "alphabet", "beginner"),
    ("Letter J", "Draw a J with pinky finger in the air", "alphabet", "beginner"),
    ("Letter K", "Index and middle up in V, thumb between them", "alphabet", "beginner"),
    ("Letter L", "Extend thumb and index at 90 degrees (L shape)", "alphabet", "beginner"),
    ("Letter M", "Tuck thumb under first three fingers", "alphabet", "beginner"),
    ("Letter N", "Tuck thumb under first two fingers", "alphabet", "beginner"),
    ("Letter O", "Make O shape with all fingers and thumb", "alphabet", "beginner"),
    ("Letter P", "Like K but pointed down", "alphabet", "beginner"),
    ("Letter Q", "Point index and thumb down (like upside-down G)", "alphabet", "beginner"),
    ("Letter R", "Cross middle finger over index finger", "alphabet", "beginner"),
    ("Letter S", "Make fist with thumb across fingers", "alphabet", "beginner"),
    ("Letter T", "Tuck thumb between index and middle finger", "alphabet", "beginner"),
    ("Letter U", "Extend index and middle fingers together, up", "alphabet", "beginner"),
    ("Letter V", "Peace sign - index and middle fingers up in V", "alphabet", "beginner"),
    ("Letter W", "Extend index, middle, and ring fingers up", "alphabet", "beginner"),
    ("Letter X", "Bend index finger into hook shape", "alphabet", "beginner"),
    ("Letter Y", "Extend thumb and pinky (hang loose sign)", "alphabet", "beginner"),
    ("Letter Z", "Draw a Z in the air with index finger", "alphabet", "beginner"),
    
    # Common Greetings
    ("Hello", "Wave hand side to side with palm facing out", "greeting", "beginner"),
    ("Goodbye", "Wave hand with palm facing in, move away from body", "greeting", "beginner"),
    ("Thank You", "Touch fingertips to chin, move hand forward and down", "greeting", "beginner"),
    ("Please", "Rub flat hand in circle on chest", "greeting", "beginner"),
    ("You're Welcome", "Flat hand at forehead, move forward", "greeting", "beginner"),
    ("Sorry", "Fist on chest, move in circular motion", "greeting", "beginner"),
    ("Nice to Meet You", "Bring index fingers together from sides", "greeting", "beginner"),
    
    # Basic Questions
    ("What", "Shake both hands side to side, palms up", "question", "beginner"),
    ("Where", "Point index finger up, shake side to side", "question", "beginner"),
    ("When", "Point index finger up, circle one finger around other", "question", "beginner"),
    ("Who", "Circle index finger around lips", "question", "beginner"),
    ("Why", "Touch forehead with middle finger, pull away to Y handshape", "question", "beginner"),
    ("How", "Backs of hands together, roll forward", "question", "beginner"),
    
    # Family Signs
    ("Mother", "Thumb of open hand taps chin", "family", "beginner"),
    ("Father", "Thumb of open hand taps forehead", "family", "beginner"),
    ("Sister", "L handshape at chin, move down to join other L hand", "family", "intermediate"),
    ("Brother", "L handshape at forehead, move down to join other L hand", "family", "intermediate"),
    ("Baby", "Rock arms as if holding baby", "family", "beginner"),
    ("Family", "F handshapes, circle from sides to meet", "family", "intermediate"),
    
    # Common Words
    ("Yes", "Fist with knuckles forward, nod wrist up and down", "common", "beginner"),
    ("No", "Snap index, middle finger and thumb together", "common", "beginner"),
    ("Help", "Fist on flat palm, lift both hands together", "common", "beginner"),
    ("Water", "W handshape, tap chin twice", "common", "beginner"),
    ("Food/Eat", "Flat O hand, tap lips twice", "common", "beginner"),
    ("Drink", "C hand, tip toward mouth as if holding cup", "common", "beginner"),
    ("Sleep", "Open hand slides down face, close to flat O", "common", "beginner"),
    ("Home", "Flat O at lips, move to cheek", "common", "beginner"),
    ("School", "Clap hands twice", "common", "beginner"),
    ("Friend", "Hook index fingers together, then reverse", "common", "beginner"),
    ("Love", "Cross fists over heart", "common", "beginner"),
    ("Happy", "Brush flat hand up chest twice", "common", "beginner"),
    ("Sad", "Both hands slide down face", "common", "beginner"),
    
    # Numbers (1-10)
    ("Number 1", "Extend index finger up", "number", "beginner"),
    ("Number 2", "Extend index and middle fingers", "number", "beginner"),
    ("Number 3", "Extend thumb, index, and middle fingers", "number", "beginner"),
    ("Number 4", "Extend all fingers except thumb", "number", "beginner"),
    ("Number 5", "Extend all five fingers", "number", "beginner"),
    ("Number 6", "Extend thumb and pinky, others down", "number", "beginner"),
    ("Number 7", "Extend thumb, index, middle, ring fingers", "number", "beginner"),
    ("Number 8", "Extend thumb, index, middle fingers down", "number", "beginner"),
    ("Number 9", "Touch thumb to index, others extended", "number", "beginner"),
    ("Number 10", "Shake A handshape (fist with thumb out)", "number", "beginner"),
    
    # Colors
    ("Red", "Touch lips with index finger, move down", "color", "intermediate"),
    ("Blue", "Shake B handshape side to side", "color", "intermediate"),
    ("Green", "Shake G handshape side to side", "color", "intermediate"),
    ("Yellow", "Shake Y handshape side to side", "color", "intermediate"),
    ("Black", "Draw line across forehead with index finger", "color", "intermediate"),
    ("White", "Flat hand on chest, pull out closing to flat O", "color", "intermediate"),
]

def populate_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Clear existing lessons
    cursor.execute("DELETE FROM lessons")
    print(f"Cleared existing lessons")
    
    # Insert new lessons
    inserted = 0
    for title, description, sign_type, difficulty in lessons_data:
        cursor.execute(
            "INSERT INTO lessons (title, description, sign_type, difficulty) VALUES (?, ?, ?, ?)",
            (title, description, sign_type, difficulty)
        )
        inserted += 1
    
    conn.commit()
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM lessons")
    count = cursor.fetchone()[0]
    
    print(f"\n✅ Successfully populated {count} lessons!")
    print(f"\nBreakdown:")
    
    cursor.execute("SELECT sign_type, COUNT(*) FROM lessons GROUP BY sign_type")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]} lessons")
    
    cursor.execute("SELECT difficulty, COUNT(*) FROM lessons GROUP BY difficulty")
    print(f"\nBy difficulty:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]} lessons")
    
    conn.close()
    print(f"\n🎉 Database ready! Restart the server to see lessons.")

if __name__ == "__main__":
    populate_database()
