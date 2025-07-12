"""Audio Format Conversion Module"""

import os
import librosa
import soundfile as sf


def convert_audio(file_path, output_dir, target_format="wav"):
    """Convert audio file to target format

    Args:
        file_path: Path to input audio file
        output_dir: Directory to save converted file
        target_format: Target audio format (default: wav)
    """
    # Load the audio file
    y, sr = librosa.load(file_path, sr=None)

    # Get filename without extension
    filename = os.path.splitext(os.path.basename(file_path))[0]

    # Create output path
    output_path = os.path.join(output_dir, f"{filename}.{target_format}")

    # Write the converted file
    sf.write(output_path, y, sr)
    print(f"✅ Converted: {filename} → {output_path}")
