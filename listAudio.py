import pyaudio

def list_audio_devices():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        print(f"Device {i}: {info['name']}")
        print(f"    Manufacturer: {info.get('manufacturer', 'Unknown')}")
        print(f"    Product Name: {info.get('productName', 'Unknown')}")
        print(f"    Max Input Channels: {info['maxInputChannels']}")
        print(f"    Default Sample Rate: {info['defaultSampleRate']}")
    p.terminate()

if __name__ == "__main__":
    list_audio_devices()

