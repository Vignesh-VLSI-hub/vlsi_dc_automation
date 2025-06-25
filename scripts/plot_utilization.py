import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_chart():
    csv_file = "reports/util_summary.csv"
    if not os.path.exists(csv_file):
        print("❌ util_summary.csv not found.")
        return

    df = pd.read_csv(csv_file, encoding="utf-8")
    
    metrics = ["Slack", "Delay", "Power", "LUTs", "FFs"]

    try:
        values = [float(df[m].iloc[0]) for m in metrics]
    except ValueError:
        print("⚠️ Error: One or more values in the CSV are not numeric.")
        print(df)
        return

    module_name = df["Module"].iloc[0]

    # === Plot 1: Basic Bar Chart ===
    plt.figure(figsize=(8, 5))
    bars = plt.bar(metrics, values, color=["#4B8BBE", "#306998", "#FFE873", "#FFD43B", "#646464"])
    plt.title(f"Synthesis Metrics: {module_name}")
    plt.ylabel("Value")

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.05, f"{yval:.2f}", ha="center")

    plt.tight_layout()
    plt.savefig("plots/synthesis_plot.png")
    plt.show()

    # === Plot 2: 100% Stacked Bar Chart (Relative) ===
    plt.figure(figsize=(8, 5))
    total = sum(values)
    if total == 0:
        print("⚠️ Cannot generate percentage chart: Total value is zero.")
        return

    percentages = [(v / total) * 100 for v in values]
    plt.bar([module_name], [100], color="lightgray")  # base bar

    bottom = 0
    colors = ["#4B8BBE", "#306998", "#FFE873", "#FFD43B", "#646464"]
    for idx, perc in enumerate(percentages):
        plt.bar([module_name], [perc], bottom=bottom, label=f"{metrics[idx]} ({perc:.1f}%)", color=colors[idx])
        bottom += perc

    plt.title(f"Proportional Distribution: {module_name}")
    plt.ylabel("Percentage (%)")
    plt.legend(loc="upper right")
    plt.ylim(0, 110)
    plt.tight_layout()
    plt.savefig("plots/synthesis_percent.png")
    plt.show()
