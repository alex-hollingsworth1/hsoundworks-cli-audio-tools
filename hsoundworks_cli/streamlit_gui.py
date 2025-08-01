#!/usr/bin/env python3
"""Streamlit GUI for Audio Toolkit"""

import streamlit as st
import os
from pathlib import Path
import pandas as pd
import tempfile

# Import your existing modules
from analyzers.bpm import calculate_bpm, discover_audio_files, csv_writing
from analyzers.features import audio_file_checker
from converters.format import convert_audio
from database.manager import (
    setup_database,
    export_to_csv,
    view_database,
    filter_loops,
)

SUPPORTED_EXTENSIONS = (".mp3", ".wav", ".flac", ".ogg")

st.set_page_config(page_title="Audio Toolkit", page_icon="🎵", layout="wide")

st.title("🎵 Audio Toolkit GUI")
st.markdown("---")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["🔍 Analyze", "🔄 Convert", "💾 Database", "📦 Batch"]
)

with tab1:
    st.header("Audio Analysis")

    # Folder selection
    folder_path = st.text_input(
        "Folder Path", placeholder="Enter path to audio folder"
    )

    if folder_path and Path(folder_path).exists():
        folder = Path(folder_path)
        audio_files = [f for f in folder.glob("*") if f.suffix.lower() in SUPPORTED_EXTENSIONS]
        
        if audio_files:
            st.success(f"✅ Found {len(audio_files)} audio files:")
            with st.expander("Click to see file list"):
                for file in audio_files[:10]:  # Show first 10 files
                    st.text(f"• {file.name}")
                if len(audio_files) > 10:
                    st.text(f"... and {len(audio_files) - 10} more files")
        else:
            st.warning("⚠️ No audio files found in this folder")
            st.info("Looking for: .mp3, .wav, .flac, .ogg files")
    elif folder_path:
        st.error(f"❌ Folder not found: {folder_path}")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Analysis Options")
        bpm_analysis = st.checkbox("Calculate BPM")
        features_analysis = st.checkbox("Extract Features")
        plot_analysis = st.checkbox("Show Plots")
        mfcc_analysis = st.checkbox("MFCC Analysis")

    with col2:
        st.subheader("Advanced Options")
        chroma_analysis = st.checkbox("Chroma Analysis")
        spectrogram_analysis = st.checkbox("Spectrogram")
        save_to_db = st.checkbox("Save to Database")

    # CSV output options
    st.subheader("Output Options")
    save_csv = st.checkbox("Save BPM to CSV")
    if save_csv:
        csv_filename = st.text_input("CSV Filename", value="bpm_results.csv")

    if st.button("Start Analysis", type="primary"):
        if not folder_path:
            st.error("Please enter a folder path")
        elif not Path(folder_path).exists():
            st.error(f"Folder not found: {folder_path}")
        else:
            with st.spinner("Analyzing audio files..."):
                results_container = st.container()

                # BPM analysis
                if bpm_analysis:
                    st.info("🎵 Calculating BPM...")
                    results = discover_audio_files(folder_path)

                    if results:
                        df = pd.DataFrame(results, columns=["Filename", "BPM"])
                        st.dataframe(df)

                        if save_csv and csv_filename:
                            # Save CSV
                            import argparse

                            args = argparse.Namespace()
                            args.log = csv_filename
                            csv_writing(args, results)
                            st.success(f"BPM results saved to {csv_filename}")

                # Feature analysis
                if any(
                    [
                        features_analysis,
                        mfcc_analysis,
                        chroma_analysis,
                        spectrogram_analysis,
                        save_to_db,
                    ]
                ):
                    st.info("📊 Analyzing audio features...")

                    folder = Path(folder_path)
                    audio_files = [
                        f
                        for f in folder.glob("*")
                        if f.suffix.lower() in SUPPORTED_EXTENSIONS
                    ]

                    progress_bar = st.progress(0)
                    for i, file in enumerate(audio_files):
                        st.text(f"Processing: {file.name}")

                        audio_file_checker(
                            str(file),
                            plot=plot_analysis,
                            mfcc=mfcc_analysis,
                            chroma=chroma_analysis,
                            spectrogram=spectrogram_analysis,
                            save_db=save_to_db,
                        )

                        progress_bar.progress((i + 1) / len(audio_files))

                st.success("✅ Analysis complete!")

with tab2:
    st.header("Audio Conversion")

    # Input folder
    convert_input = st.text_input(
        "Input Folder",
        placeholder="Enter path to audio folder",
        key="convert_input",
    )

    col1, col2 = st.columns(2)

    with col1:
        target_format = st.selectbox(
            "Target Format", ["wav", "mp3", "flac", "ogg"]
        )

    with col2:
        output_dir = st.text_input("Output Directory", value="converted_audio")

    if st.button("Start Conversion", type="primary"):
        if not convert_input:
            st.error("Please enter an input folder path")
        elif not Path(convert_input).exists():
            st.error(f"Folder not found: {convert_input}")
        else:
            with st.spinner(f"Converting audio files to {target_format}..."):
                folder_path = Path(convert_input)
                output_path = Path(output_dir)
                output_path.mkdir(exist_ok=True)

                audio_files = [
                    f
                    for f in folder_path.glob("*")
                    if f.suffix.lower() in SUPPORTED_EXTENSIONS
                ]

                if audio_files:
                    progress_bar = st.progress(0)
                    for i, file in enumerate(audio_files):
                        st.text(f"Converting: {file.name}")
                        convert_audio(
                            str(file), str(output_path), target_format
                        )
                        progress_bar.progress((i + 1) / len(audio_files))

                    st.success("✅ Conversion complete!")
                else:
                    st.warning("No audio files found in the specified folder")

with tab3:
    st.header("Database Management")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("View Database"):
            setup_database()

            # Capture database output
            import sqlite3

            conn = sqlite3.connect("audio_library.db")
            df = pd.read_sql_query(
                "SELECT file_name, sample_rate, duration_seconds FROM audio_files",
                conn,
            )
            conn.close()

            if not df.empty:
                st.dataframe(df)
            else:
                st.info("Database is empty")

    with col2:
        if st.button("Filter Loops (>3s)"):
            setup_database()

            import sqlite3

            conn = sqlite3.connect("audio_library.db")
            df = pd.read_sql_query(
                "SELECT file_name, sample_rate, duration_seconds FROM audio_files WHERE duration_seconds > 3.0 ORDER BY duration_seconds DESC",
                conn,
            )
            conn.close()

            if not df.empty:
                st.dataframe(df)
            else:
                st.info("No files longer than 3 seconds found")

    with col3:
        export_filename = st.text_input(
            "Export Filename", value="audio_library.csv"
        )
        if st.button("Export to CSV"):
            setup_database()
            export_to_csv(export_filename)
            st.success(f"Database exported to {export_filename}")

with tab4:
    st.header("Batch Processing")

    # Input folder
    batch_input = st.text_input(
        "Input Folder",
        placeholder="Enter path to audio library",
        key="batch_input",
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Options")
        recursive = st.checkbox("Process Recursively")
        batch_bpm = st.checkbox("Calculate BPM", key="batch_bpm")

    with col2:
        st.subheader("Output")
        batch_save_db = st.checkbox("Save to Database", key="batch_save_db")

    if st.button("Start Batch Processing", type="primary"):
        if not batch_input:
            st.error("Please enter an input folder path")
        elif not Path(batch_input).exists():
            st.error(f"Folder not found: {batch_input}")
        else:
            with st.spinner("Processing audio library..."):
                folder_path = Path(batch_input)

                # Find audio files
                if recursive:
                    audio_files = []
                    for ext in SUPPORTED_EXTENSIONS:
                        audio_files.extend(folder_path.rglob(f"*{ext}"))
                else:
                    audio_files = [
                        f
                        for f in folder_path.iterdir()
                        if f.suffix.lower() in SUPPORTED_EXTENSIONS
                    ]

                st.info(f"🎵 Found {len(audio_files)} audio files")

                if batch_save_db:
                    setup_database()

                if audio_files:
                    progress_bar = st.progress(0)
                    results = []

                    for i, file in enumerate(audio_files):
                        st.text(
                            f"[{i+1}/{len(audio_files)}] Processing: {file.name}"
                        )

                        if batch_bpm:
                            bpm = calculate_bpm(str(file))
                            if bpm:
                                results.append({"File": file.name, "BPM": bpm})

                        if batch_save_db:
                            audio_file_checker(str(file), save_db=True)

                        progress_bar.progress((i + 1) / len(audio_files))

                    if results:
                        st.subheader("BPM Results")
                        df = pd.DataFrame(results)
                        st.dataframe(df)

                    st.success("✅ Batch processing complete!")
                else:
                    st.warning("No audio files found")

# Sidebar with info
st.sidebar.header("About")
st.sidebar.info(
    """
This is a GUI for the Audio Toolkit CLI application.

**Features:**
- 🔍 Audio analysis (BPM, features, plots)
- 🔄 Format conversion
- 💾 Database management
- 📦 Batch processing

**Supported formats:**
MP3, WAV, FLAC, OGG
"""
)

st.sidebar.header("Instructions")
st.sidebar.markdown(
    """
1. **Analyze**: Select a folder and choose analysis options
2. **Convert**: Convert audio files between formats
3. **Database**: View and manage your audio library database
4. **Batch**: Process large audio libraries efficiently
"""
)
