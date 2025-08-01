"""Database Management Module for Audio Library"""

import sqlite3
import csv
from pathlib import Path

# Database constants
DATABASE_NAME = "audio_library.db"
DURATION_DECIMAL_PLACES = 1
DEFAULT_MIN_DURATION = 3.0


def setup_database():
    """Create a simple database to store our audio analysis results"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audio_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                sample_rate INTEGER NOT NULL,
                duration_seconds REAL NOT NULL
            )
        """
        )

        conn.commit()
        print("Database setup completed successfully")
        return True

    except sqlite3.Error as e:
        print(f"Database setup error: {e}")
        return False
    except (ValueError, TypeError) as e:
        print(f"Data validation error setting up database: {e}")
        return False
    finally:
        if "conn" in locals():
            conn.close()


def save_to_database(file_path, sample_rate, duration):
    """Save the audio analysis results to our database"""
    # Validate input parameters
    if not file_path:
        print("Error: File path cannot be empty")
        return False

    if not isinstance(sample_rate, (int, float)) or sample_rate <= 0:
        print(f"Error: Invalid sample rate: {sample_rate}")
        return False

    if not isinstance(duration, (int, float)) or duration <= 0:
        print(f"Error: Invalid duration: {duration}")
        return False

    # Validate file path
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        print(f"Warning: File path does not exist: {file_path}")
        # Continue anyway as the file might have been processed and moved

    try:
        conn = sqlite3.connect(DATABASE_NAME)
        
        # Round duration to specified decimal places before saving
        duration = round(duration, DURATION_DECIMAL_PLACES)
        file_name = file_path_obj.name

        conn.execute(
            """
            INSERT OR REPLACE INTO audio_files
            (file_name, sample_rate, duration_seconds)
            VALUES (?, ?, ?)
        """,
            (file_name, int(sample_rate), duration),
        )
        conn.commit()
        print(f"Saved to database: {file_name}")
        return True

    except sqlite3.Error as e:
        print(f"Database error saving {file_path_obj.name}: {e}")
        return False
    except (ValueError, TypeError) as e:
        print(f"Data validation error saving to database: {e}")
        return False
    finally:
        if "conn" in locals():
            conn.close()


def export_to_csv(output_file="ah_audio_sample_library.csv"):
    """Export the database to a CSV file"""
    if not output_file:
        print("Error: Output file name cannot be empty")
        return False
        
    # Validate output directory
    output_path = Path(output_file)
    output_dir = output_path.parent
    
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Error creating output directory {output_dir}: {e}")
        return False

    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT file_name, sample_rate, duration_seconds
            FROM audio_files
            ORDER BY file_name
        """
        )

        rows = cursor.fetchall()
        if not rows:
            print("Warning: No data found in database to export")
            return False

        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                [
                    "File Name",
                    "Sample Rate (Hz)",
                    "Duration (seconds)",
                ]
            )

            for row in rows:
                writer.writerow(row)

        print(f"Exported {len(rows)} records to {output_file}")
        return True

    except sqlite3.Error as e:
        print(f"Database error during export: {e}")
        return False
    except PermissionError:
        print(f"Error: Permission denied writing to {output_file}")
        return False
    except OSError as e:
        print(f"Error writing CSV file {output_file}: {e}")
        return False
    except (ValueError, TypeError) as e:
        print(f"Data validation error during export: {e}")
        return False
    finally:
        if "conn" in locals():
            conn.close()


def view_database():
    """View what's in the database"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT file_name, sample_rate, duration_seconds FROM audio_files"
        )

        rows = cursor.fetchall()
        if not rows:
            print("Database is empty - no audio files found")
            return True

        print("\nAudio Library Database:")
        print("-" * 60)

        for row in rows:
            name, sr, duration = row
            print(f"{name:<30} | {sr:>6} Hz | {duration:>6.2f}s")

        print(f"\nTotal files: {len(rows)}")
        return True

    except sqlite3.Error as e:
        print(f"Database error viewing records: {e}")
        return False
    except (ValueError, TypeError) as e:
        print(f"Data validation error viewing database: {e}")
        return False
    finally:
        if "conn" in locals():
            conn.close()


def filter_loops(min_duration=DEFAULT_MIN_DURATION):
    """Show files in the database longer than min_duration seconds
    (default 3)."""
    # Validate input
    if not isinstance(min_duration, (int, float)) or min_duration < 0:
        print(f"Error: Invalid minimum duration: {min_duration}")
        return False
        
    try:
        conn = sqlite3.connect(DATABASE_NAME)
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

        rows = cursor.fetchall()
        if not rows:
            print(f"No audio files found longer than {min_duration} seconds")
            return True

        print(f"\nAudio Files longer Than {min_duration} Seconds:")
        print("-" * 60)
        for row in rows:
            name, sr, duration = row
            print(f"{name:<30} | {sr:>6} Hz | {duration:>6.2f}s")

        print(f"\nFound {len(rows)} files longer than {min_duration}s")
        return True

    except sqlite3.Error as e:
        print(f"Database error filtering records: {e}")
        return False
    except (ValueError, TypeError) as e:
        print(f"Data validation error filtering database: {e}")
        return False
    finally:
        if "conn" in locals():
            conn.close()
