# report.py
from datetime import datetime
import json

def generate_report(user_responses, user_id="User001"):
    report_lines = []
    report_lines.append(f"📋 Emotion & Sentiment Report — {user_id}")
    report_lines.append(f"🕒 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 60)

    for idx, entry in enumerate(user_responses, 1):
        report_lines.append(f"\nQ{idx}: {entry['question']}")
        report_lines.append(f"🗣️ Answer: {entry['answer']}")
        report_lines.append(f"🎭 Emotion: {entry['emotion']}")
        report_lines.append(f"🧠 Sentiment Summary:")
        for k, v in entry['sentiment'].items():
            if v > 1.0:  # Highlight strong sentiments
                report_lines.append(f"   - {k}: {v:.2f}")
        report_lines.append(f"🛡️ Moderation Flags:")
        for k, v in entry['moderation'].items():
            if v > 0.01:  # Filter low risks
                report_lines.append(f"   - {k}: {v:.4f}")

    report_lines.append("\n✅ Summary: No major red flags." if all(
        all(v < 0.05 for v in e['moderation'].values()) for e in user_responses
    ) else "\n⚠️ Alert: Some moderation risks detected.")

    report = "\n".join(report_lines)
    
    with open("voice_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    print("\n📁 Report saved as: voice_report.txt")

    return report
