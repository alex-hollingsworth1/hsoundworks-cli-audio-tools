"""Audio Features Analysis Module"""

import os
import datetime
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt

from database.manager import save_to_database, setup_database

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

        setup_database()  # Ensure database exists
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
