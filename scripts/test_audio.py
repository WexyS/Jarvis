import sounddevice as sd
print("=== Sistem Audio Bilgisi ===")
devs = sd.query_devices()
default_in = sd.query_devices(kind="input")
print(f"Varsayilan Giris: {default_in['name']}")
print(f"Oran: {default_in['default_samplerate']} Hz")
print(f"Kanal: {default_in['max_input_channels']}")

print("\nTest: 16kHz acilabilir mi?")
try:
    stream = sd.InputStream(samplerate=16000, channels=default_in['max_input_channels'], dtype='int16', blocksize=1024)
    stream.start()
    stream.stop()
    stream.close()
    print("✅ 16kHz ACILDI")
except Exception as e:
    print(f"❌ 16kHz acilmiyor: {e}")

print("\nTest: 44.1kHz acilabilir mi?")
try:
    stream = sd.InputStream(samplerate=44100, channels=default_in['max_input_channels'], dtype='int16', blocksize=1024)
    stream.start()
    stream.stop()
    stream.close()
    print("✅ 44.1kHz ACILDI")
except Exception as e:
    print(f"❌ 44.1kHz acilmiyor: {e}")

print("\nTum giris cihazlari:")
for i, d in enumerate(devs):
    if d.get('max_input_channels', 0) > 0:
        sr = d.get("default_samplerate", "?")
        ch = d["max_input_channels"]
        print(f"  [{i}] {d['name']} | SR: {sr} Hz | Ch: {ch}")
