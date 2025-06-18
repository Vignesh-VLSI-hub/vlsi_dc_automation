import os
import pandas as pd

def parse_utilization(module="unknown"):
    data = {"Module": [], "LUTs": [], "FFs": []}
    summary_path = "reports/synthesis_summary.txt"

    if not os.path.exists(summary_path):
        print(f"⚠️ Summary report not found: {summary_path}")
        return

    with open(summary_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if "Slice LUTs*" in line:
                try:
                    data["LUTs"].append(int(line.split("|")[2].strip()))
                except:
                    data["LUTs"].append(0)
            if "Slice Registers" in line:
                try:
                    data["FFs"].append(int(line.split("|")[2].strip()))
                except:
                    data["FFs"].append(0)

    data["Module"].append(module)

    # Append to or create CSV
    csv_path = "reports/util_summary.csv"
    df = pd.DataFrame(data)
    if os.path.exists(csv_path):
        df.to_csv(csv_path, mode="a", index=False, header=False)
    else:
        df.to_csv(csv_path, index=False)
    print(f"✅ Utilization parsed for module: {module}")
