# userinput.py
from .speech import get_voice_input, analyze_emotion_from_audio,moderation
user_responses = []

questions = [
    "How are you feeling today?",
    "What motivated you this week?",
    "Did you face any challenges recently?",
    "What are you looking forward to?",
    "Is there anything you'd like help with?"
    # Add more if needed
]

for i, question in enumerate(questions, start=1):
    print(f"\n📝 Question {i}: {question}")
    answer_text = get_voice_input()  # This should return transcribed text
    if answer_text:
        # Analyze emotion
        emotion = analyze_emotion_from_audio(answer_text)  # Update to return emotion if needed
        sentiment = sentiment.analyze_sentiment(answer_text)
        moderation_result = moderation.analyze_moderation(answer_text)

        # Store the full record
        user_responses.append({
            "question": question,
            "answer": answer_text,
            "emotion": emotion,
            "sentiment": sentiment,
            "moderation": moderation_result
        })
