# managers/ui_manager.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date
from .base_manager import BaseManager

class UIManager(BaseManager):
    """
    Responsible for Streamlit UI rendering: entry form, dashboard, plots, and
    overwrite confirmation for same-day entries.
    Expects an 'app' object with attributes:
        - data_manager (DataManager instance)
        - analysis_engine (AnalysisEngine instance)
        - recs_engine (RecommendationsEngine instance)
    """

    def __init__(self, app):
        self.app = app

    def render_dashboard(self, username: str):
        # Clear any leftover pending entries
        if "pending_entry" in st.session_state:
            del st.session_state["pending_entry"]

        st.title("🌿 Lifestyle & Wellness Tracker 🌿")
        st.markdown(f"**Logged in as:** `{username}`")
        st.write("")  # spacer

        # Load entries
        df_all = self.app.data_manager.load_entries()
        user_df = df_all[df_all["user_id"] == username].copy() if not df_all.empty else pd.DataFrame()

        # Welcome message
        if user_df.empty:
            st.info(f"Welcome, {username}! 🌟 Start tracking your wellness today — small steps lead to big improvements! 💪")
        else:
            st.success(f"Welcome back, {username}! 🌟 Keep logging daily — small steps add up. 💪")

        # ENTRY FORM
        st.header("Daily Wellness Entry")
        today_str = date.today().isoformat()
        logged_today = (not user_df.empty) and (user_df["date"].astype(str) == today_str).any()

        with st.form("entry_form"):
            st.text_input("Date (auto)", value=today_str, disabled=True, key="entry_date_display")
            sleep = st.number_input("Sleep hours (hrs)", min_value=0.0, max_value=24.0, value=7.0, step=0.25, key="entry_sleep")
            mood = st.slider("Mood (1-10)", 1, 10, 7, key="entry_mood")
            stress = st.slider("Stress (1-10)", 1, 10, 3, key="entry_stress")
            activity = st.number_input("Physical activity (minutes)", min_value=0, max_value=1440, value=30, key="entry_activity")
            notes = st.text_area("Notes (optional)", "", key="entry_notes")
            submit = st.form_submit_button("Save entry")

        if submit:
            entry = {
                "date": today_str,
                "user_id": username,
                "sleep_hours": float(sleep),
                "mood": int(mood),
                "stress": int(stress),
                "activity_min": int(activity),
                "notes": notes or ""
            }

            mask = (df_all["user_id"] == username) & (df_all["date"].astype(str) == today_str) if not df_all.empty else pd.Series([False])

            if mask.any():
                st.warning("You already logged data today. Overwriting the entry...")
                try:
                    self.app.data_manager.save_entry(entry)
                    st.success("Entry overwritten for today ✅")
                    st.experimental_rerun()  # instant refresh
                except Exception as e:
                    st.error(f"Failed to overwrite entry: {e}")
            else:
                try:
                    self.app.data_manager.save_entry(entry)
                    st.success("✅ Entry saved successfully! Keep up the good work! 🌟")
                    st.experimental_rerun()  # instant refresh
                except Exception as e:
                    st.error(f"Failed to save entry: {e}")

        # DASHBOARD
        st.header("Your Dashboard")
        if not user_df.empty:
            display_df = user_df.sort_values("date", ascending=False).reset_index(drop=True)
            st.subheader("Entries (latest first)")
            st.dataframe(display_df)

            # Key statistics
            st.subheader("Key statistics")
            try:
                stats = pd.DataFrame({
                    "Average": [
                        pd.to_numeric(user_df["sleep_hours"], errors="coerce").mean(),
                        pd.to_numeric(user_df["mood"], errors="coerce").mean(),
                        pd.to_numeric(user_df["stress"], errors="coerce").mean(),
                        pd.to_numeric(user_df["activity_min"], errors="coerce").mean()
                    ],
                    "Minimum": [
                        pd.to_numeric(user_df["sleep_hours"], errors="coerce").min(),
                        pd.to_numeric(user_df["mood"], errors="coerce").min(),
                        pd.to_numeric(user_df["stress"], errors="coerce").min(),
                        pd.to_numeric(user_df["activity_min"], errors="coerce").min()
                    ],
                    "Maximum": [
                        pd.to_numeric(user_df["sleep_hours"], errors="coerce").max(),
                        pd.to_numeric(user_df["mood"], errors="coerce").max(),
                        pd.to_numeric(user_df["stress"], errors="coerce").max(),
                        pd.to_numeric(user_df["activity_min"], errors="coerce").max()
                    ]
                }, index=["Sleep (hrs)", "Mood (1-10)", "Stress (1-10)", "Physical Activity (min)"])
                st.table(stats.round(2))
            except Exception:
                st.info("Not enough numeric data to compute stats.")

            # Recommendations
            st.subheader("Latest entry recommendations")
            latest = display_df.iloc[0].to_dict()
            recs = self.app.recs_engine.generate(latest)
            for r in recs:
                st.markdown(f"- {r}", unsafe_allow_html=True)

            # Correlations
            st.subheader("Correlations")
            try:
                corr = self.app.analysis_engine.correlations(user_df)
                if corr.empty:
                    st.info("Not enough data to compute correlations.")
                else:
                    fig, ax = plt.subplots(figsize=(6, 4))
                    sns.heatmap(corr, annot=True, fmt=".2f", vmin=-1, vmax=1, ax=ax, cmap="coolwarm")
                    ax.set_title("Correlation Heatmap")
                    st.pyplot(fig)
            except Exception as e:
                st.error(f"Could not compute correlations: {e}")

            # Rolling 7-day trends
            st.subheader("Trends (rolling 7-day mean)")
            if len(user_df) >= 7:
                try:
                    rm_sleep = self.app.analysis_engine.rolling_mean(user_df, "sleep_hours", window=7)
                    rm_mood  = self.app.analysis_engine.rolling_mean(user_df, "mood", window=7)
                    rm_stress = self.app.analysis_engine.rolling_mean(user_df, "stress", window=7)
                    rm_activity = self.app.analysis_engine.rolling_mean(user_df, "activity_min", window=7)

                    fig2, axes = plt.subplots(4, 1, figsize=(9, 12), sharex=True)
                    series_list = [rm_sleep, rm_mood, rm_stress, rm_activity]
                    colors = ["blue", "orange", "red", "green"]
                    titles = ["Sleep (hrs)", "Mood (1-10)", "Stress (1-10)", "Activity (min)"]

                    for i, ax in enumerate(axes):
                        s = series_list[i]
                        if not s.empty:
                            ax.plot(s.index, s.values, color=colors[i])
                            ax.set_ylabel(titles[i])
                            ax.set_title(f"{titles[i]} (7-day rolling mean)")
                    axes[-1].set_xlabel("Date")
                    fig2.tight_layout()
                    st.pyplot(fig2)
                except Exception as e:
                    st.error(f"Failed to plot rolling trends: {e}")
            else:
                st.info("At least 7 entries required to show rolling trends.")

            # Weekly averages
            st.subheader("Weekly averages")
            try:
                weekly = self.app.analysis_engine.weekly_summary(user_df)
                if weekly is not None and weekly.shape[0] > 0:
                    weekly = weekly.set_index("date")
                    fig3, ax1 = plt.subplots(figsize=(10, 5))
                    ax1.plot(weekly.index, weekly["sleep_hours"], label="Sleep (hrs)", marker="o")
                    ax1.plot(weekly.index, weekly["mood"], label="Mood (1-10)", marker="o")
                    ax1.plot(weekly.index, weekly["stress"], label="Stress (1-10)", marker="o")
                    ax1.set_ylabel("Sleep / Mood / Stress")
                    ax2 = ax1.twinx()
                    ax2.plot(weekly.index, weekly["activity_min"], label="Activity (min)", marker="o")
                    ax2.set_ylabel("Physical Activity (min)")
                    lines, labels = ax1.get_legend_handles_labels()
                    lines2, labels2 = ax2.get_legend_handles_labels()
                    ax1.legend(lines + lines2, labels + labels2, loc="upper left")
                    fig3.tight_layout()
                    st.pyplot(fig3)
                else:
                    st.info("Weekly averages not available (not enough data).")
            except Exception as e:
                st.error(f"Failed to compute weekly averages: {e}")

        else:
            st.subheader("Entries (latest first)")
            st.info("No data to display yet. Use the entry form above to add your first entry.")
