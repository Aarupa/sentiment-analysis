import os, time, wave
import numpy as np
import pygame
import sounddevice as sd
from gtts import gTTS
from transformers import pipeline

# Text-to-Speech
def speak(text):
    tts = gTTS(text, lang='en')
    tts.save("speak.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load("speak.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy(): time.sleep(0.1)
    pygame.mixer.quit()
    os.remove("speak.mp3")

# Record microphone audio and save as WAV
def record_audio(filename="speech.wav", duration=5, rate=44100):
    print("🎙️ Recording...")
    data = sd.rec(int(duration * rate), samplerate=rate, channels=1, dtype='int16')
    sd.wait()
    with wave.open(filename, 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(rate)
        f.writeframes(data.tobytes())
    return filename

# Speech-to-Text using Whisper
def transcribe(audio_file):
    asr = pipeline("automatic-speech-recognition", model="openai/whisper-base", generate_kwargs={"language": "en"})
    return asr(audio_file)['text'].strip()

# Demo
if __name__ == "__main__":
    speak("Please say something after the beep.")
    file = record_audio()
    text = transcribe(file)
    print("📝 You said:", text)
    speak(f"You said: {text}")
