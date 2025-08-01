"""BPM Analyser Module"""

import os
import csv
import librosa


# Audio file extensions supported by the BPM analyzer
AUDIO_EXTENSIONS = (".mp3", ".wav", ".flac", ".ogg")

# BPM analysis constants
MIN_BPM = 0
MAX_BPM = 300


def calculate_bpm(file_path):
    """Calculate the BPM of the file with exception handling for
    empty files and incorrect processing"""
    # Validate file existence
    if not os.path.isfile(file_path):
        print(f"Error: File does not exist: {file_path}")
        return None

    # Validate file extension
    if not file_path.lower().endswith(AUDIO_EXTENSIONS):
        print(f"Error: Unsupported audio format: {file_path}")
        return None

    try:
        # Check file size to avoid processing empty files
        if os.path.getsize(file_path) == 0:
            print(f"Error: Empty file: {file_path}")
            return None

        y, sr = librosa.load(file_path, sr=None)
        if y is None or y.size == 0:
            print(f"Error: Could not load audio data from file: {file_path}")
            return None

        tempo = librosa.beat.tempo(y=y, sr=sr)[0]
        if tempo <= MIN_BPM or tempo > MAX_BPM:  # Sanity check for reasonable BPM range
            print(
                f"Warning: Unusual BPM detected ({tempo:.1f}) "
                f"for file: {file_path}"
            )

        return round(tempo)

    except librosa.LibrosaError as e:
        print(f"Librosa error processing {file_path}: {e}")
        return None
    except FileNotFoundError:
        print(f"Error: File not found during processing: {file_path}")
        return None
    except PermissionError:
        print(f"Error: Permission denied accessing file: {file_path}")
        return None
    except (ValueError, TypeError) as e:
        print(f"Data validation error processing {file_path}: {e}")
        return None
    except MemoryError:
        print(f"Memory error: File too large to process: {file_path}")
        return None


def csv_writing(arg, results_list):
    """Write the BPM and filename information to a CSV file"""
    if not results_list:
        print("Warning: No BPM results to write to CSV")
        return False

    # Validate output directory exists
    output_dir = os.path.dirname(arg.log)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            print(f"Error creating output directory {output_dir}: {e}")
            return False

    try:
        with open(arg.log, "w", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["filename", "bpm"])
            writer.writerows(results_list)
            print(f"\nBPM log saved to {arg.log}")
            return True
    except PermissionError:
        print(f"Error: Permission denied writing to {arg.log}")
        return False
    except OSError as e:
        print(f"Error writing CSV file {arg.log}: {e}")
        return False
    except (ValueError, TypeError) as e:
        print(f"Data validation error writing CSV file: {e}")
        return False


def discover_audio_files(folder_path):
    """Finds the audio files in the folder path specified,
    loops through them and calls calculate BPM function."""
    # Validate folder path exists
    if not os.path.exists(folder_path):
        print(f"Error: Folder does not exist: {folder_path}")
        return []

    if not os.path.isdir(folder_path):
        print(f"Error: Path is not a directory: {folder_path}")
        return []

    # Check if folder is readable
    if not os.access(folder_path, os.R_OK):
        print(f"Error: No read permission for folder: {folder_path}")
        return []

    bpm_results = []
    try:
        files = os.listdir(folder_path)
        audio_files = [
            f for f in files if f.lower().endswith(AUDIO_EXTENSIONS)
        ]

        if not audio_files:
            print(f"Warning: No supported audio files found in {folder_path}")
            return []

        print(f"Found {len(audio_files)} audio file(s) in {folder_path}")

        for filename in audio_files:
            full_path = os.path.join(folder_path, filename)
            bpm = calculate_bpm(full_path)
            if bpm:
                bpm_results.append((filename, bpm))
                print(f"{filename} - BPM - {bpm}")

    except PermissionError:
        print(f"Error: Permission denied accessing folder: {folder_path}")
        return []
    except OSError as e:
        print(f"Error accessing folder {folder_path}: {e}")
        return []
    except (ValueError, TypeError) as e:
        print(f"Data validation error processing folder {folder_path}: {e}")
        return []

    return bpm_results
