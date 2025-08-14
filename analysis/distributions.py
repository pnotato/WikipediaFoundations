"""
Distribution summaries for vital_level and links_away

Outputs (saved under ../plots/):
  - vital_distribution.csv           # counts & proportions for rated pages
  - links_away_distribution.csv      # histogram table for steps
  - vital_hist.png                   # bar chart of vital level distribution
  - links_away_hist.png              # histogram of distance to Philosophy
  - vital_ecdf.png                   # ECDF for vital levels (step plot)
  - links_away_ecdf.png              # ECDF for distance

Notes:
  * Filters to rated pages for vital_level (>0), and keeps non-null links_away.
  * Also reports basic descriptive stats (count, mean, std, min, quartiles, max).
"""

import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# -----------------
# Config & loading
# -----------------
HERE = os.path.dirname(__file__)
DATA_PATH = os.path.join(HERE, "../data/cleaned_data.csv")
PLOTS_DIR = os.path.join(HERE, "../plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

# Load
df = pd.read_csv(DATA_PATH)

# Basic filters
df_vital = df.loc[df["vital_level"].notna() & (df["vital_level"] > 0)].copy()
df_links = df.loc[df["links_away"].notna()].copy()

# Cast types
df_vital["vital_level"] = df_vital["vital_level"].astype(int)
df_links["links_away"] = df_links["links_away"].astype(int)

# -------------------------------
# 1) Vital distribution (table)
# -------------------------------
vit_counts = (
    df_vital["vital_level"].value_counts().sort_index().rename("count").to_frame()
)
vit_counts["proportion"] = vit_counts["count"] / vit_counts["count"].sum()
vit_counts.index.name = "vital_level"

# Descriptive stats
vit_desc = df_vital["vital_level"].describe().to_frame(name="vital_level")

# Save table
vit_counts.to_csv(os.path.join(PLOTS_DIR, "vital_distribution.csv"))
vit_desc.to_csv(os.path.join(PLOTS_DIR, "vital_desc.csv"))

# -------------------------------
# 2) Links-away distribution (table)
# -------------------------------
# Histogram bins for steps: use each integer step as a bin
step_counts = (
    df_links["links_away"].value_counts().sort_index().rename("count").to_frame()
)
step_counts["proportion"] = step_counts["count"] / step_counts["count"].sum()
step_counts.index.name = "links_away"

links_desc = df_links["links_away"].describe().to_frame(name="links_away")

# Save table
step_counts.to_csv(os.path.join(PLOTS_DIR, "links_away_distribution.csv"))
links_desc.to_csv(os.path.join(PLOTS_DIR, "links_away_desc.csv"))

# -----------------
# 3) Plots
# -----------------
sns.set_theme(style="whitegrid", context="talk")

# Vital: bar chart (categorical levels 1–5)
plt.figure(figsize=(8,5))
ax = sns.barplot(x=vit_counts.index, y=vit_counts["count"].values)
ax.set_xlabel("Vital Level")
ax.set_ylabel("Count of Articles (rated)")
ax.set_title("Distribution of Vital Levels (rated pages)")
for i, v in enumerate(vit_counts["count"].values):
    ax.text(i, v, f"{v}", ha="center", va="bottom", fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "vital_hist.png"))
plt.close()

# Links-away: histogram (integer steps)
plt.figure(figsize=(10,5))
ax = sns.histplot(df_links, x="links_away", bins=range(int(df_links["links_away"].min()), int(df_links["links_away"].max())+2), edgecolor=None)
ax.set_xlabel("Links Away from Philosophy")
ax.set_ylabel("Number of Articles")
ax.set_title("Distribution of Distance to Philosophy (steps)")
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "links_away_hist.png"))
plt.close()

# ECDFs (good for comparing shapes/medians visually)
# Vital ECDF
plt.figure(figsize=(8,5))
vit_sorted = np.sort(df_vital["vital_level"].values)
vit_ecdf = np.arange(1, len(vit_sorted)+1) / len(vit_sorted)
plt.step(vit_sorted, vit_ecdf, where="post")
plt.xlabel("Vital Level")
plt.ylabel("ECDF")
plt.title("ECDF of Vital Levels (rated pages)")
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "vital_ecdf.png"))
plt.close()

# Links-away ECDF
plt.figure(figsize=(10,5))
la_sorted = np.sort(df_links["links_away"].values)
la_ecdf = np.arange(1, len(la_sorted)+1) / len(la_sorted)
plt.step(la_sorted, la_ecdf, where="post")
plt.xlabel("Links Away from Philosophy")
plt.ylabel("ECDF")
plt.title("ECDF of Distance to Philosophy (steps)")
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "links_away_ecdf.png"))
plt.close()

print("Saved tables: vital_distribution.csv, vital_desc.csv, links_away_distribution.csv, links_away_desc.csv")
print("Saved plots: vital_hist.png, links_away_hist.png, vital_ecdf.png, links_away_ecdf.png")
