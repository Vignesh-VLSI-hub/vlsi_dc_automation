import pandas as pd
import re
import os

def parse_utilization(module="unknown"):
    path = "reports/synthesis_summary.txt"
    data = {"Module": [], "LUTs": [], "FFs": []}

    if not os.path.exists(path):
        print(f"❌ Report file not found: {path}")
        return

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    lut = ff = None
    for line in lines:
        if "Slice LUTs" in line:
            match = re.findall(r"\|\s+(\d+)\s+\|", line)
            if match:
                lut = int(match[0])
        elif "Slice Registers" in line:
            match = re.findall(r"\|\s+(\d+)\s+\|", line)
            if match:
                ff = int(match[0])

    if lut is not None and ff is not None:
        data["Module"].append(module if module else "unknown")  # Update this if your module name changes
        data["LUTs"].append(lut)
        data["FFs"].append(ff)
        df = pd.DataFrame(data)
        df.to_csv("reports/util_summary.csv", index=False)
        print(df)
    else:
        print("⚠️ Could not parse LUT or FF from summary report.")

if __name__ == "__main__":
    parse_utilization()
