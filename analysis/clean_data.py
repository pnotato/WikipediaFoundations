'''
1. Cleans the data, fixes groups
'''
import pandas as pd

api_data = pd.read_csv("../data/api_data.csv")
hyperlink_data = pd.read_csv("../data/hyperlink_data.csv")

api_data_filtered = api_data.drop(columns=["page_url", "run_id"])
complete_runs = hyperlink_data[hyperlink_data["stop_reason"] == 'reached_philosophy']

merged = complete_runs.merge(api_data_filtered, on="page_title", how="left")
merged_filled = merged.fillna(0)
merged_filled["created_ts"] = merged["created_ts"]
merged_filled["page_title_normalized"] = merged_filled["page_title"].str.replace("Philosophical", "Philosophy", regex=False)
merged_filled.drop(columns=["page_url"], inplace=True)
merged_filled.to_csv("../data/cleaned_data.csv", index=False)
