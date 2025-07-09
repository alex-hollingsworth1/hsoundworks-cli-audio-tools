"""BPM Analyser"""

import os
import argparse
import librosa
import csv

AUDIO_EXTENSIONS = (".mp3", ".wav", ".flac", ".ogg")


def calculate_bpm(file_path):
    """Calculate the BPM of the file with exception handling for
    empty files and incorrect processing"""
    try:
        y, sr = librosa.load(file_path, sr=None)
        if y.size == 0:
            print(f"Empty or silent file: {file_path}")
            return None
        tempo = librosa.beat.tempo(y=y, sr=sr)[0]
        return round(tempo)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None


def csv_writing(arg, results_list):
    """Write the BPM and filename information to a CSV file"""
    with open(arg.log, 'w', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "bpm"])
        writer.writerows(results_list)
        print(f"\nBPM log saved to {arg.log}")


def discover_audio_files(folder_path):
    """Finds the audio files in the folder path specified,
    loops through them and calls calculate BPM function."""
    bpm_results = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(AUDIO_EXTENSIONS):
            full_path = os.path.join(folder_path, filename)
            bpm = calculate_bpm(full_path)
            if bpm:
                bpm_results.append((filename, bpm))
                print(f"{filename} - BPM - {bpm}")
    return bpm_results


def main():
    """Main function for BPM analyser"""
    parser = argparse.ArgumentParser(description="BPM analyser.")
    parser.add_argument("folder_path", type=str,
                        help="Path to folder with audio files.")
    parser.add_argument("--log", type=str,
                        help="Create a log of the BPM for the audio file")

    args = parser.parse_args()
    folder_path = args.folder_path

    audio_results = discover_audio_files(folder_path)

    if args.log:
        csv_writing(args, audio_results)


if __name__ == "__main__":
    main()
