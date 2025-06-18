import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_chart():
    csv_path = "reports/util_summary.csv"
    if not os.path.exists(csv_path):
        print("❌ Utilization summary CSV not found.")
        return

    df = pd.read_csv(csv_path)
    if df.empty:
        print("⚠️ CSV is empty.")
        return

    plt.figure(figsize=(8, 5))
    plt.bar(df["Module"], df["LUTs"], label="LUTs")
    plt.bar(df["Module"], df["FFs"], bottom=df["LUTs"], label="FFs")
    plt.title("Utilization Chart")
    plt.ylabel("Resource Count")
    plt.xlabel("Modules")
    plt.legend()
    plt.tight_layout()
    os.makedirs("plots", exist_ok=True)
    plt.savefig("plots/utilization_chart.png")
    plt.show()
