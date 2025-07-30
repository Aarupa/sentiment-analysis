# import speech_recognition as sr
# from voice import analyze_emotion_from_audio
# import sentiment
# import moderation

# def get_voice_input():
#     recognizer = sr.Recognizer()
#     with sr.Microphone() as source:
#         print("🎤 Listening... Speak your answer.")
#         recognizer.adjust_for_ambient_noise(source)
#         audio = recognizer.listen(source)

#         # Analyze emotion and get transcribed text using Whisper
#         transcribed_text = analyze_emotion_from_audio(audio)

#         if transcribed_text:
#             print("🗣️ You said:", transcribed_text)
#             sentiment.analyze_sentiment(transcribed_text)
#             moderation.analyze_moderation(transcribed_text)
#         else:
#             print("❗Could not transcribe audio.")


# if __name__ == "__main__":
#     user_text = get_voice_input()
#     if user_text:
#         sentiment.analyze_sentiment(user_text)
#         moderation.analyze_moderation(user_text)


import speech_recognition as sr
from voice import analyze_emotion_from_audio
import sentiment
import moderation
from datetime import datetime
import json

# Define the list of questions
questions = [
    "How are you feeling today?",
    "What motivated you this week?",
    "Did you face any challenges recently?",
    "What are you looking forward to?",
    "Is there anything you'd like help with?"
]

user_responses = []

def get_voice_input_for_question(question):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(f"\n📝 Question: {question}")
        print("🎤 Listening... Speak your answer.")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        transcribed_text, emotion = analyze_emotion_from_audio(audio)

        if transcribed_text:
            print("🗣️ You said:", transcribed_text)
            sentiment_result = sentiment.analyze_sentiment(transcribed_text)
            moderation_result = moderation.analyze_moderation(transcribed_text)

            return {
                "question": question,
                "answer": transcribed_text,
                "emotion": emotion,
                "sentiment": sentiment_result,
                "moderation": moderation_result
            }
        else:
            print("❗Could not transcribe audio.")
            return None

def generate_report(responses, user_id="User001"):
    report_lines = []
    report_lines.append(f"📋 Voice Sentiment Report for {user_id}")
    report_lines.append(f"🕒 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 60)

    for idx, entry in enumerate(responses, 1):
        report_lines.append(f"\nQ{idx}: {entry['question']}")
        report_lines.append(f"🗣️ Answer: {entry['answer']}")
        report_lines.append(f"🎭 Emotion: {entry['emotion']}")
        report_lines.append(f"🧠 Sentiment Scores:")
        for k, v in entry['sentiment'].items():
            if v > 1.0:
                report_lines.append(f"   - {k}: {v:.2f}")
        report_lines.append(f"🛡️ Moderation Flags:")
        for k, v in entry['moderation'].items():
            if v > 0.01:
                report_lines.append(f"   - {k}: {v:.4f}")

    report_lines.append("\n✅ Summary: No major red flags." if all(
        all(v < 0.05 for v in e['moderation'].values()) for e in responses
    ) else "\n⚠️ Alert: Some moderation risks detected.")

    final_report = "\n".join(report_lines)
    filename = f"voice_sentiment_report_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(final_report)

    print(f"\n📁 Report saved as: {filename}")

if __name__ == "__main__":
    for question in questions:
        result = get_voice_input_for_question(question)
        if result:
            user_responses.append(result)

    if user_responses:
        generate_report(user_responses)

