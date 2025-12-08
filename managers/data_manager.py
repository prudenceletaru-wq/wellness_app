# managers/data_manager.py
import pandas as pd
import os
from datetime import date

COLUMNS = [
    "date",
    "user_id",
    "sleep_hours",
    "mood",
    "stress",
    "activity_min",
    "notes"
]


class DataManager:
    def __init__(self, data_csv="data/saved_data.csv"):
        self.data_csv = data_csv
        self._ensure_csv()

    def _ensure_csv(self):
        parent = os.path.dirname(self.data_csv)
        if parent and not os.path.exists(parent):
            os.makedirs(parent)
        if not os.path.exists(self.data_csv):
            pd.DataFrame(columns=COLUMNS).to_csv(self.data_csv, index=False)

    def load_entries(self) -> pd.DataFrame:
        try:
            df = pd.read_csv(self.data_csv, dtype=str)
        except pd.errors.EmptyDataError:
            df = pd.DataFrame(columns=COLUMNS)
            df.to_csv(self.data_csv, index=False)
        for c in COLUMNS:
            if c not in df.columns:
                df[c] = pd.NA
        return df[COLUMNS].copy()

    def save_entry(self, entry: dict) -> pd.DataFrame:
        """
        Save or overwrite today's entry for the given user_id.
        Date is forced to today's date (ISO).
        """
        df = self.load_entries()

        today_str = date.today().isoformat()
        entry_date = today_str  # force today's date
        entry_copy = entry.copy()
        entry_copy["date"] = entry_date

        # If existing row for user & date -> overwrite that row only
        if not df.empty:
            mask = (df["user_id"].astype(str) == str(entry_copy["user_id"])) & (df["date"].astype(str) == entry_date)
        else:
            mask = pd.Series([False] * 0)

        if mask.any():
            # overwrite specific columns
            idx = df.index[mask][0]
            for col in ["sleep_hours", "mood", "stress", "activity_min", "notes"]:
                df.at[idx, col] = entry_copy.get(col)
        else:
            # append new entry
            df = pd.concat([df, pd.DataFrame([entry_copy])], ignore_index=True)

        df.to_csv(self.data_csv, index=False)
        return df
