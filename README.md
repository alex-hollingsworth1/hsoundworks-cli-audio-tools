# hsoundworks_cli

**hsoundworks_cli** is a Python command-line toolkit for working with audio files. It includes tools for audio inspection, visualisation, and batch conversion — perfect for musicians, producers, audio devs, and machine learning workflows.

---

## Features

- `hscheck`: Audio file inspector
  - View sample rate, duration, and estimated tempo (BPM)
  - Generate waveform, spectrogram, MFCC, and Chroma visualisations
  - Save plots as `.png` files to an `outputs/` folder

- `hsconvert`: Batch audio converter
  - Convert between `.wav`, `.mp3`, `.flac`, `.ogg`, etc.
  - Choose your output format and directory
  - Normalize filenames and prepare datasets

- `hsbpm`: BPM analyser and CSV logger
  - Estimate the tempo (BPM) of audio files using librosa
  - Print BPM results to the terminal
  - Optionally save results to a .csv log file with --log
  - Planned: Organize files into tempo-based folders with --sort

---

## Installation

Clone the repo and install in editable mode:

```bash
git clone https://github.com/alex-hollingsworth1/hsoundworks_cli.git
cd hsoundworks_cli
pip install -e .
```
