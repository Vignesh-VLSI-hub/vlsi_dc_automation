import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("reports/util_summary.csv")

plt.figure(figsize=(6,4))
plt.bar(df["Module"], df["LUTs"], label="LUTs")
plt.bar(df["Module"], df["FFs"], bottom=df["LUTs"], label="FFs")
plt.title("Utilization Report")
plt.ylabel("Resource Count")
plt.legend()
plt.tight_layout()
plt.savefig("plots/utilization_chart.png")
plt.show()