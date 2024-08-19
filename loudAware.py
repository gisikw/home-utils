import pyaudio
import numpy as np
import sys

def find_device_index(p, device_name):
    """Find the index of the device with the given name."""
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if device_name.lower() in info['name'].lower():
            return i
    return None

def get_peak_amplitude(data):
    """ Calculate the peak amplitude of the signal """
    peak = np.max(np.abs(data))
    db = 20 * np.log10(peak) if peak > 0 else -np.inf
    return db

def get_rms_decibel(data, rate):
    """ Calculate the RMS value and convert it to dB """
    rms = np.sqrt(np.mean(np.square(data)))
    
    # To avoid log of zero and handle small values
    if rms > 0:
        db = 20 * np.log10(rms)
    else:
        db = -np.inf
    
    db = max(0, db)  # Ensuring no negative values for dB
    
    return db

def render_meter(db):
    """ Render an ASCII meter with composite colors and bounded by [ and ], with proper padding """
    max_db = 100  # Adjust according to your microphone sensitivity

    # Handle the case where db is -inf
    if db == -float('inf'):
        db = 0  # Consider this as the minimum dB value (silence)

    normalized = max(0, min(int(db / max_db * 50), 50))  # Normalize to a scale of 0 to 50

    # Define the thresholds for green, yellow, and red sections
    green_threshold = 15  # First 15 characters in green
    yellow_threshold = 35  # Next 20 characters in yellow (total of 35)
    red_threshold = 50  # Final 15 characters in red

    # Construct the meter bar
    green_part = min(normalized, green_threshold)
    yellow_part = max(0, min(normalized - green_threshold, yellow_threshold - green_threshold))
    red_part = max(0, normalized - yellow_threshold)

    meter = (
        "[" +
        "\033[92m" + "#" * green_part +  # Green part
        "\033[93m" + "#" * yellow_part +  # Yellow part
        "\033[91m" + "#" * red_part +  # Red part
        "\033[0m" +  # Reset color
        " " * (50 - normalized) +  # Padding to keep the meter width consistent
        "]"
    )

    return f"dB: {db:.2f} | {meter}"


def main():
    RATE = 44100
    CHUNK = int(RATE / 10)  # 100ms
    p = pyaudio.PyAudio()

    desired_device_name = "Logi 4K Stream Edition"
    input_device_index = find_device_index(p, desired_device_name)

    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=RATE,
                    input=True,
                    input_device_index=input_device_index,
                    frames_per_buffer=CHUNK)

    try:
        # Hide the cursor
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

        while True:
            data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
            db = get_peak_amplitude(data)
            # db = get_rms_decibel(data, RATE)
            
            meter = render_meter(db)
            sys.stdout.write("\r" + meter)
            sys.stdout.flush()

    except KeyboardInterrupt:
        pass

    finally:
        # Show the cursor again before exiting
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main()

