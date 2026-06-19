# =====================================================================
# data_mining.py
# Superstore data mining — 2 algorithms:
#   (1) Decision Tree classification: predict whether an order line is
#       Profitable (Profit > 0). Random Forest used as a comparison.
#   (2) K-Means clustering on RFM features for customer segmentation.
#
# Run from d:\BI project\DataMining\ :   python data_mining.py
# Requires: pandas, numpy, matplotlib, scikit-learn  (all in Anaconda)
# =====================================================================
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

OUT = "outputs"
os.makedirs(OUT, exist_ok=True)

# ----- Load (latin-1 because the CSV is Windows-1252 encoded) -----
df = pd.read_csv(r"../dataset/Sample - Superstore.csv", encoding="latin-1")
df["Order Date"] = pd.to_datetime(df["Order Date"])
df["Ship Date"] = pd.to_datetime(df["Ship Date"])
print(f"Loaded {len(df)} rows, {df.shape[1]} columns.")

# =====================================================================
# ALGORITHM 1 — Decision Tree classification: Profitable (Profit > 0)?
# =====================================================================
print("\n" + "=" * 60 + "\nALGORITHM 1: Decision Tree classification\n" + "=" * 60)
df["Profitable"] = (df["Profit"] > 0).astype(int)
print("Class balance (1=profit, 0=loss):\n", df["Profitable"].value_counts(normalize=True).round(3))

feat_num = ["Sales", "Quantity", "Discount"]
feat_cat = ["Category", "Sub-Category", "Region", "Segment", "Ship Mode"]
X = pd.get_dummies(df[feat_num + feat_cat], columns=feat_cat)
y = df["Profitable"]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

dt = DecisionTreeClassifier(max_depth=4, random_state=42).fit(Xtr, ytr)
dt_pred = dt.predict(Xte)
print("\nDecision Tree accuracy:", round(accuracy_score(yte, dt_pred), 4))
print("Confusion matrix:\n", confusion_matrix(yte, dt_pred))
print("Classification report:\n", classification_report(yte, dt_pred))

rf = RandomForestClassifier(n_estimators=200, random_state=42).fit(Xtr, ytr)
print("Random Forest accuracy:", round(accuracy_score(yte, rf.predict(Xte)), 4))

# Feature importance (top 10) from the Random Forest
imp = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False).head(10)
plt.figure(figsize=(8, 5))
imp.iloc[::-1].plot.barh()
plt.title("Top 10 feature importances (Random Forest)")
plt.tight_layout()
plt.savefig(f"{OUT}/feature_importance.png", dpi=120)
plt.close()

# Visualise the decision tree (first 3 levels)
plt.figure(figsize=(22, 9))
plot_tree(dt, feature_names=list(X.columns), class_names=["Loss", "Profit"],
          filled=True, fontsize=7, max_depth=3)
plt.title("Decision Tree (depth<=3 shown)")
plt.savefig(f"{OUT}/decision_tree.png", dpi=120)
plt.close()

# =====================================================================
# ALGORITHM 2 — K-Means clustering on RFM (customer segmentation)
# =====================================================================
print("\n" + "=" * 60 + "\nALGORITHM 2: K-Means RFM segmentation\n" + "=" * 60)
snapshot = df["Order Date"].max() + pd.Timedelta(days=1)
rfm = df.groupby("Customer ID").agg(
    Recency=("Order Date", lambda s: (snapshot - s.max()).days),
    Frequency=("Order ID", "nunique"),
    Monetary=("Sales", "sum"),
).reset_index()
print(f"Computed RFM for {len(rfm)} customers.")

Xr = StandardScaler().fit_transform(rfm[["Recency", "Frequency", "Monetary"]])

# Elbow method to justify k
inertia = [KMeans(n_clusters=k, n_init=10, random_state=42).fit(Xr).inertia_ for k in range(1, 9)]
plt.figure(figsize=(7, 4))
plt.plot(range(1, 9), inertia, "o-")
plt.xlabel("k (number of clusters)")
plt.ylabel("Inertia")
plt.title("Elbow method")
plt.tight_layout()
plt.savefig(f"{OUT}/elbow.png", dpi=120)
plt.close()

K = 4
km = KMeans(n_clusters=K, n_init=10, random_state=42).fit(Xr)
rfm["Cluster"] = km.labels_

profile = rfm.groupby("Cluster")[["Recency", "Frequency", "Monetary"]].mean().round(1)
profile["Count"] = rfm["Cluster"].value_counts().sort_index()
print("\nRFM cluster profile:\n", profile)
profile.to_csv(f"{OUT}/rfm_profile.csv")

plt.figure(figsize=(7, 5))
sc = plt.scatter(rfm["Frequency"], rfm["Monetary"], c=rfm["Cluster"], cmap="viridis", s=15)
plt.xlabel("Frequency (# orders)")
plt.ylabel("Monetary (total sales)")
plt.title("Customer segments (K-Means on RFM)")
plt.colorbar(sc, label="Cluster")
plt.tight_layout()
plt.savefig(f"{OUT}/segments.png", dpi=120)
plt.close()

rfm.to_csv(f"{OUT}/rfm_customers.csv", index=False)
print("\nDone. Charts & tables saved to ./outputs/")
