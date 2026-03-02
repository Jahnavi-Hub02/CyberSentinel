"""
CyberSentinel - Comprehensive Evaluation Metrics
==================================================
Generates all evaluation metrics, equations, and plots for the conference paper.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    roc_auc_score, roc_curve,
    precision_score, recall_score, f1_score,
    confusion_matrix
)

import time
import os


# ─────────────────────────────────────────────
# 0. LOAD DATASET
# ─────────────────────────────────────────────

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Dataset is in backend/data/
PROJECT_ROOT = os.path.dirname(BASE_DIR)

CSV_PATH = os.path.join(
    PROJECT_ROOT,
    "backend",
    "data",
    "cybersecurity_cases_india_combined.csv"
)

print(f"\n📂 Loading dataset from:\n{CSV_PATH}\n")

df = pd.read_csv(CSV_PATH)

print("=" * 60)
print("  CyberSentinel — Evaluation Metrics Report")
print("=" * 60)
print(f"\nDataset Shape: {df.shape[0]} records × {df.shape[1]} columns\n")


# ─────────────────────────────────────────────
# 1. FEATURE ENGINEERING
# ─────────────────────────────────────────────

incident_type_severity = {
    "phishing": 0.3,
    "malware": 0.5,
    "malware_attacks": 0.5,
    "data breach": 0.8,
    "ransomware": 0.9,
    "hacking": 0.7,
    "ddos": 0.6,
    "online fraud": 0.6,
    "identity theft": 0.55,
    "cyber bullying": 0.35,
    "others": 0.4,
}

df["incident_type_score"] = (
    df["Incident_Type"].str.lower().str.strip()
    .map(lambda x: incident_type_severity.get(x, 0.5))
)

max_amt = df["Amount_Lost_INR"].max()
df["amount_lost_normalized"] = df["Amount_Lost_INR"] / max_amt

city_counts = df["City"].value_counts()
df["location_incident_count"] = df["City"].map(city_counts) / city_counts.max()

df["off_hours"] = (df["Day"] % 7 < 2).astype(float)
df["hour"] = df["Day"] % 24

df["severity_score"] = df["incident_type_score"]

FEATURE_COLS = [
    "incident_type_score",
    "location_incident_count",
    "amount_lost_normalized",
    "severity_score",
    "off_hours",
    "hour",
]

X = df[FEATURE_COLS].fillna(0.0)


# ─────────────────────────────────────────────
# 2. TRAIN ISOLATION FOREST
# ─────────────────────────────────────────────

print("─" * 60)
print("1. ISOLATION FOREST MODEL")
print("─" * 60)

contamination = min(0.1, max(0.02, len(df) / 1000))

t0 = time.time()

model = IsolationForest(
    n_estimators=100,
    contamination=contamination,
    random_state=42,
    n_jobs=-1,
)

model.fit(X)

train_time = (time.time() - t0) * 1000

predictions = model.predict(X)
raw_scores = model.score_samples(X)

anomaly_scores = -raw_scores
anomaly_scores = (anomaly_scores - anomaly_scores.min()) / (
    anomaly_scores.max() - anomaly_scores.min() + 1e-8
)

df["anomaly_score"] = anomaly_scores
df["is_anomaly"] = (predictions == -1)

n_anomalies = df["is_anomaly"].sum()

print(f"\nTraining Time: {train_time:.2f} ms")
print(f"Anomalies Detected: {n_anomalies} ({n_anomalies/len(df)*100:.2f}%)")


# ─────────────────────────────────────────────
# 3. PSEUDO LABEL EVALUATION
# ─────────────────────────────────────────────

type_counts = df["Incident_Type"].value_counts()
rare_threshold = type_counts.quantile(0.20)
rare_types = set(type_counts[type_counts <= rare_threshold].index)

df["pseudo_label"] = df["Incident_Type"].isin(rare_types).astype(int)

y_true = df["pseudo_label"].values
y_pred = df["is_anomaly"].astype(int).values

precision = precision_score(y_true, y_pred, zero_division=0)
recall = recall_score(y_true, y_pred, zero_division=0)
f1 = f1_score(y_true, y_pred, zero_division=0)
auc = roc_auc_score(y_true, anomaly_scores)

print("\nModel Performance:")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1-Score  : {f1:.4f}")
print(f"AUC-ROC   : {auc:.4f}")


# ─────────────────────────────────────────────
# 4. GENERATE PLOTS
# ─────────────────────────────────────────────

plt.rcParams.update({
    "figure.facecolor": "#0d1117",
    "axes.facecolor": "#161b22",
    "text.color": "white",
    "axes.labelcolor": "white",
    "xtick.color": "white",
    "ytick.color": "white",
})

fig, ax = plt.subplots(figsize=(8, 6))

ax.hist(anomaly_scores, bins=40)
ax.set_title("Isolation Forest Anomaly Score Distribution")
ax.set_xlabel("Anomaly Score")
ax.set_ylabel("Frequency")

output_path = os.path.join(BASE_DIR, "cybersentinel_evaluation_metrics.png")

plt.tight_layout()
plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="#0d1117")
plt.close()

print(f"\nPlot saved at:\n{output_path}")


# ─────────────────────────────────────────────
# 5. FINAL SUMMARY
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("FINAL METRICS SUMMARY")
print("=" * 60)

print(f"""
Dataset Size          : {len(df)}
Features Used         : {len(FEATURE_COLS)}
Model                 : Isolation Forest
n_estimators          : 100
Contamination         : {contamination:.4f}
Anomalies Detected    : {n_anomalies}
Precision             : {precision:.4f}
Recall                : {recall:.4f}
F1-Score              : {f1:.4f}
AUC-ROC               : {auc:.4f}
Training Time (ms)    : {train_time:.2f}
""")

print("\n✅ All evaluation metrics computed successfully!")

# BASELINE: flag top 10% by financial loss only (single-feature threshold)
threshold = df['Amount_Lost_INR'].quantile(0.90)
df['baseline_anomaly'] = (df['Amount_Lost_INR'] >= threshold).astype(int)

# Compare baseline vs Isolation Forest on pseudo-labels
from sklearn.metrics import f1_score
baseline_f1 = f1_score(y_true, df['baseline_anomaly'], zero_division=0)
model_f1 = f1_score(y_true, df['is_anomaly'].astype(int), zero_division=0)

print(f"Baseline F1  : {baseline_f1:.4f}")
print(f"IF Model F1  : {model_f1:.4f}")
