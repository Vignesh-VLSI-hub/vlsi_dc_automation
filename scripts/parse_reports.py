# === parse_reports.py ===
import pandas as pd
import os
import re
import datetime
def parse_utilization(module="module"):
    file = "reports/synthesis_summary.txt"
    if not os.path.exists(file):
        print("\u274c synthesis_summary.txt not found.")
        return

    with open(file, encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    summary = {
        "Module": module,
        "Slack": "N/A",
        "Delay": "N/A",
        "Power": "N/A",
        "LUTs": "N/A",
        "FFs": "N/A",
        "DSPs": "N/A",
        "BRAM": "N/A",
        "IO": "N/A"
    }

    for line in lines:
        if "Worst Slack" in line:
            match = re.search(r"(-?\d+\.\d+)ns", line)
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
        elif "DSPs" in line:
            match = re.findall(r"\|\s+(\d+)\s+\|", line)
            if match:
                summary["DSPs"] = match[0]
        elif "RAMB" in line or "BRAM" in line:
            match = re.findall(r"\|\s+(\d+)\s+\|", line)
            if match:
                summary["BRAM"] = match[0]
        elif "IO Buffers" in line:
            match = re.findall(r"\|\s+(\d+)\s+\|", line)
            if match:
                summary["IO"] = match[0]

    df = pd.DataFrame([summary])
    df.to_csv("reports/util_summary.csv", index=False)
    print("[\U0001f9ee PARSED SUMMARY]")
    print(df)

def get_latest_summary():
    df = pd.read_csv("reports/util_summary.csv")
    return df.iloc[0].to_dict()
def log_to_history(df):
    history_file = "reports/history.csv"
    df["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if os.path.exists(history_file):
        pd.read_csv(history_file).append(df).to_csv(history_file, index=False)
    else:
        df.to_csv(history_file, index=False)

