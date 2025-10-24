"""Audio Features Analysis Module"""

import os
import datetime
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt

from database.manager import save_to_database, setup_database

# Audio analysis constants
MFCC_COEFFICIENTS = 13
FIGURE_WIDTH = 10
FIGURE_HEIGHT = 4
NUMPY_PRECISION = 2

# Set numpy print options
np.set_printoptions(precision=NUMPY_PRECISION, suppress=True)


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
    graphs. Returns a dictionary with analysis results."""

    # Initialize results dictionary
    results = {
        "filename": os.path.basename(file_path),
        "sample_rate": None,
        "duration_seconds": None,
        "mfcc_calculated": False,
        "chroma_calculated": False,
        "spectrogram_calculated": False,
        "saved_to_db": False,
    }

    # Validate file existence
    if not os.path.isfile(file_path):
        print(f"Error: File does not exist: {file_path}")
        return None

    # Check file permissions
    if not os.access(file_path, os.R_OK):
        print(f"Error: No read permission for file: {file_path}")
        return None

    try:
        # Load the audio
        y, sr = librosa.load(file_path, sr=None, mono=False)

        if y is None or (hasattr(y, "size") and y.size == 0):
            print(f"Error: Could not load audio data from file: {file_path}")
            return None

    except librosa.LibrosaError as e:
        print(f"Librosa error loading {file_path}: {e}")
        return None
    except FileNotFoundError:
        print(f"Error: File not found during loading: {file_path}")
        return None
    except (ValueError, TypeError) as e:
        print(f"Data validation error loading {file_path}: {e}")
        return None
    except MemoryError:
        print(f"Memory error: File too large to process: {file_path}")
        return None

    try:
        output_dir = os.path.join(os.getcwd(), "outputs")
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        print(f"Error creating output directory: {e}")
        return None

    try:
        # Work out the duration
        duration = librosa.get_duration(y=y, sr=sr)

        if duration <= 0:
            print(
                f"Error: Invalid duration ({duration}s) for file: {file_path}"
            )
            return None

        # If stereo, average the channels to make it mono
        if y.ndim > 1:
            y = np.mean(y, axis=0)

        # Populate results dictionary
        results["sample_rate"] = sr
        results["duration_seconds"] = float(duration)

        # Print core info
        print(f"\nFile: {os.path.basename(file_path)}")
        print(f"Sample Rate: {sr} Hz")
        print(f"Duration: {datetime.timedelta(seconds=round(duration))}")

    except (ValueError, TypeError) as e:
        print(f"Data validation error processing audio properties: {e}")
        return None
    except MemoryError:
        print("Memory error: Audio file too large to process")
        return None

    # Save to database
    if save_db:
        try:
            # Import from database.manager to avoid circular imports
            setup_database()  # Ensure database exists
            save_to_database(file_path, sr, duration)
            results["saved_to_db"] = True
        except (ValueError, TypeError) as e:
            print(f"Data validation error saving to database: {e}")
            # Continue execution even if database save fails

    if plot:
        try:
            plot_waveform(y, sr, title=os.path.basename(file_path))
        except (ValueError, TypeError, RuntimeError) as e:
            print(f"Error creating waveform plot: {e}")

    if mfcc:
        try:
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=MFCC_COEFFICIENTS)
            results["mfcc_calculated"] = True

            if plot:
                filename = os.path.splitext(os.path.basename(file_path))[0]
                save_path = os.path.join(output_dir, f"{filename}_mfcc.png")
                plot_features(
                    mfccs,
                    title="MFCC",
                    ylabel="MFCC Coefficients",
                    save_path=save_path,
                )
        except librosa.LibrosaError as e:
            print(f"Librosa error calculating MFCC: {e}")
        except (ValueError, TypeError, RuntimeError) as e:
            print(f"Error processing MFCC features: {e}")
        except MemoryError:
            print(
                "Memory error: Cannot compute MFCC features - file too large"
            )

    if chroma:
        try:
            chroma_feat = librosa.feature.chroma_stft(y=y, sr=sr)
            results["chroma_calculated"] = True

            if plot:
                filename = os.path.splitext(os.path.basename(file_path))[0]
                save_path = os.path.join(output_dir, f"{filename}_chroma.png")

                plot_features(
                    chroma_feat,
                    title="Chroma",
                    ylabel="Pitch Class",
                    save_path=save_path,
                )
        except librosa.LibrosaError as e:
            print(f"Librosa error calculating Chroma: {e}")
        except (ValueError, TypeError, RuntimeError) as e:
            print(f"Error processing Chroma features: {e}")
        except MemoryError:
            print(
                "Memory error: Cannot compute Chroma features - file too large"
            )

    if spectrogram:
        try:
            spectro_feat = librosa.stft(y=y)
            s_db = librosa.amplitude_to_db(np.abs(spectro_feat), ref=np.max)
            results["spectrogram_calculated"] = True

            if plot:
                filename = os.path.splitext(os.path.basename(file_path))[0]
                save_path = os.path.join(
                    output_dir, f"{filename}_spectrogram.png"
                )

                plot_features(
                    s_db,
                    title="Spectrogram",
                    ylabel="Frequency",
                    save_path=save_path,
                )
        except librosa.LibrosaError as e:
            print(f"Librosa error calculating Spectrogram: {e}")
        except (ValueError, TypeError, RuntimeError) as e:
            print(f"Error processing Spectrogram features: {e}")
        except MemoryError:
            print("Memory error: Cannot compute Spectrogram - file too large")

    return results


def plot_waveform(y, sr, title="Waveform"):
    """Function that draws waveform if user types --plot"""
    try:
        plt.figure(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        librosa.display.waveshow(y, sr=sr)
        plt.title(title)
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.tight_layout()
        plt.show()
    except (ValueError, TypeError, RuntimeError) as e:
        print(f"Error creating waveform plot '{title}': {e}")
        plt.close()
    except MemoryError:
        print(f"Memory error creating waveform plot '{title}': File too large")
        plt.close()


def plot_features(
    feature, title="Feature", ylabel="Feature Coefficients", save_path=None
):
    """Plots MFCC and Chroma graphs, and then saves them as a PNG"""
    try:
        if feature is None or feature.size == 0:
            print(f"Error: No feature data to plot for '{title}'")
            return False

        plt.figure(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        plt.imshow(feature, aspect="auto", origin="lower", cmap="magma")
        plt.title(title)
        plt.xlabel("Time (frames)")
        plt.ylabel(ylabel)
        plt.colorbar(format="%+2.0f dB")
        plt.tight_layout()

        if save_path:
            try:
                # Ensure output directory exists
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                plt.savefig(save_path)
                print(f"Saved plot to: {save_path}")
            except OSError as e:
                print(f"Error saving plot to {save_path}: {e}")
                return False
        else:
            plt.show()

        plt.close()
        return True

    except (ValueError, TypeError, RuntimeError) as e:
        print(f"Error creating feature plot '{title}': {e}")
        plt.close()
        return False
    except MemoryError:
        print(f"Memory error creating feature plot '{title}': Data too large")
        plt.close()
        return False
