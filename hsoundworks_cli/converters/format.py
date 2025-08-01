"""Audio Format Conversion Module"""

import os
import librosa
import soundfile as sf
from pathlib import Path


def convert_audio(file_path, output_dir, target_format="wav"):
    """Convert audio file to target format

    Args:
        file_path: Path to input audio file
        output_dir: Directory to save converted file
        target_format: Target audio format (default: wav)

    Returns:
        bool: True if conversion successful, False otherwise
    """
    # Supported formats (common ones for soundfile)
    SUPPORTED_FORMATS = {"wav", "flac", "ogg", "mp3", "aiff", "m4a"}

    # Validate input parameters
    if not file_path:
        print("Error: File path cannot be empty")
        return False

    if not output_dir:
        print("Error: Output directory cannot be empty")
        return False

    if not target_format:
        print("Error: Target format cannot be empty")
        return False

    # Validate target format
    target_format = target_format.lower().strip(".")
    if target_format not in SUPPORTED_FORMATS:
        print(
            f"Error: Unsupported target format '{target_format}'. "
            f"Supported formats: {', '.join(SUPPORTED_FORMATS)}"
        )
        return False

    # Validate input file
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        print(f"Error: Input file does not exist: {file_path}")
        return False

    if not file_path_obj.is_file():
        print(f"Error: Input path is not a file: {file_path}")
        return False

    # Check file permissions
    if not os.access(file_path, os.R_OK):
        print(f"Error: No read permission for file: {file_path}")
        return False

    # Validate and create output directory
    output_dir_obj = Path(output_dir)
    try:
        output_dir_obj.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Error creating output directory {output_dir}: {e}")
        return False

    # Check write permission for output directory
    if not os.access(output_dir, os.W_OK):
        print(f"Error: No write permission for output directory: {output_dir}")
        return False

    try:
        # Load the audio file
        y, sr = librosa.load(file_path, sr=None)

        if y is None or y.size == 0:
            print(f"Error: Could not load audio data from: {file_path}")
            return False

        if sr is None or sr <= 0:
            print(f"Error: Invalid sample rate from file: {file_path}")
            return False

        # Get filename without extension
        filename = file_path_obj.stem

        # Create output path
        output_path = output_dir_obj / f"{filename}.{target_format}"

        # Check if output file already exists and warn user
        if output_path.exists():
            print(
                f"Warning: Output file already exists and will be "
                f"overwritten: {output_path}"
            )

        # Write the converted file
        sf.write(str(output_path), y, sr)

        # Verify the file was written successfully
        if not output_path.exists() or output_path.stat().st_size == 0:
            print(f"Error: Failed to write output file: {output_path}")
            return False

        print(f"✅ Converted: {filename} → {output_path}")
        return True

    except librosa.LibrosaError as e:
        print(f"Librosa error loading {file_path}: {e}")
        return False
    except sf.SoundFileError as e:
        print(f"SoundFile error writing {target_format}: {e}")
        return False
    except FileNotFoundError as e:
        print(f"File not found during conversion: {e}")
        return False
    except PermissionError as e:
        print(f"Permission error during conversion: {e}")
        return False
    except OSError as e:
        print(f"OS error during conversion: {e}")
        return False
    except (ValueError, TypeError) as e:
        print(f"Data validation error during conversion: {e}")
        return False
    except MemoryError:
        print(f"Memory error: File too large to process: {file_path}")
        return False
