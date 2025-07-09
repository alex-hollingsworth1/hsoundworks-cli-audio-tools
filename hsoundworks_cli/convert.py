"""Audio batch converter"""

import os
import argparse
import librosa
import soundfile as sf


def convert_audio(file_path, output_dir, target_format="wav"):
    """Convert audio function"""
    y, sr = librosa.load(file_path, sr=None)

    filename = os.path.splitext(os.path.basename(file_path))[0]
    output_path = os.path.join(output_dir, f"{filename}.{target_format}")

    sf.write(output_path, y, sr)
    print(f"✅ Converted: {filename} → {output_path}")


def main():
    """Main functino for audio batch converter"""
    parser = argparse.ArgumentParser(description="Batch audio file converter.")
    parser.add_argument("folder_path", type=str,
                        help="Path to folder with audio files.")
    parser.add_argument("--format", type=str, default="wav",
                        help="Target audio format (default: wav)")

    args = parser.parse_args()
    folder_path = args.folder_path
    target_format = args.format

    output_dir = os.path.join(os.getcwd(), "converted_audio")
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".mp3", ".wav", ".flac", ".ogg")):
            full_path = os.path.join(folder_path, filename)
            convert_audio(full_path, output_dir, target_format)

    print("Folder path:", args.folder_path)
    print("Target format:", args.format)


if __name__ == "__main__":
    main()
