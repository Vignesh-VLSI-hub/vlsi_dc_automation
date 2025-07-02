# === plot_utilization.py ===
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import yaml
from matplotlib import use as matplotlib_use
matplotlib_use('Agg')  # Use Agg backend for safe GUI plotting

def plot_chart():
    csv_file = "reports/util_summary.csv"
    if not os.path.exists(csv_file):
        print("❌ util_summary.csv not found.")
        return

    df = pd.read_csv(csv_file, encoding="utf-8")
    metrics = ["Slack", "Delay", "Power", "LUTs", "FFs", "DSPs", "BRAM", "IO"]
    module_name = df["Module"].iloc[0]

    try:
        values = [float(df[m].iloc[0]) if df[m].iloc[0] != "N/A" else 0 for m in metrics]
    except ValueError:
        print("⚠️ One or more metric values are non-numeric.")
        return

    os.makedirs("plots", exist_ok=True)

    # === Bar chart ===
    plt.figure(figsize=(10, 5))
    colors = sns.color_palette("viridis", len(metrics))
    bars = plt.bar(metrics, values, color=colors)
    plt.title(f"Synthesis Metrics for {module_name}", fontsize=14)
    plt.ylabel("Values")

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.05, f"{yval:.2f}", ha="center", fontsize=9)

    plt.tight_layout()
    plt.savefig("plots/synthesis_plot.png")
    plt.close()
    print("✅ Saved bar chart: plots/synthesis_plot.png")

    # === Heatmap ===
    heat_df = pd.DataFrame([values], columns=metrics, index=[module_name])
    plt.figure(figsize=(10, 1.5))
    sns.heatmap(heat_df, annot=True, cmap="coolwarm", cbar=False, fmt=".2f")
    plt.title("Metric Heatmap", fontsize=12)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig("plots/synthesis_heatmap.png")
    plt.close()
    print("✅ Saved heatmap: plots/synthesis_heatmap.png")

    # === User-defined metric threshold comparison plots ===
    yaml_path = "user_thresholds.yaml"
    thresholds = {}
    if os.path.exists(yaml_path):
        with open(yaml_path, "r") as f:
            thresholds = yaml.safe_load(f)

        # === Plot 4: Individual metric comparison plots ===
    for metric in metrics:
        try:
            actual = float(df[metric].iloc[0])
            threshold = float(thresholds.get(metric, actual))  # fallback to actual if missing
        except (ValueError, TypeError):
            print(f"⚠️ Skipping {metric}: invalid data")
            continue

        if not (pd.notna(actual) and pd.notna(threshold)):
            print(f"⚠️ Skipping {metric}: N/A values consider as empty value")
            continue

        plt.figure(figsize=(4, 4))
        bars = plt.bar(["Actual", "Threshold"], [actual, threshold],
                       color=["#2ecc71" if actual <= threshold else "#e74c3c", "#3498db"])
        plt.title(f"{metric} Comparison", fontsize=12)
        plt.ylabel("Value")

        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.05, f"{yval:.2f}", ha="center", fontsize=9)

        plt.tight_layout()
        filename = f"plots/{module_name}_{metric}_comparison.png"
        plt.savefig(filename)
        plt.close()
        print(f"📊 Saved metric comparison: {filename}")


def get_chart():
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    csv_file = "reports/util_summary.csv"
    if not os.path.exists(csv_file):
        print("❌ util_summary.csv not found.")
        return Figure()

    df = pd.read_csv(csv_file, encoding="utf-8")
    metrics = ["Slack", "Delay", "Power", "LUTs", "FFs", "DSPs", "BRAM", "IO"]
    module_name = df["Module"].iloc[0]

    try:
        values = [float(df[m].iloc[0]) if df[m].iloc[0] != "N/A" else 0 for m in metrics]
    except ValueError:
        values = [0] * len(metrics)

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(metrics, values, color=sns.color_palette("coolwarm", len(metrics)))
    ax.set_title(f"Synthesis Metrics for {module_name}")
    ax.set_ylabel("Values")

    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.05, f"{yval:.2f}", ha="center", fontsize=8)

    return fig
