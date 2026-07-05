# =====================================================================
# data_mining.py
# Superstore data mining:
#   1) Decision Tree classification for Profit/Loss, with validated rules.
#   2) K-Means RFM customer segmentation, with stable cluster names/colors.
#
# Run from D:\BI project\DataMining: python data_mining.py
# =====================================================================
from pathlib import Path
from textwrap import shorten, wrap

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    make_scorer,
    precision_score,
    recall_score,
    silhouette_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, plot_tree


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "dataset" / "Sample - Superstore.csv"
OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(exist_ok=True)

RANDOM_STATE = 42
TEST_SIZE = 0.25
TREE_MAX_DEPTH = 4
TREE_MIN_SAMPLES_LEAF = 30
LOSS_RULE_MIN_SUPPORT = 30
K = 4

FEAT_NUM = ["Sales", "Quantity", "Discount"]
FEAT_CAT = ["Category", "Sub-Category", "Region", "Segment", "Ship Mode"]

# Keep the previous business meaning of each cluster stable for reporting.
CLUSTER_NAMES = {
    0: "Trung thanh / Active",
    1: "Pho thong / Trung binh",
    2: "VIP / Champions",
    3: "Roi bo / Lost",
}

# Preserve the old viridis cluster color order instead of letting matplotlib
# remap colors differently across charts.
_VIRIDIS = plt.get_cmap("viridis")
CLUSTER_COLORS = {
    0: _VIRIDIS(0.00),
    1: _VIRIDIS(0.33),
    2: _VIRIDIS(0.66),
    3: _VIRIDIS(1.00),
}


def apply_chart_style():
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#B7C0C7",
            "axes.grid": True,
            "grid.color": "#E1E7EC",
            "grid.linewidth": 0.8,
            "axes.titleweight": "bold",
            "axes.titlesize": 13,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.frameon": False,
            "font.family": "DejaVu Sans",
        }
    )


def savefig(name: str, dpi: int = 180):
    plt.tight_layout()
    plt.savefig(OUT / name, dpi=dpi, bbox_inches="tight")
    plt.close()


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATASET, encoding="latin-1")
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Ship Date"] = pd.to_datetime(df["Ship Date"])
    return df


def plot_class_balance(y: pd.Series):
    counts = y.value_counts().reindex([0, 1])
    labels = ["Loss", "Profit"]
    colors = ["#D64545", "#26734D"]

    fig, ax = plt.subplots(figsize=(7, 4.2))
    bars = ax.bar(labels, counts.values, color=colors)
    total = counts.sum()
    for bar, count in zip(bars, counts.values):
        pct = count / total * 100
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{count:,}\n{pct:.1f}%",
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    ax.set_title("Profit/Loss Class Balance")
    ax.set_ylabel("Order lines")
    ax.set_xlabel("Class")
    ax.set_ylim(0, counts.max() * 1.18)
    savefig("class_balance.png")


def plot_confusion_matrix(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    row_pct = cm / cm.sum(axis=1, keepdims=True)

    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    image = ax.imshow(cm, cmap="Blues")
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)

    ax.set_xticks([0, 1], labels=["Predicted Loss", "Predicted Profit"])
    ax.set_yticks([0, 1], labels=["Actual Loss", "Actual Profit"])
    ax.set_title("Decision Tree Confusion Matrix")

    for i in range(2):
        for j in range(2):
            color = "white" if cm[i, j] > cm.max() * 0.55 else "#1F2A36"
            ax.text(
                j,
                i,
                f"{cm[i, j]:,}\n{row_pct[i, j] * 100:.1f}%",
                ha="center",
                va="center",
                color=color,
                fontweight="bold",
            )
    savefig("confusion_matrix.png")


def format_condition(feature: str, operator: str, threshold: float) -> str:
    for prefix in FEAT_CAT:
        marker = prefix + "_"
        if feature.startswith(marker) and abs(threshold - 0.5) < 0.001:
            value = feature[len(marker) :]
            return f"{prefix} = {value}" if operator == ">" else f"{prefix} != {value}"

    if feature == "Discount":
        return f"{feature} {operator} {threshold:.2f}"
    if feature in {"Sales", "Quantity"}:
        return f"{feature} {operator} {threshold:,.2f}"
    return f"{feature} {operator} {threshold:.2f}"


def extract_decision_rules(
    model: DecisionTreeClassifier,
    feature_names: list[str],
    X_eval: pd.DataFrame,
    y_eval: pd.Series,
) -> pd.DataFrame:
    tree = model.tree_
    leaf_ids = model.apply(X_eval)
    rows = []
    total_by_class = y_eval.value_counts().to_dict()

    def walk(node: int, conditions: list[str]):
        if tree.children_left[node] == tree.children_right[node]:
            predicted_class = int(np.argmax(tree.value[node][0]))
            predicted_label = "Profit" if predicted_class == 1 else "Loss"
            mask = leaf_ids == node
            support_test = int(mask.sum())
            correct_test = int((y_eval[mask] == predicted_class).sum())
            incorrect_test = int(support_test - correct_test)
            precision = correct_test / support_test if support_test else 0.0
            class_total = total_by_class.get(predicted_class, 0)
            recall_contribution = correct_test / class_total if class_total else 0.0

            rows.append(
                {
                    "leaf_id": node,
                    "rule": " AND ".join(conditions) if conditions else "All rows",
                    "predicted_class": predicted_label,
                    "support_train": int(tree.n_node_samples[node]),
                    "support_test": support_test,
                    "correct_test": correct_test,
                    "incorrect_test": incorrect_test,
                    "precision": round(precision, 4),
                    "recall_contribution": round(recall_contribution, 4),
                }
            )
            return

        feature = feature_names[tree.feature[node]]
        threshold = tree.threshold[node]
        left = tree.children_left[node]
        right = tree.children_right[node]
        walk(left, conditions + [format_condition(feature, "<=", threshold)])
        walk(right, conditions + [format_condition(feature, ">", threshold)])

    walk(0, [])
    rules = pd.DataFrame(rows)
    return rules.sort_values(
        ["predicted_class", "precision", "support_test"],
        ascending=[True, False, False],
    )


def plot_loss_rules(loss_rules: pd.DataFrame):
    plot_df = loss_rules[
        (loss_rules["support_test"] >= LOSS_RULE_MIN_SUPPORT)
        & (loss_rules["precision"] >= 0.8)
    ].copy()

    if plot_df.empty:
        plot_df = loss_rules.head(5).copy()
    else:
        plot_df = plot_df.head(5).copy()

    fig_height = max(3.2, 1.15 * len(plot_df) + 1.4)
    fig, ax = plt.subplots(figsize=(10.8, fig_height))
    if plot_df.empty:
        ax.text(0.5, 0.5, "No validated loss rules found", ha="center", va="center")
        ax.axis("off")
        savefig("loss_rules.png")
        return

    plot_df = plot_df.iloc[::-1]
    labels = [
        "\n".join(wrap(shorten(rule, width=92, placeholder="..."), width=46))
        for rule in plot_df["rule"]
    ]
    colors = ["#D64545" if s >= LOSS_RULE_MIN_SUPPORT else "#E8998D" for s in plot_df["support_test"]]
    bars = ax.barh(labels, plot_df["precision"], color=colors)

    for bar, (_, row) in zip(bars, plot_df.iterrows()):
        label = f"precision {row['precision']:.1%} | n={int(row['support_test'])}"
        if row["precision"] >= 0.72:
            x_pos = row["precision"] - 0.015
            ha = "right"
            color = "white"
        else:
            x_pos = row["precision"] + 0.015
            ha = "left"
            color = "#1F2A36"
        ax.text(
            x_pos,
            bar.get_y() + bar.get_height() / 2,
            label,
            va="center",
            ha=ha,
            fontsize=9,
            fontweight="bold",
            color=color,
        )

    ax.set_title("Validated Decision Rules for Loss")
    ax.set_xlabel("Precision on test set")
    ax.set_xlim(0, 1.05)
    ax.axvline(0.8, color="#6C757D", linestyle="--", linewidth=1)
    savefig("loss_rules.png")


def plot_feature_importance(importances: pd.Series):
    top = importances.sort_values(ascending=False).head(12).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    bars = ax.barh(top.index, top.values, color="#2F80ED")
    for bar, value in zip(bars, top.values):
        ax.text(
            value + top.max() * 0.015,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.3f}",
            va="center",
            fontsize=8.5,
        )
    ax.set_title("Top Feature Importances (Random Forest)")
    ax.set_xlabel("Importance")
    ax.set_xlim(0, top.max() * 1.18)
    savefig("feature_importance.png")


def run_classification(df: pd.DataFrame) -> dict:
    print("\n" + "=" * 64)
    print("ALGORITHM 1: Decision Tree classification with validated rules")
    print("=" * 64)

    df = df.copy()
    df["Profitable"] = (df["Profit"] > 0).astype(int)
    plot_class_balance(df["Profitable"])

    X = pd.get_dummies(df[FEAT_NUM + FEAT_CAT], columns=FEAT_CAT)
    y = df["Profitable"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    model = DecisionTreeClassifier(
        max_depth=TREE_MAX_DEPTH,
        min_samples_leaf=TREE_MIN_SAMPLES_LEAF,
        random_state=RANDOM_STATE,
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    baseline_accuracy = y_test.value_counts(normalize=True).max()
    accuracy = accuracy_score(y_test, y_pred)
    f1_macro = f1_score(y_test, y_pred, average="macro")

    scoring = {
        "accuracy": "accuracy",
        "f1_macro": "f1_macro",
        "loss_precision": make_scorer(precision_score, pos_label=0),
        "loss_recall": make_scorer(recall_score, pos_label=0),
    }
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cv_result = cross_validate(model, X, y, cv=cv, scoring=scoring)

    print(f"Baseline accuracy: {baseline_accuracy:.4f}")
    print(f"Decision Tree accuracy: {accuracy:.4f}")
    print(f"Decision Tree macro F1: {f1_macro:.4f}")
    print(
        "5-fold CV accuracy: "
        f"{cv_result['test_accuracy'].mean():.4f} +/- {cv_result['test_accuracy'].std():.4f}"
    )
    print("Classification report:\n", classification_report(y_test, y_pred))

    plot_confusion_matrix(y_test, y_pred)

    fig, ax = plt.subplots(figsize=(24, 11))
    plot_tree(
        model,
        feature_names=list(X.columns),
        class_names=["Loss", "Profit"],
        filled=True,
        fontsize=7,
        rounded=True,
        ax=ax,
    )
    ax.set_title("Decision Tree for Profit/Loss Rules")
    savefig("decision_tree.png", dpi=180)

    rules = extract_decision_rules(model, list(X.columns), X_test, y_test)
    rules.to_csv(OUT / "decision_rules.csv", index=False)
    loss_rules_all = rules[rules["predicted_class"] == "Loss"].sort_values(
        ["precision", "support_test"], ascending=[False, False]
    )
    loss_rules = loss_rules_all[loss_rules_all["support_test"] >= LOSS_RULE_MIN_SUPPORT]
    if loss_rules.empty:
        loss_rules = loss_rules_all
    loss_rules.to_csv(OUT / "loss_rules.csv", index=False)
    plot_loss_rules(loss_rules)

    rf = RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE)
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    rf_accuracy = accuracy_score(y_test, rf_pred)
    importances = pd.Series(rf.feature_importances_, index=X.columns)
    plot_feature_importance(importances)

    print(f"Random Forest benchmark accuracy: {rf_accuracy:.4f}")
    print("\nTop validated loss rules:")
    print(loss_rules.head(5)[["rule", "support_test", "precision"]].to_string(index=False))

    return {
        "baseline_accuracy": baseline_accuracy,
        "tree_accuracy": accuracy,
        "tree_f1_macro": f1_macro,
        "rf_accuracy": rf_accuracy,
        "cv_accuracy_mean": cv_result["test_accuracy"].mean(),
        "cv_accuracy_std": cv_result["test_accuracy"].std(),
        "cv_loss_precision_mean": cv_result["test_loss_precision"].mean(),
        "cv_loss_recall_mean": cv_result["test_loss_recall"].mean(),
    }


def build_rfm(df: pd.DataFrame) -> pd.DataFrame:
    snapshot = df["Order Date"].max() + pd.Timedelta(days=1)
    return (
        df.groupby("Customer ID")
        .agg(
            Recency=("Order Date", lambda s: (snapshot - s.max()).days),
            Frequency=("Order ID", "nunique"),
            Monetary=("Sales", "sum"),
        )
        .reset_index()
    )


def plot_elbow_silhouette(X_scaled: np.ndarray):
    ks = range(2, 9)
    inertia = []
    silhouettes = []
    for k in ks:
        model = KMeans(n_clusters=k, n_init=10, random_state=RANDOM_STATE)
        labels = model.fit_predict(X_scaled)
        inertia.append(model.inertia_)
        silhouettes.append(silhouette_score(X_scaled, labels))

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    axes[0].plot(list(ks), inertia, marker="o", color="#2F80ED")
    axes[0].axvline(K, color="#D64545", linestyle="--", linewidth=1.2)
    axes[0].set_title("Elbow Method")
    axes[0].set_xlabel("k")
    axes[0].set_ylabel("Inertia")

    axes[1].plot(list(ks), silhouettes, marker="o", color="#26734D")
    axes[1].axvline(K, color="#D64545", linestyle="--", linewidth=1.2)
    axes[1].set_title("Silhouette Score")
    axes[1].set_xlabel("k")
    axes[1].set_ylabel("Score")
    savefig("elbow_silhouette.png")

    # Keep the old single elbow file too, so old report references do not break.
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(list(range(1, 9)), [np.nan] + inertia, "o-", color="#2F80ED")
    ax.axvline(K, color="#D64545", linestyle="--", linewidth=1.2)
    ax.set_xlabel("k (number of clusters)")
    ax.set_ylabel("Inertia")
    ax.set_title("Elbow Method")
    savefig("elbow.png")

    return dict(zip(ks, silhouettes))


def plot_segments(rfm: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 5.4))
    for cluster in sorted(CLUSTER_NAMES):
        subset = rfm[rfm["Cluster"] == cluster]
        ax.scatter(
            subset["Frequency"],
            subset["Monetary"],
            s=28,
            alpha=0.78,
            color=CLUSTER_COLORS[cluster],
            edgecolor="white",
            linewidth=0.4,
            label=f"{cluster}: {CLUSTER_NAMES[cluster]}",
        )

    ax.set_title("Customer Segments (K-Means on RFM)")
    ax.set_xlabel("Frequency (# orders)")
    ax.set_ylabel("Monetary (total sales)")
    ax.legend(loc="best", fontsize=8)
    savefig("segments.png")


def plot_rfm_profile(profile: pd.DataFrame):
    metrics = ["Recency", "Frequency", "Monetary"]
    heat = profile[metrics].copy()
    heat["Recency"] = -heat["Recency"]  # lower recency is better
    scaled = (heat - heat.mean()) / heat.std(ddof=0)

    fig, ax = plt.subplots(figsize=(9.8, 5.4))
    image = ax.imshow(scaled[metrics], cmap="RdYlGn", aspect="auto", vmin=-1.6, vmax=1.6)
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04, label="Relative strength")

    x_labels = ["Recency\n(lower better)", "Frequency", "Monetary"]
    y_labels = [
        f"{int(row.Cluster)}: {row.SegmentName}\nn={int(row.Count)}"
        for row in profile.itertuples()
    ]
    ax.set_xticks(range(len(metrics)), labels=x_labels)
    ax.set_yticks(range(len(profile)), labels=y_labels)
    ax.set_title("RFM Cluster Profile")

    for i, row in enumerate(profile.itertuples()):
        values = [row.Recency, row.Frequency, row.Monetary]
        for j, value in enumerate(values):
            text = f"{value:,.1f}" if j != 2 else f"{value:,.0f}"
            ax.text(j, i, text, ha="center", va="center", fontweight="bold", fontsize=8.5)

    savefig("rfm_profile.png")


def run_rfm_clustering(df: pd.DataFrame) -> dict:
    print("\n" + "=" * 64)
    print("ALGORITHM 2: K-Means RFM segmentation")
    print("=" * 64)

    rfm = build_rfm(df)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(rfm[["Recency", "Frequency", "Monetary"]])

    silhouettes = plot_elbow_silhouette(X_scaled)
    km = KMeans(n_clusters=K, n_init=10, random_state=RANDOM_STATE)
    rfm["Cluster"] = km.fit_predict(X_scaled)
    rfm["SegmentName"] = rfm["Cluster"].map(CLUSTER_NAMES)

    profile = (
        rfm.groupby("Cluster")[["Recency", "Frequency", "Monetary"]]
        .mean()
        .round(1)
        .reset_index()
    )
    profile["Count"] = profile["Cluster"].map(rfm["Cluster"].value_counts()).astype(int)
    profile["SegmentName"] = profile["Cluster"].map(CLUSTER_NAMES)
    profile = profile[["Cluster", "SegmentName", "Recency", "Frequency", "Monetary", "Count"]]

    print(f"Computed RFM for {len(rfm)} customers.")
    print("\nRFM cluster profile:\n", profile.to_string(index=False))
    print(f"Silhouette score for k=4: {silhouettes[K]:.4f}")

    profile.to_csv(OUT / "rfm_profile.csv", index=False)
    rfm.to_csv(OUT / "rfm_customers.csv", index=False)
    plot_segments(rfm)
    plot_rfm_profile(profile)

    return {
        "customers": len(rfm),
        "k": K,
        "silhouette_k4": silhouettes[K],
    }


def write_summary(classification: dict, clustering: dict):
    lines = [
        "Superstore Data Mining Summary",
        "=" * 34,
        "",
        "Decision Tree classification",
        f"- Baseline accuracy: {classification['baseline_accuracy']:.4f}",
        f"- Test accuracy: {classification['tree_accuracy']:.4f}",
        f"- Test macro F1: {classification['tree_f1_macro']:.4f}",
        (
            "- 5-fold CV accuracy: "
            f"{classification['cv_accuracy_mean']:.4f} +/- {classification['cv_accuracy_std']:.4f}"
        ),
        f"- CV loss precision: {classification['cv_loss_precision_mean']:.4f}",
        f"- CV loss recall: {classification['cv_loss_recall_mean']:.4f}",
        f"- Random Forest benchmark accuracy: {classification['rf_accuracy']:.4f}",
        "",
        "K-Means RFM segmentation",
        f"- Customers: {clustering['customers']}",
        f"- k: {clustering['k']}",
        f"- Silhouette score for k=4: {clustering['silhouette_k4']:.4f}",
        "",
        "Stable cluster names",
    ]
    for cluster, name in CLUSTER_NAMES.items():
        lines.append(f"- Cluster {cluster}: {name}")

    (OUT / "model_summary.txt").write_text("\n".join(lines), encoding="utf-8")


def main():
    apply_chart_style()
    df = load_data()
    print(f"Loaded {len(df)} rows, {df.shape[1]} columns.")

    classification = run_classification(df)
    clustering = run_rfm_clustering(df)
    write_summary(classification, clustering)
    print(f"\nDone. Charts and tables saved to {OUT}")


if __name__ == "__main__":
    main()
