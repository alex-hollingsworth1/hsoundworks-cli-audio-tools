# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Installation
```bash
# Install in editable mode from project root
pip install -e .
```

### Running the CLI
The main entry point is `cli.py` which provides a unified command-line interface:
```bash
# Analyze audio files for BPM and features
python cli.py analyze ~/music --bpm --features --save-db

# Convert audio files between formats
python cli.py convert ~/samples --format mp3 --output-dir converted_audio

# Database operations
python cli.py db --view
python cli.py db --export-csv results.csv

# Batch processing
python cli.py batch ~/library --recursive --bpm --save-db
```

### Running the GUI
```bash
# Launch Streamlit web interface
streamlit run streamlit_gui.py
```

### Linting
The project uses pylint with custom configuration in `.vscode/settings.json`:
```bash
pylint hsoundworks_cli/
```

## Architecture

### Module Structure
- **analyzers/**: Audio analysis functionality
  - `bpm.py`: BPM calculation using librosa beat tracking
  - `features.py`: Audio feature extraction (MFCC, chroma, spectrograms)
  
- **converters/**: Audio format conversion
  - `format.py`: Audio format conversion using librosa and soundfile
  
- **database/**: SQLite database management  
  - `manager.py`: Database operations for storing audio metadata
  
- **cli.py**: Unified command-line interface with subcommands
- **streamlit_gui.py**: Web-based GUI using Streamlit

### Key Dependencies
- `librosa`: Core audio analysis library
- `matplotlib`: Plotting and visualization
- `soundfile`: Audio I/O operations
- `numpy`: Numerical operations
- `streamlit`: Web GUI framework

### Database Schema
SQLite database (`audio_library.db`) with table:
```sql
CREATE TABLE audio_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT NOT NULL,
    sample_rate INTEGER NOT NULL,
    duration_seconds REAL NOT NULL
)
```

### Supported Audio Formats
- `.mp3`, `.wav`, `.flac`, `.ogg`
- Constants defined in individual modules (AUDIO_EXTENSIONS, SUPPORTED_EXTENSIONS)

### Constants and Configuration
- BPM analysis range: 0-300 BPM (MIN_BPM, MAX_BPM in bpm.py:12-13)
- MFCC coefficients: 13 (MFCC_COEFFICIENTS in features.py:13)
- Default output directory: "converted_audio" (DEFAULT_OUTPUT_DIR in cli.py:22)
- Database file: "audio_library.db" (DATABASE_NAME in manager.py:8)

## Entry Points
The setup.py defines console scripts that may be outdated - the current unified CLI approach uses `cli.py` directly.