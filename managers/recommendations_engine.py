# managers/recommendations_engine.py
from .base_manager import BaseManager

class RecommendationsEngine(BaseManager):
    def __init__(self):
        self.colors = {"healthy": "green", "moderate": "orange", "high": "red"}

    def _span(self, text: str, level: str) -> str:
        color = self.colors.get(level, "black")
        return f"<span style='color:{color}'>{text}</span>"

    def generate(self, entry: dict) -> list:
        tips = []

        # Sleep
        try:
            s = float(entry.get("sleep_hours", None))
            if 7 <= s <= 9:
                tips.append(self._span("💤 **Sleep:** Healthy — 7–9 hours.", "healthy"))
            elif 6 <= s < 7:
                tips.append(self._span("💤 **Sleep:** Moderate — slightly below recommended.", "moderate"))
            else:
                tips.append(self._span("💤 **Sleep:** High risk ⚠️ Adjust sleep schedule to 7–9 hrs.", "high"))
        except Exception:
            pass

        # Activity
        try:
            a = float(entry.get("activity_min", None))
            if a >= 30:
                tips.append(self._span("🏃‍♂️ **Activity:** Healthy — meets recommended activity.", "healthy"))
            elif 15 <= a < 30:
                tips.append(self._span("🏃‍♀️ **Activity:** Moderate — add short walks.", "moderate"))
            else:
                tips.append(self._span("⚠️ **Activity:** High risk — aim for 30+ mins daily.", "high"))
        except Exception:
            pass

        # Mood
        try:
            m = float(entry.get("mood", None))
            if 7 <= m <= 10:
                tips.append(self._span("🙂 **Mood:** Healthy — keep doing what works.", "healthy"))
            elif 4 <= m <= 6:
                tips.append(self._span("😐 **Mood:** Moderate — schedule enjoyable activities.", "moderate"))
            else:
                tips.append(self._span("😞 **Mood:** High risk — consider reaching out for support.", "high"))
        except Exception:
            pass

        # Stress
        try:
            stv = float(entry.get("stress", None))
            if 1 <= stv <= 3:
                tips.append(self._span("😌 **Stress:** Healthy — continue current coping strategies.", "healthy"))
            elif 4 <= stv <= 6:
                tips.append(self._span("😰 **Stress:** Moderate — relaxation may help.", "moderate"))
            else:
                tips.append(self._span("⚠️ **Stress:** High — try short breathing exercises.", "high"))
        except Exception:
            pass

        if not tips:
            tips.append(self._span("✅ All metrics look within healthy ranges — keep it up!", "healthy"))

        return tips
