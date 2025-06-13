# scripts/plot_utilization.py

import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_chart():
    csv_path = "reports/util_summary.csv"
    if not os.path.exists(csv_path):
        print("❌ Utilization summary CSV not found.")
        return

    df = pd.read_csv(csv_path)
    plt.figure(figsize=(6,4))
    plt.bar(df["Module"], df["LUTs"], label="LUTs")
    plt.bar(df["Module"], df["FFs"], bottom=df["LUTs"], label="FFs")
    plt.title("Utilization Report")
    plt.ylabel("Resource Count")
    plt.legend()
    plt.tight_layout()

    os.makedirs("plots", exist_ok=True)
    plt.savefig("plots/utilization_chart.png")
    plt.close()

if __name__ == "__main__":
    plot_chart()
