# sentiment.py
from transformers import pipeline

classifier = pipeline("text-classification", model="bhadresh-savani/bert-base-go-emotion", return_all_scores=True)

def analyze_sentiment(text):
    print("\n🔍 Running sentiment check on:", text)

    results = classifier(text)
    emotion_dict = {emotion['label']: round(emotion['score'] * 100, 2) for emotion in results[0]}

    print("\n🧠 Sentiment Results:")
    for label, score in emotion_dict.items():
        print(f"{label}: {score}")

    return emotion_dict  # ✅ You missed this line
