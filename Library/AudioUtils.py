import numpy as np
from scipy.io.wavfile import write
from PIL import Image, PngImagePlugin


def write_metadata(filename, metadata):
    with Image.open(filename) as img:
        meta = PngImagePlugin.PngInfo()
        for key, value in metadata.items(): meta.add_text(key, value)
        img.save(filename, "PNG", pnginfo=meta)


def read_metadata(filename):
    with Image.open(filename) as img:
        return img.info


def array2wav(filename, array):
    # Ensure the array is in the correct format
    sample_rate = 400000
    if not isinstance(array, np.ndarray):
        raise ValueError("Input data must be a numpy array.")
    # Check if the array is floating-point and normalize to 16-bit PCM range
    if np.issubdtype(array.dtype, np.floating):
        array = np.int16(array / np.max(np.abs(array)) * 32767)
    # Ensure the filename ends with '.wav'
    if not filename.lower().endswith('.wav'):
        filename += '.wav'
    # Save the array as a WAV file
    write(filename, sample_rate, array)
    print(f"WAV file saved to {filename}")

