#!/usr/bin/env python3
"""Unified CLI for Audio Toolkit - combines all audio processing
features"""

import argparse
import sys
from pathlib import Path
import numpy as np

from analyzers.bpm import calculate_bpm, csv_writing, discover_audio_files
from analyzers.features import audio_file_checker
from converters.format import convert_audio
from database.manager import (
    setup_database,
    export_to_csv,
    view_database,
    filter_loops,
)

# CLI constants
SUPPORTED_EXTENSIONS = (".mp3", ".wav", ".flac", ".ogg")
DEFAULT_OUTPUT_DIR = "converted_audio"

np.set_printoptions(precision=2, suppress=True)


def create_parser():
    """Create and configure the command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Audio Features Analysis Module",
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

    # Batch command
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
    """Handle the analyze command."""
    folder_path = Path(args.folder_path)
    if not folder_path.exists():
        print(f"Error: Folder not found: {folder_path}")
        return
    if args.bpm:
        print("\nCalculating BPM...")
        results = discover_audio_files(str(folder_path))
        if args.log:
            csv_writing(args, results)
    if (
        args.features
        or args.mfcc
        or args.chroma
        or args.spectrogram
        or args.save_db
    ):
        print("\nAnalyzing audio features...")
        for file in folder_path.glob("*"):
            if file.suffix.lower() in SUPPORTED_EXTENSIONS:
                audio_file_checker(
                    str(file),
                    plot=args.plot,
                    mfcc=args.mfcc,
                    chroma=args.chroma,
                    spectrogram=args.spectrogram,
                    save_db=args.save_db,
                )


def handle_convert(args):
    """Handle the convert command."""
    folder_path = Path(args.folder_path)
    output_dir = args.output_dir or DEFAULT_OUTPUT_DIR
    if not folder_path.exists():
        print(f"Error: Folder not found: {folder_path}")
        return
    print(f"\nConverting audio files to {args.format}...")
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    for file in folder_path.glob("*"):
        if file.suffix.lower() in SUPPORTED_EXTENSIONS:
            convert_audio(str(file), str(output_path), args.format)


def handle_database(args):
    """Handle the database command."""
    setup_database()
    if args.view:
        view_database()
    elif args.export_csv:
        export_to_csv(args.export_csv)
    elif args.filter_loops:
        filter_loops()


def handle_batch(args):
    """Handle the batch of audio files."""
    folder_path = Path(args.folder_path)
    if not folder_path.exists():
        print(f"Error: Folder not found: {folder_path}")
        return
    if args.recursive:
        audio_files = []
        for ext in SUPPORTED_EXTENSIONS:
            audio_files.extend(folder_path.rglob(f"*{ext}"))
    else:
        audio_files = [
            f
            for f in folder_path.iterdir()
            if f.suffix.lower() in SUPPORTED_EXTENSIONS
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
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    if args.command == "analyze":
        handle_analyze(args)
    elif args.command == "convert":
        handle_convert(args)
    elif args.command == "db":
        handle_database(args)
    elif args.command == "batch":
        handle_batch(args)
    print("\nDone!")


if __name__ == "__main__":
    main()
