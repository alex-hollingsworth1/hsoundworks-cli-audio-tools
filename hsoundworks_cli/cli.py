#!/usr/bin/env python3
"""Unified CLI for Audio Toolkit - Combines all audio processing features"""

import argparse
import sys
from pathlib import Path

# Import your modules (adjust paths as needed)
from analyzers.bpm import calculate_bpm, discover_audio_files, csv_writing
from analyzers.features import audio_file_checker
from converters.format import convert_audio
from database.manager import (
    setup_database,
    export_to_csv,
    view_database,
    filter_loops,
)


def create_parser():
    """Create the main argument parser with subcommands"""
    parser = argparse.ArgumentParser("""Audio Features Analysis Module""")

import os
import datetime
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sqlite3

# Set numpy print options
np.set_printoptions(precision=2, suppress=True)


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
        # Import from database.manager to avoid circular imports
        from database.manager import save_to_database
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
        description="Audio Toolkit - Analyze, convert, and manage audio files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  audio-toolkit analyze ~/music --bpm --save-db
  audio-toolkit convert ~/samples --format mp3
  audio-toolkit db --view
  audio-toolkit db --export-csv output.csv
        """,
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands"
    )

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze audio files"
    )
    analyze_parser.add_argument(
        "folder_path", type=str, help="Path to audio folder"
    )
    analyze_parser.add_argument(
        "--bpm", action="store_true", help="Calculate BPM"
    )
    analyze_parser.add_argument(
        "--features", action="store_true", help="Extract audio features"
    )
    analyze_parser.add_argument(
        "--plot", action="store_true", help="Show waveform plots"
    )
    analyze_parser.add_argument(
        "--mfcc", action="store_true", help="Extract MFCC features"
    )
    analyze_parser.add_argument(
        "--chroma", action="store_true", help="Extract Chroma features"
    )
    analyze_parser.add_argument(
        "--spectrogram", action="store_true", help="Extract spectrogram"
    )
    analyze_parser.add_argument(
        "--save-db", action="store_true", help="Save to database"
    )
    analyze_parser.add_argument(
        "--log", type=str, help="Save BPM results to CSV"
    )

    # Convert command
    convert_parser = subparsers.add_parser(
        "convert", help="Convert audio files"
    )
    convert_parser.add_argument(
        "folder_path", type=str, help="Path to audio folder"
    )
    convert_parser.add_argument(
        "--format",
        type=str,
        default="wav",
        choices=["wav", "mp3", "flac", "ogg"],
        help="Target format (default: wav)",
    )
    convert_parser.add_argument(
        "--output-dir", type=str, help="Output directory"
    )

    # Database command
    db_parser = subparsers.add_parser("db", help="Database operations")
    db_group = db_parser.add_mutually_exclusive_group(required=True)
    db_group.add_argument(
        "--view", action="store_true", help="View database contents"
    )
    db_group.add_argument("--export-csv", type=str, help="Export to CSV file")
    db_group.add_argument(
        "--filter-loops",
        action="store_true",
        help="Show files longer than 3 seconds",
    )

    # Batch command (analyze entire library)
    batch_parser = subparsers.add_parser(
        "batch", help="Batch process audio library"
    )
    batch_parser.add_argument(
        "folder_path", type=str, help="Root folder of audio library"
    )
    batch_parser.add_argument(
        "--recursive", action="store_true", help="Process folders recursively"
    )
    batch_parser.add_argument(
        "--bpm", action="store_true", help="Calculate BPM"
    )
    batch_parser.add_argument(
        "--save-db", action="store_true", help="Save all to database"
    )

    return parser


def handle_analyze(args):
    """Handle the analyze command"""
    folder_path = Path(args.folder_path)

    if not folder_path.exists():
        print(f"Error: Folder not found: {folder_path}")
        return

    if args.bpm:
        print("\n🎵 Calculating BPM...")
        results = discover_audio_files(str(folder_path))

        if args.log:
            # Use your existing CSV writing function
            from analyzers.bpm import csv_writing

            csv_writing(args, results)

    if args.features or args.mfcc or args.chroma or args.spectrogram or args.save_db:
        print("\n📊 Analyzing audio features...")
        for file in folder_path.glob("*"):
            if file.suffix.lower() in (".mp3", ".wav", ".flac", ".ogg"):
                audio_file_checker(
                    str(file),
                    plot=args.plot,
                    mfcc=args.mfcc,
                    chroma=args.chroma,
                    spectrogram=args.spectrogram,
                    save_db=args.save_db,
                )


def handle_convert(args):
    """Handle the convert command"""
    folder_path = Path(args.folder_path)
    output_dir = args.output_dir or "converted_audio"

    if not folder_path.exists():
        print(f"Error: Folder not found: {folder_path}")
        return

    print(f"\n🔄 Converting audio files to {args.format}...")

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    for file in folder_path.glob("*"):
        if file.suffix.lower() in (".mp3", ".wav", ".flac", ".ogg"):
            convert_audio(str(file), str(output_path), args.format)


def handle_database(args):
    """Handle database operations"""
    # Ensure database exists
    setup_database()

    if args.view:
        view_database()
    elif args.export_csv:
        export_to_csv(args.export_csv)
    elif args.filter_loops:
        filter_loops()


def handle_batch(args):
    """Handle batch processing of entire library"""
    folder_path = Path(args.folder_path)

    if not folder_path.exists():
        print(f"Error: Folder not found: {folder_path}")
        return

    # Get all audio files
    if args.recursive:
        audio_files = []
        for ext in (".mp3", ".wav", ".flac", ".ogg"):
            audio_files.extend(folder_path.rglob(f"*{ext}"))
    else:
        audio_files = [
            f
            for f in folder_path.iterdir()
            if f.suffix.lower() in (".mp3", ".wav", ".flac", ".ogg")
        ]

    print(f"\n🎵 Found {len(audio_files)} audio files")

    if args.save_db:
        setup_database()

    for i, file in enumerate(audio_files, 1):
        print(f"\n[{i}/{len(audio_files)}] Processing: {file.name}")

        if args.bpm:
            bpm = calculate_bpm(str(file))
            if bpm:
                print(f"  BPM: {bpm}")

        if args.save_db:
            audio_file_checker(str(file), save_db=True)


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Route to appropriate handler
    if args.command == "analyze":
        handle_analyze(args)
    elif args.command == "convert":
        handle_convert(args)
    elif args.command == "db":
        handle_database(args)
    elif args.command == "batch":
        handle_batch(args)

    print("\n✅ Done!")


if __name__ == "__main__":
    main()
