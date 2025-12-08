# managers/sample_data_generator.py
import pandas as pd
import numpy as np
from datetime import date, timedelta
import os

class SampleDataGenerator:
    def __init__(self, users_csv="data/users.csv", output_csv="data/saved_data.csv", days=30):
        self.users_csv = users_csv
        self.output_csv = output_csv
        self.days = days

    def generate_for_user(self, user_id: str, days: int = None) -> pd.DataFrame:
        if days is None:
            days = self.days
        rows = []
        today = date.today()
        for i in range(days):
            d = today - timedelta(days=(days - 1 - i))
            sleep = round(max(4.5, min(9.5, np.random.normal(7.2, 1.0))), 2)
            mood = int(max(1, min(10, round(np.random.normal(6.8, 1.5)))))
            stress = int(max(1, min(10, round(np.random.normal(4.0, 1.8)))))
            activity = int(max(0, min(120, int(np.random.normal(35, 20)))))
            rows.append({
                "date": d.isoformat(),
                "user_id": user_id,
                "sleep_hours": sleep,
                "mood": mood,
                "stress": stress,
                "activity_min": activity,
                "notes": ""
            })
        return pd.DataFrame(rows)

    def generate_all(self, days: int = None):
        if days is None:
            days = self.days
        if not os.path.exists(self.users_csv):
            print(f"Users CSV '{self.users_csv}' not found.")
            return
        users_df = pd.read_csv(self.users_csv, dtype=str).fillna("")
        all_rows = []
        for user in users_df["username"].dropna():
            all_rows.append(self.generate_for_user(user, days))
        if not all_rows:
            print("No users found.")
            return
        df_all = pd.concat(all_rows, ignore_index=True)
        df_all.to_csv(self.output_csv, index=False)
        print(f"Generated {len(df_all)} rows to '{self.output_csv}'.")
