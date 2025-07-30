# voice.py
import os
import torch
import soundfile as sf
from transformers import pipeline

# classifier = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")

# def analyze_emotion_from_audio(audio_data):
#     file_path = "temp.wav"
#     with open(file_path, "wb") as f:
#         f.write(audio_data.get_wav_data())

#     # Transcribe
#     speech_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-base")
#     result = speech_pipeline(file_path)
#     text = result['text'].strip()
#     print(f"Transcribed text: {text}")

#     if text:
#         emotion_result = classifier(text)
#         print(f"Emotion: {emotion_result}")
#     else:
#         print("⚠️ No transcribable speech detected.")

#     os.remove(file_path)
#     return text
def analyze_emotion_from_audio(audio_data):
    import os
    from transformers import pipeline

    classifier = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion", top_k=1)
    speech_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-base", generate_kwargs={"language": "en"})

    file_path = "temp.wav"
    with open(file_path, "wb") as f:
        f.write(audio_data.get_wav_data())

    result = speech_pipeline(file_path)
    text = result['text'].strip()
    print(f"Transcribed text: {text}")

    top_emotion = "neutral"  # default fallback
    if text:
        emotion_result = classifier(text)
        print(f"[DEBUG] Raw emotion_result: {emotion_result}")

        # Normalize output
    if isinstance(emotion_result, list):
    # Handle nested list from top_k > 1 or default config
        if isinstance(emotion_result[0], list) and len(emotion_result[0]) > 0:
            top_emotion = emotion_result[0][0].get("label", "neutral")
        elif isinstance(emotion_result[0], dict):
            top_emotion = emotion_result[0].get("label", "neutral")


        print(f"Detected Emotion: {top_emotion}")

    os.remove(file_path)
    return text, top_emotion
