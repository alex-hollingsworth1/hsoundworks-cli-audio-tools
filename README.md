# Audio Toolkit

**Audio Toolkit** is a comprehensive Python application for audio analysis, conversion, and batch processing. It provides both a powerful command-line interface and an intuitive web-based GUI built with Streamlit — perfect for musicians, producers, audio engineers, and machine learning workflows.

---

## Features

### Audio Analysis
- **BPM Calculation**: Estimate the tempo of audio files using librosa beat tracking
  - Calculate BPM for individual files or batch process entire libraries
  - Save results to CSV for analysis and organization
  - Support for MP3, WAV, FLAC, and OGG formats

- **Audio Feature Extraction**: Comprehensive audio analysis with structured results
  - Extract MFCC (Mel-frequency cepstral coefficients) for timbre analysis
  - Calculate Chroma features for pitch/harmony analysis
  - Generate spectrograms for frequency visualization
  - Waveform visualization for audio inspection
  - All results displayed as structured DataFrames in the GUI
  - View sample rate, duration, and file metadata

### Audio Conversion
- **Batch Format Conversion**: Convert between multiple audio formats
  - Supported formats: `.wav`, `.mp3`, `.flac`, `.ogg`
  - Process entire folders or individual files
  - Customizable output directory

### Database Management
- **Audio Library Database**: SQLite-based audio metadata storage
  - Automatically save file metadata during analysis
  - Query and filter audio files by duration, sample rate, and more
  - Export database to CSV for external analysis
  - Organize and manage large audio collections

### Batch Processing
- **Efficient Bulk Operations**: Process large audio libraries
  - Recursive folder scanning for deep directory structures
  - Simultaneous BPM calculation and feature extraction
  - Progress tracking with real-time status updates
  - Database integration for long-term organization

---

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

Clone the repository and install in editable mode:

```bash
git clone https://github.com/alex-hollingsworth1/hsoundworks-cli-audio-tools.git
cd hsoundworks-cli-toolkit
pip install -e .
```

---

## Usage

### Command-Line Interface

The CLI provides a unified interface with multiple subcommands:

```bash
# Analyze audio files for BPM and features
python cli.py analyze ~/music --bpm --features --save-db

# Convert audio files between formats
python cli.py convert ~/samples --format mp3 --output-dir converted_audio

# View or manage the database
python cli.py db --view
python cli.py db --export-csv results.csv

# Batch process an entire audio library
python cli.py batch ~/library --recursive --bpm --save-db
```

### Web-Based GUI (Streamlit)

Launch the interactive web interface:

```bash
streamlit run streamlit_gui.py
```

The GUI provides a user-friendly interface with four main tabs:

1. **Analyze Tab**
   - Browse and select audio folders
   - Choose analysis options (BPM, features, visualizations)
   - Enable MFCC, Chroma, and Spectrogram analysis
   - Save to database or export results
   - View analysis results in interactive tables

2. **Convert Tab**
   - Select input folder and target format
   - Specify output directory
   - Batch convert multiple files with progress tracking

3. **Database Tab**
   - View complete audio library database
   - Filter files by duration (e.g., loops longer than 3 seconds)
   - Export database to CSV

4. **Batch Tab**
   - Process large audio libraries efficiently
   - Option for recursive folder scanning
   - Simultaneous BPM and database operations
   - Real-time progress tracking

---

## Supported Audio Formats

- MP3 (`.mp3`)
- WAV (`.wav`)
- FLAC (`.flac`)
- OGG Vorbis (`.ogg`)

---

## Architecture

### Module Structure

```
hsoundworks_cli/
├── analyzers/
│   ├── bpm.py           # BPM calculation using librosa beat tracking
│   └── features.py      # Audio feature extraction (MFCC, Chroma, Spectrograms)
├── converters/
│   └── format.py        # Audio format conversion
├── database/
│   └── manager.py       # SQLite database operations
├── cli.py               # Command-line interface with subcommands
└── streamlit_gui.py     # Web-based GUI using Streamlit
```

### Key Dependencies

- **librosa**: Audio analysis and feature extraction
- **matplotlib**: Visualization and plotting
- **soundfile**: Audio file I/O operations
- **numpy**: Numerical computing
- **streamlit**: Web GUI framework
- **pandas**: Data manipulation and display

### Database Schema

SQLite database (`audio_library.db`) structure:

```sql
CREATE TABLE audio_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT NOT NULL,
    sample_rate INTEGER NOT NULL,
    duration_seconds REAL NOT NULL
)
```

---

## Configuration

### Constants and Configuration

Key configuration values can be found in individual modules:

- **BPM Analysis Range**: 0-300 BPM (configurable in `analyzers/bpm.py`)
- **MFCC Coefficients**: 13 (configurable in `analyzers/features.py`)
- **Default Output Directory**: `converted_audio` (configurable in `cli.py`)
- **Database File**: `audio_library.db` (configurable in `database/manager.py`)
- **Supported Formats**: MP3, WAV, FLAC, OGG (defined in modules)

---

## Features Overview

### Analysis Results

When running analysis, results are returned as structured data:

- **Filename**: Name of the analyzed audio file
- **Sample Rate**: Audio sample rate in Hz
- **Duration**: Audio duration in seconds
- **MFCC Calculated**: Whether MFCC analysis was successful
- **Chroma Calculated**: Whether Chroma analysis was successful
- **Spectrogram Calculated**: Whether Spectrogram analysis was successful
- **Saved to Database**: Whether file metadata was saved

Results are displayed as interactive DataFrames in the Streamlit GUI for easy viewing and analysis.

---

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss your proposed changes.

---

## License

This project is part of the hsoundworks audio toolkit suite.

---

## Support

For issues, questions, or feature requests, please visit the [GitHub repository](https://github.com/alex-hollingsworth1/hsoundworks-cli-audio-tools).
