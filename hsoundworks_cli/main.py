"""Second Librosa commit to check the audio file sample rate
and duration, save it to a database and export it as a CSV."""

import os
import sqlite3
import csv
from pathlib import Path
import datetime
import argparse
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt

DEFAULT_AUDIO_DIR = (
    "/Users/alexhollingsworth/Dropbox/Alex Hollingsworth/Education/"
    "Coding/AI Music/Librosa/audio_samples_db_test"
)

np.set_printoptions(precision=2, suppress=True)  # Round floats when printing


def audio_file_checker(
    file_path,
    plot=False,
    mfcc=False,
    chroma=False,
    spectrogram=False,
    save_db=False,
):
    """Analyses audio file and provides file name, sample rate
    and duration. Option to show plot graphs, mfcc graphs and chroma
    graphs."""
    # Load the audio
    y, sr = librosa.load(file_path, sr=None, mono=False)

    output_dir = os.path.join(os.getcwd(), "outputs")
    os.makedirs(output_dir, exist_ok=True)

    # Work out the duration
    duration = librosa.get_duration(y=y, sr=sr)

    # If stereo, average the channels to make it mono
    if y.ndim > 1:
        y = np.mean(y, axis=0)

    # Print core info
    print(f"\nFile: {os.path.basename(file_path)}")
    print(f"Sample Rate: {sr} Hz")
    print(f"Duration: {datetime.timedelta(seconds=round(duration))}")

    # Save to database
    if save_db:
        save_to_database(file_path, sr, duration)

    if plot:
        plot_waveform(y, sr, title=os.path.basename(file_path))

    if mfcc:
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

        if plot:
            filename = os.path.splitext(os.path.basename(file_path))[0]
            save_path = os.path.join(output_dir, f"{filename}_mfcc.png")
            plot_features(
                mfccs,
                title="MFCC",
                ylabel="MFCC Coefficients",
                save_path=save_path,
            )

    if chroma:
        chroma_feat = librosa.feature.chroma_stft(y=y, sr=sr)

        if plot:
            filename = os.path.splitext(os.path.basename(file_path))[0]
            save_path = os.path.join(output_dir, f"{filename}_chroma.png")

            plot_features(
                chroma_feat,
                title="Chroma",
                ylabel="Pitch Class",
                save_path=save_path,
            )

    if spectrogram:
        spectro_feat = librosa.stft(y=y)
        s_db = librosa.amplitude_to_db(np.abs(spectro_feat), ref=np.max)

        if plot:
            filename = os.path.splitext(os.path.basename(file_path))[0]
            save_path = os.path.join(output_dir, f"{filename}_spectrogram.png")

            plot_features(
                s_db,
                title="Spectrogram",
                ylabel="Frequency",
                save_path=save_path,
            )


def plot_waveform(y, sr, title="Waveform"):
    """Function that draws waveform if user types --plot"""
    plt.figure(figsize=(10, 4))
    librosa.display.waveshow(y, sr=sr)
    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.tight_layout()
    plt.show()


def plot_features(
    feature, title="Feature", ylabel="Feature Coefficients", save_path=None
):
    """Plots MFCC and Chroma graphs, and then saves them as a PNG"""
    plt.figure(figsize=(10, 4))
    plt.imshow(feature, aspect="auto", origin="lower", cmap="magma")
    plt.title(title)
    plt.xlabel("Time (frames)")
    plt.ylabel(ylabel)
    plt.colorbar(format="%+2.0f dB")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
        print(f"Saved plot to: {save_path}")
    else:
        plt.show()

    plt.close()


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
    (default 8)."""
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


def main():
    """Main function for CLI audio tool checker."""
    print("✅ Script is running...")

    # Setup database on first run
    setup_database()

    parser = argparse.ArgumentParser(
        description="Process audio files and display their properties."
    )

    parser.add_argument(
        "folder_path",
        type=str,
        nargs="?",
        default=DEFAULT_AUDIO_DIR,
        help="Path to audio files.",
    )
    parser.add_argument(
        "--plot", action="store_true", help="Show waveform plot."
    )
    parser.add_argument(
        "--mfcc", action="store_true", help="Extract MFCC features."
    )
    parser.add_argument(
        "--chroma", action="store_true", help="Extract Chroma features."
    )
    parser.add_argument(
        "--spectrogram",
        action="store_true",
        help="Extract and display Spectrogram",
    )
    parser.add_argument(
        "--save-db", action="store_true", help="Save results to database"
    )
    parser.add_argument(
        "--export-csv", action="store_true", help="Export database to CSV"
    )
    parser.add_argument(
        "--view-db", action="store_true", help="View database contents"
    )
    parser.add_argument(
        "--filterloops",
        action="store_true",
        help="Show only audio files longer than 3 seconds",
    )

    args = parser.parse_args()

    if args.export_csv:
        export_to_csv()
        return

    if args.view_db:
        view_database()
        return

    if args.filterloops:
        filter_loops()
        return

    folder_path = args.folder_path

    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".wav", ".mp3")):
            full_path = os.path.join(folder_path, filename)
            audio_file_checker(
                full_path,
                plot=args.plot,
                mfcc=args.mfcc,
                chroma=args.chroma,
                spectrogram=args.spectrogram,
                save_db=args.save_db,
            )


if __name__ == "__main__":
    main()
