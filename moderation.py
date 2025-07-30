from transformers import pipeline

moderator = pipeline("text-classification", model="unitary/toxic-bert", return_all_scores=True)

def analyze_moderation(text):
    print("\n🚨 Running moderation analysis on:", text)

    results = moderator(text)
    print("\n🛡️ Moderation Results:")
    for result in results[0]:
        print(f"{result['label']}: {result['score']:.4f}")
