# moderation.py
from transformers import pipeline

moderator = pipeline("text-classification", model="unitary/toxic-bert", return_all_scores=True)

def analyze_moderation(text):
    print("\n🚨 Running moderation analysis on:", text)

    results = moderator(text)
    moderation_dict = {res['label']: round(res['score'], 4) for res in results[0]}

    print("\n🛡️ Moderation Results:")
    for label, score in moderation_dict.items():
        print(f"{label}: {score}")

    return moderation_dict  # ✅ Important!
