import pandas as pd
import os
import re

def parse_utilization(module="module"):
    summary_file = f"reports/synthesis_summary_{module}.txt"
    fallback_file = "reports/synthesis_summary.txt"

    if os.path.exists(summary_file):
        file = summary_file
    elif os.path.exists(fallback_file):
        file = fallback_file
    else:
        print("❌ synthesis_summary file not found.")
        return

    with open(file, encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    summary = {
        "Module": module,
        "Slack": "N/A",
        "Delay": "N/A",
        "Power": "N/A",
        "LUTs": "N/A",
        "FFs": "N/A"
    }

    for line in lines:
        if "Worst Slack" in line:
            match = re.search(r"(-?\d+\.\d+)\s*ns", line)
            if match:
                summary["Slack"] = match.group(1)
        elif "Data Path Delay" in line:
            match = re.search(r"Data Path Delay:\s+(\d+\.\d+)", line)
            if match:
                summary["Delay"] = match.group(1)
        elif "Dynamic (W)" in line:
            match = re.search(r"Dynamic \(W\)\s+\|\s+([\d\.]+)", line)
            if match:
                summary["Power"] = match.group(1)
        elif "Slice LUTs" in line:
            match = re.findall(r"\|\s+(\d+)\s+\|", line)
            if match:
                summary["LUTs"] = match[0]
        elif "Slice Registers" in line:
            match = re.findall(r"\|\s+(\d+)\s+\|", line)
            if match:
                summary["FFs"] = match[0]

    df = pd.DataFrame([summary])
    df.to_csv("reports/util_summary.csv", index=False)
    print("[🧮 PARSED SUMMARY]")
    print(df)
    return df

# ✅ Required by GUI: reads latest summary CSV
def get_latest_summary():
    df = pd.read_csv("reports/util_summary.csv")
    return df.iloc[0].to_dict()
