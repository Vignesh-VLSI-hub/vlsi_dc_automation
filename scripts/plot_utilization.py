# === plot_utilization.py ===
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib
matplotlib.use('Agg')

def plot_chart():
    csv_file = "reports/util_summary.csv"
    plot_dir = "plots"

    if not os.path.exists(csv_file):
        print("❌ util_summary.csv not found.")
        return

    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
        print("📁 'plots/' folder created.")

    df = pd.read_csv(csv_file, encoding="utf-8")
    metrics = ["Slack", "Delay", "Power", "LUTs", "FFs", "DSPs", "BRAM", "IO"]
    module_name = df["Module"].iloc[0]

    try:
        values = [float(df[m].iloc[0]) for m in metrics]
    except Exception as e:
        print(f"⚠️ Error reading metric values: {e}")
        print(df)
        return

    # Plot 1: Bar chart
    try:
        plt.figure(figsize=(10, 5))
        colors = sns.color_palette("viridis", len(metrics))
        bars = plt.bar(metrics, values, color=colors)
        plt.title(f"Synthesis Metrics for {module_name}")
        plt.ylabel("Values")

        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.05, f"{yval:.2f}", ha="center")

        bar_path = os.path.join(plot_dir, "synthesis_plot.png")
        plt.tight_layout()
        plt.savefig(bar_path)
        plt.close()
        print(f"✅ Saved bar chart: {bar_path}")
    except Exception as e:
        print(f"❌ Failed to save bar chart: {e}")

    # Plot 2: Percent chart
    try:
        total = sum(values)
        if total > 0:
            percents = [(v / total) * 100 for v in values]
            plt.figure(figsize=(10, 5))
            plt.bar(metrics, percents, color=colors)
            plt.title(f"Metric Distribution (%) - {module_name}")
            plt.ylabel("Percentage")

            for i, p in enumerate(percents):
                plt.text(i, p + 0.5, f"{p:.1f}%", ha="center")

            percent_path = os.path.join(plot_dir, "synthesis_percent.png")
            plt.tight_layout()
            plt.savefig(percent_path)
            plt.close()
            print(f"✅ Saved percentage chart: {percent_path}")
    except Exception as e:
        print(f"❌ Failed to save percentage chart: {e}")

    # Plot 3: Heatmap
    try:
        heat_df = pd.DataFrame([values], columns=metrics, index=[module_name])
        plt.figure(figsize=(10, 1.5))
        sns.heatmap(heat_df, annot=True, cmap="coolwarm", cbar=False, fmt=".2f")
        plt.title("Metric Heatmap")
        plt.yticks(rotation=0)

        heatmap_path = os.path.join(plot_dir, "synthesis_heatmap.png")
        plt.tight_layout()
        plt.savefig(heatmap_path)
        plt.close()
        print(f"✅ Saved heatmap: {heatmap_path}")
    except Exception as e:
        print(f"❌ Failed to save heatmap: {e}")

def get_chart():
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    csv_file = "reports/util_summary.csv"
    if not os.path.exists(csv_file):
        print("\u274c util_summary.csv not found.")
        return Figure()

    df = pd.read_csv(csv_file, encoding="utf-8")
    metrics = ["Slack", "Delay", "Power", "LUTs", "FFs", "DSPs", "BRAM", "IO"]
    module_name = df["Module"].iloc[0]

    try:
        values = [float(df[m].iloc[0]) for m in metrics]
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
def save_individual_metric_charts():
    csv_file = "reports/util_summary.csv"
    if not os.path.exists(csv_file):
        print("❌ CSV not found for individual metrics.")
        return

    df = pd.read_csv(csv_file)
    metrics = ["Slack", "Delay", "Power", "LUTs", "FFs", "DSPs", "BRAM", "IO"]
    module = df["Module"].iloc[0]

    for metric in metrics:
        if metric not in df.columns:
            continue
        try:
            value = float(df[metric].iloc[0])
        except:
            continue
        fig, ax = plt.subplots()
        ax.bar([metric], [value], color="skyblue")
        ax.set_title(f"{metric} for {module}")
        ax.set_ylabel("Value")
        for bar in ax.patches:
            ax.annotate(f"{value:.2f}", (bar.get_x() + 0.1, bar.get_height() + 0.05))
        plt.tight_layout()
        plt.savefig(f"plots/metric_{metric.lower()}.png")
        plt.close()

