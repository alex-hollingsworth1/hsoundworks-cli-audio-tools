"""Database Management Module for Audio Library"""

import sqlite3
import csv
from pathlib import Path


def setup_database():
    """Create a simple database to store our audio analysis results"""
    conn = sqlite3.connect("audio_library.db")

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS audio_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            sample_rate INTEGER,
            duration_seconds REAL
        )
    """
    )

    conn.commit()
    conn.close()


def save_to_database(file_path, sample_rate, duration):
    """Save the audio analysis results to our database"""
    conn = sqlite3.connect("audio_library.db")

    # Round duration to 1 decimal place before saving
    duration = round(duration, 1)

    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO audio_files
            (file_name, sample_rate, duration_seconds)
            VALUES (?, ?, ?)
        """,
            (Path(file_path).name, sample_rate, duration),
        )
        conn.commit()
        print(f"Saved to database: {Path(file_path).name}")
    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


def export_to_csv(output_file="ah_audio_sample_library.csv"):
    """Export the database to a CSV file"""
    conn = sqlite3.connect("audio_library.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT file_name, sample_rate, duration_seconds
        FROM audio_files
        ORDER BY file_name
    """
    )

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "File Name",
                "Sample Rate (Hz)",
                "Duration (seconds)",
            ]
        )

        for row in cursor.fetchall():
            writer.writerow(row)

    conn.close()
    print(f"Exported to {output_file}")


def view_database():
    """View what's in the database"""
    conn = sqlite3.connect("audio_library.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT file_name, sample_rate, duration_seconds FROM audio_files"
    )

    print("\nAudio Library Database:")
    print("-" * 60)

    for row in cursor.fetchall():
        name, sr, duration = row
        print(f"{name:<30} | {sr:>6} Hz | {duration:>6.2f}s")

    conn.close()


def filter_loops(min_duration=3.0):
    """Show files in the database longer than min_duration seconds
    (default 3)."""
    conn = sqlite3.connect("audio_library.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT file_name, sample_rate, duration_seconds
        FROM audio_files
        WHERE duration_seconds > ?
        ORDER BY duration_seconds DESC
    """,
        (min_duration,),
    )

    print(f"\nAudio Files longer Than {min_duration} Seconds:")
    print("-" * 60)
    for row in cursor.fetchall():
        name, sr, duration = row
        print(f"{name:<30} | {sr:>6} Hz | {duration:>6.2f}s")

    conn.close()
