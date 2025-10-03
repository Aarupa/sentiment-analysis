import os
from transformers import pipeline

def get_score(question, scale_info):
    while True:
        try:
            print(f"\n{question}")
            for key, (text, _) in scale_info.items():
                print(f"{key}. {text}")
            choice = input("Enter your choice (1-5): ").strip()
            if choice in scale_info:
                return scale_info[choice][1]
            else:
                print("❌ Invalid input. Please enter a number between 1 and 5.")
        except ValueError:
            print("❌ Invalid input. Please enter a number between 1 and 5.")

def get_yes_no_score(question):
    while True:
        answer = input(f"\n{question} (Yes/No): ").strip().lower()
        if answer in ["yes", "y"]:
            return 15
        elif answer in ["no", "n"]:
            return 0
        else:
            print("❌ Invalid input. Please answer Yes or No.")

def analyze_audio_sentiment(audio_file):
    """Analyze audio file for sentiment using lightweight model"""
    try:
        # Initialize sentiment analysis pipeline
        classifier = pipeline("audio-classification", model="superb/hubert-base-superb-er")
        
        # Run analysis
        results = classifier(audio_file)
        
        # Get top emotion and score
        top_emotion = results[0]['label']
        emotion_score = results[0]['score']
        
        # Map emotion to our scoring system (0-35)
        emotion_mapping = {
            'angry': 5,
            'disgust': 5,
            'fear': 10,
            'happy': 30,
            'neutral': 20,
            'sad': 10,
            'surprise': 25
        }
        
        # Calculate weighted score
        mental_score = emotion_mapping.get(top_emotion.lower(), 15) * emotion_score
        return min(35, max(0, mental_score))  # Ensure score is between 0-35
    
    except Exception as e:
        print(f"❌ Error analyzing audio: {e}")
        return 17.5  # Return neutral score if analysis fails

def readiness_scoring():
    # Likert scale definition
    likert_scale = {
        "1": ("Strongly Disagree", 1),
        "2": ("Disagree", 2),
        "3": ("Neutral", 3),
        "4": ("Agree", 4),
        "5": ("Strongly Agree", 5)
    }
    
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

    print("\n📝 Physical Readiness Questions (1-7)")
    physical_score = sum(get_score(q, likert_scale) for q in physical_questions) * 1.0
    physical_score = (physical_score / 35) * 35  # Scale to 35 points

    # Mental readiness assessment choice
    print("\n🧠 Mental Readiness Assessment Method:")
    print("1. Text-based questions (default)")
    print("2. Audio-based sentiment analysis")
    assessment_choice = input("Choose assessment method (1 or 2): ").strip()

    if assessment_choice == "2":
        # Audio-based assessment
        audio_file = input("Enter path to your audio file (or press Enter to skip): ").strip()
        if audio_file and os.path.exists(audio_file):
            print("\n🎤 Analyzing your voice for emotional state...")
            mental_score = analyze_audio_sentiment(audio_file)
            print(f"🔹 Audio analysis complete. Mental readiness score: {mental_score:.1f}/35")
        else:
            print("⚠️ Using text-based assessment (invalid audio file)")
            mental_score = sum(get_score(q, likert_scale) for q in mental_questions) * 1.0
            mental_score = (mental_score / 35) * 35
    else:
        # Default text-based assessment
        print("\n📝 Mental Readiness Questions (8-14)")
        mental_score = sum(get_score(q, likert_scale) for q in mental_questions) * 1.0
        mental_score = (mental_score / 35) * 35

    print("\n📝 Certification Status (Question 15)")
    certification_score = get_yes_no_score(certification_question)

    print("\n📝 Historical Behavior (Question 16)")
    behavior_score = 15 - get_yes_no_score(behavior_question)  # Inverse scoring for behavior

    total_score = physical_score + mental_score + certification_score + behavior_score

    # Scoring interpretation
    def interpret(score):
        if score >= 90:
            return "✅ Excellent Readiness"
        elif score >= 75:
            return "🟢 Good Readiness"
        elif score >= 60:
            return "🟡 Moderate Readiness"
        elif score >= 45:
            return "🟠 Low Readiness"
        else:
            return "🔴 Critical (Not Ready)"

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
    readiness_scoring()