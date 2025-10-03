import os
import sounddevice as sd
import numpy as np
import wave
from transformers import pipeline
from gtts import gTTS
import pygame
import time

def text_to_speech(text):
    """Convert text to speech and play it"""
    tts = gTTS(text=text, lang='en')
    tts.save("temp_audio.mp3")
    
    pygame.mixer.init()
    pygame.mixer.music.load("temp_audio.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    pygame.mixer.quit()
    os.remove("temp_audio.mp3")

def record_audio(duration=5, sample_rate=44100):
    """Record audio from microphone"""
    print(f"Recording for {duration} seconds...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished
    return audio_data

def save_audio(audio_data, filename="temp.wav", sample_rate=44100):
    """Save audio data to WAV file"""
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())
    return filename

def analyze_emotion_from_audio(audio_path):
    """Analyze emotion from audio file path using Whisper + Emotion classifier"""
    classifier = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion", top_k=1)
    speech_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-base", generate_kwargs={"language": "en"})

    result = speech_pipeline(audio_path)
    text = result['text'].strip()
    print(f"Transcribed text: {text}")

    top_emotion = "neutral"  # fallback
    if text:
        emotion_result = classifier(text)
        print(f"[DEBUG] Raw emotion_result: {emotion_result}")

        if isinstance(emotion_result, list):
            if isinstance(emotion_result[0], list) and len(emotion_result[0]) > 0:
                top_emotion = emotion_result[0][0].get("label", "neutral")
            elif isinstance(emotion_result[0], dict):
                top_emotion = emotion_result[0].get("label", "neutral")

        print(f"Detected Emotion: {top_emotion}")

    return text, top_emotion
# Removed erroneous check for undefined 'audio_path'



def get_voice_response(question):
    """Get voice response from user for a question"""
    text_to_speech(question)
    audio_data = record_audio()
    audio_path = save_audio(audio_data)  # This returns 'temp.wav'
    text, emotion = analyze_emotion_from_audio(audio_path)

    
    # Map emotion to score (1-5 for Likert scale)
    emotion_mapping = {
        'anger': 1,
        'disgust': 1,
        'fear': 2,
        'joy': 5,
        'neutral': 3,
        'sadness': 2,
        'surprise': 4
    }
    return emotion_mapping.get(emotion, 3)

def get_text_response(question, scale_info=None):
    """Get text response from user for a question"""
    if scale_info:
        print(f"\n{question}")
        for key, (text, _) in scale_info.items():
            print(f"{key}. {text}")
        while True:
            choice = input("Enter your choice (1-5): ").strip()
            if choice in scale_info:
                return scale_info[choice][1]
            else:
                print("❌ Invalid input. Please enter a number between 1 and 5.")
    else:
        while True:
            answer = input(f"\n{question} (Yes/No): ").strip().lower()
            if answer in ["yes", "y"]:
                return 15
            elif answer in ["no", "n"]:
                return 0
            else:
                print("❌ Invalid input. Please answer Yes or No.")

def readiness_scoring():
    # Ask for interaction mode
    print("Welcome to the Comprehensive Readiness Assessment")
    print("Please choose your preferred interaction mode:")
    print("1. Text-based (all questions will be text)")
    print("2. Voice-based (all questions will be voice)")
    
    while True:
        mode_choice = input("Enter your choice (1 or 2): ").strip()
        if mode_choice in ["1", "2"]:
            voice_mode = mode_choice == "2"
            break
        else:
            print("❌ Invalid input. Please enter 1 or 2.")

    # Likert scale definition
    likert_scale = {
        "1": ("Strongly Disagree", 1),
        "2": ("Disagree", 2),
        "3": ("Neutral", 3),
        "4": ("Agree", 4),
        "5": ("Strongly Agree", 5)
    }
    
    if voice_mode:
        text_to_speech("\n🧠 Welcome to the Comprehensive Readiness Assessment")
        text_to_speech("This assessment evaluates four key areas:")
        text_to_speech("1. Physical Readiness (35 points)")
        text_to_speech("2. Mental Readiness (35 points)")
        text_to_speech("3. Certification Status (15 points)")
        text_to_speech("4. Historical Behavior (15 points)")
        text_to_speech("Total possible score: 100 points")
    else:
        print("\n🧠 Welcome to the Comprehensive Readiness Assessment\n")
        print("👉 This assessment evaluates four key areas:")
        print("1. Physical Readiness (35 points)")
        print("2. Mental Readiness (35 points)")
        print("3. Certification Status (15 points)")
        print("4. Historical Behavior (15 points)\n")
        print("📊 Total possible score: 100 points\n")

    # Physical readiness questions (7 questions x 5 points each = 35 points)
    physical_questions = [
        "1. I feel physically fit and ready to perform my tasks today.",
        "2. I had restful sleep last night and feel refreshed.",
        "3. I am free from any pain, discomfort, or illness at this moment.",
        "4. I feel energetic and physically active.",
        "5. I can perform my physical work without strain or fatigue.",
        "6. My physical condition allows me to work at my full capacity.",
        "7. I have no physical limitations that would affect my work today."
    ]

    # Text-based mental readiness questions (only used if audio not selected)
    mental_questions = [
        "8. I am feeling emotionally balanced and grounded.",
        "9. I am mentally present, focused, and not distracted.",
        "10. I feel emotionally stable and know how to manage my stress.",
        "11. I am well-rested and not experiencing mental fatigue.",
        "12. I recover quickly from emotional or mental setbacks.",
        "13. I feel motivated and engaged with my work.",
        "14. I can maintain concentration for extended periods when needed."
    ]

    # Certification question (15 points)
    certification_question = "15. Have you completed all required certification courses for your current role?"

    # Historical behavior question (15 points)
    behavior_question = "16. Do you have any past incidents of safety violations or concerning behavior?"

    # Physical readiness assessment
    if voice_mode:
        text_to_speech("Physical Readiness Questions 1 to 7")
        physical_score = 0
        for q in physical_questions:
            score = get_voice_response(q)
            physical_score += score * 1.0
        physical_score = (physical_score / 35) * 35  # Scale to 35 points
    else:
        print("\n📝 Physical Readiness Questions (1-7)")
        physical_score = sum(get_text_response(q, likert_scale) for q in physical_questions) * 1.0
        physical_score = (physical_score / 35) * 35

    # Mental readiness assessment
    if voice_mode:
        text_to_speech("Mental Readiness Questions 8 to 14")
        mental_score = 0
        for q in mental_questions:
            score = get_voice_response(q)
            mental_score += score * 1.0
        mental_score = (mental_score / 35) * 35
    else:
        print("\n📝 Mental Readiness Questions (8-14)")
        mental_score = sum(get_text_response(q, likert_scale) for q in mental_questions) * 1.0
        mental_score = (mental_score / 35) * 35

    # Certification status
    if voice_mode:
        cert_response = get_voice_response(certification_question)
        certification_score = 15 if cert_response >= 4 else 0
    else:
        print("\n📝 Certification Status (Question 15)")
        certification_score = get_text_response(certification_question)

    # Historical behavior
    if voice_mode:
        behavior_response = get_voice_response(behavior_question)
        behavior_score = 0 if behavior_response >= 4 else 15
    else:
        print("\n📝 Historical Behavior (Question 16)")
        behavior_score = 15 - get_text_response(behavior_question)

    total_score = physical_score + mental_score + certification_score + behavior_score

    # Scoring interpretation
    def interpret(score):
        if score >= 90:
            return "Excellent Readiness"
        elif score >= 75:
            return "Good Readiness"
        elif score >= 60:
            return "Moderate Readiness"
        elif score >= 45:
            return "Low Readiness"
        else:
            return "Critical (Not Ready)"

    # Present results
    if voice_mode:
        text_to_speech(f"Your Physical Readiness score is {physical_score:.1f} out of 35")
        text_to_speech(f"Your Mental Readiness score is {mental_score:.1f} out of 35")
        text_to_speech(f"Your Certification Status score is {certification_score} out of 15")
        text_to_speech(f"Your Historical Behavior score is {behavior_score} out of 15")
        text_to_speech(f"Your Total Readiness Score is {total_score:.1f} out of 100")
        text_to_speech(f"Your Status is {interpret(total_score)}")
    else:
        print("\n📊 Readiness Summary:")
        print(f"🔹 Physical Readiness: {physical_score:.1f}/35")
        print(f"🔹 Mental Readiness: {mental_score:.1f}/35")
        print(f"🔸 Certification Status: {certification_score}/15")
        print(f"🔸 Historical Behavior: {behavior_score}/15")
        print(f"🏆 Total Readiness Score: {total_score:.1f}/100")
        print(f"📌 Status: {interpret(total_score)}")

        # Detailed interpretation
        print("\n📋 Detailed Assessment:")
        if physical_score < 21:
            print("- Physical readiness is concerning. Consider rest, recovery, or medical consultation.")
        if mental_score < 21:
            print("- Mental readiness needs improvement. Stress management or mental health support may be beneficial.")
        if certification_score < 15:
            print("- Certification requirements not met. Complete required training.")
        if behavior_score < 15:
            print("- Historical behavior flagged. Additional review may be needed.")

if __name__ == "__main__":
    try:
        readiness_scoring()
    except Exception as e:
        print(f"An error occurred: {e}")