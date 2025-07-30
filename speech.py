# speech.py
import speech_recognition as sr
from voice import analyze_emotion_from_audio
import sentiment
import moderation
from datetime import datetime
from collections import defaultdict
import os

# ---------------- Updated Questions ---------------- #
questions = [
    "How are you today?",
    "Do you feel like working today?",
    "How was your day yesterday?",
    "Are you worried about anything?",
    "Are you ready to work today?"
]

user_responses = []

# -------------- Voice Input -------------- #
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

            sentiment_result = {}
            moderation_result = {}

            try:
                sentiment_result = sentiment.analyze_sentiment(transcribed_text)
            except Exception as e:
                print(f"[❗ Sentiment Error] {e}")

            try:
                moderation_result = moderation.analyze_moderation(transcribed_text)
            except Exception as e:
                print(f"[❗ Moderation Error] {e}")

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

# ------------- Report 1: Sentiment + Moderation ------------- #
def generate_sentiment_report(responses, user_id="User001", sentiment_thresh=5.0, moderation_thresh=0.01):
    print("--------------------------------------------")
    report_lines = []
    report_lines.append(f"📋 Voice Sentiment Report for {user_id}")
    report_lines.append(f"🕒 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 60)

    sentiment_aggregate = defaultdict(float)
    moderation_aggregate = defaultdict(float)

    for idx, entry in enumerate(responses, 1):
        report_lines.append(f"\nQ{idx}: {entry['question']}")
        report_lines.append(f"🗣️ Answer: {entry['answer']}")
        report_lines.append(f"🎭 Emotion: {entry['emotion'] or 'N/A'}")

        sentiment_data = entry.get('sentiment') or {}
        moderation_data = entry.get('moderation') or {}

        for k, v in sentiment_data.items():
            sentiment_aggregate[k] += v
        for k, v in moderation_data.items():
            moderation_aggregate[k] += v

        # Show sentiment
        if sentiment_data:
            non_neutral = [(k, v) for k, v in sentiment_data.items() if k.lower() != 'neutral']
            if non_neutral:
                top_sentiments = sorted(non_neutral, key=lambda x: x[1], reverse=True)[:3]
                report_lines.append("🧠 Top Sentiments:")
                for label, score in top_sentiments:
                    report_lines.append(f"   - {label}: {score:.2f}")
            else:
                report_lines.append("🧠 Sentiment mostly neutral.")
        else:
            report_lines.append("🧠 Sentiment analysis failed or missing.")

        # Show moderation
        flagged = {k: v for k, v in moderation_data.items() if v >= moderation_thresh}
        if flagged:
            report_lines.append(f"🛡️ Moderation Flags (>{moderation_thresh}):")
            for k, v in flagged.items():
                report_lines.append(f"   - {k}: {v:.4f}")
        else:
            report_lines.append("🛡️ No moderation risks detected.")

    # Summary
    report_lines.append("\n📊 Summary Analysis:")

    top_sentiment_overall = sorted(
        [(k, v) for k, v in sentiment_aggregate.items() if k.lower() != 'neutral'],
        key=lambda x: x[1],
        reverse=True
    )[:3]

    if top_sentiment_overall:
        report_lines.append("🔝 Most Frequent Strong Sentiments:")
        for label, score in top_sentiment_overall:
            report_lines.append(f"   - {label}: {score:.2f}")
    else:
        report_lines.append("🧠 No strong sentiment trends detected.")

    top_moderation_overall = sorted(
        [(k, v) for k, v in moderation_aggregate.items()],
        key=lambda x: x[1],
        reverse=True
    )[:3]

    if any(v >= moderation_thresh * len(responses) for _, v in top_moderation_overall):
        report_lines.append("⚠️ Top Moderation Concerns:")
        for label, score in top_moderation_overall:
            if score >= moderation_thresh * len(responses):
                report_lines.append(f"   - {label}: {score:.4f}")

    all_clear = all(
        all(v < moderation_thresh for v in (e.get('moderation') or {}).values())
        for e in responses
    )
    report_lines.append("\n✅ Summary: No major red flags." if all_clear else "\n⚠️ Alert: Some moderation risks detected.")

    final_report = "\n".join(report_lines)
    filename = f"report_sentiment_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(final_report)

    print("--------------------------------------------")
    print(f"\n📁 Sentiment report saved as: {filename}")

# ------------- Report 2: Readiness Score ------------- #
import statistics

def generate_readiness_score_report(responses, user_id="User001"):
    POSITIVE_EMOTIONS = {"joy", "gratitude", "admiration", "optimism", "love", "hope", "approval", "relief", "pride"}
    NEGATIVE_EMOTIONS = {"anger", "sadness", "disgust", "fear", "grief", "disappointment", "disapproval", "annoyance", "remorse", "nervousness"}

    pos_raw = []
    neg_raw = []

    for entry in responses:
        sentiment_data = entry.get('sentiment') or {}

        # Get top 3 non-neutral sentiments
        non_neutral = [(k, v) for k, v in sentiment_data.items() if k.lower() != 'neutral']
        top_3 = sorted(non_neutral, key=lambda x: x[1], reverse=True)[:3]

        pos_score = sum(score for label, score in top_3 if label in POSITIVE_EMOTIONS)
        neg_score = sum(score for label, score in top_3 if label in NEGATIVE_EMOTIONS)

        pos_raw.append(pos_score)
        neg_raw.append(neg_score)

    # Safe std deviation
    def safe_std(values):
        return statistics.stdev(values) if len(values) > 1 else 1.0

    # Z-score calculation
    def z_scores(values):
        mean = statistics.mean(values)
        std = safe_std(values)
        return [(x - mean) / std for x in values]

    pos_z = z_scores(pos_raw)
    neg_z = z_scores(neg_raw)

    avg_pos_z = sum(z for z in pos_z if z > 0) / len(pos_z) if pos_z else 0
    avg_neg_z = sum(z for z in neg_z if z < 0) / len(neg_z) if neg_z else 0

    readiness = 50 + (avg_pos_z * 10) + (avg_neg_z * 10)
    readiness = round(max(0, min(readiness, 100)), 2)

    # Generate report
    report = [
        f"🧠 Mental & Emotional Readiness Score Report",
        f"👷 Worker ID: {user_id}",
        f"🕒 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 60,
        f"\n📊 Positive Z-Scores: {['{:.2f}'.format(z) for z in pos_z]}",
        f"📉 Negative Z-Scores: {['{:.2f}'.format(z) for z in neg_z]}",
        f"\n✅ Final Readiness Score: {readiness:.2f} / 100"
    ]

    if readiness >= 75:
        report.append("🟢 Status: Worker seems fully ready and positive.")
    elif readiness >= 50:
        report.append("🟡 Status: Worker is somewhat ready, but monitor closely.")
    else:
        report.append("🔴 Status: Worker may not be mentally/emotionally ready.")

    filename = f"report_readiness_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    print(f"\n📁 Readiness score report saved as: {filename}")

# --------------- Main ---------------- #
if __name__ == "__main__":
    for question in questions:
        result = get_voice_input_for_question(question)
        if result:
            user_responses.append(result)

    if user_responses:
        generate_sentiment_report(user_responses)
        generate_readiness_score_report(user_responses)
