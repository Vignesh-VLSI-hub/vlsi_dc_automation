import pandas as pd

def parse_utilization():
    data = {"Module": [], "LUTs": [], "FFs": []}
    with open("reports/util.txt") as f:
        for line in f:
            if "Slice LUTs" in line:
                data["LUTs"].append(int(line.split()[-1]))
            if "Slice Registers" in line:
                data["FFs"].append(int(line.split()[-1]))
    data["Module"].append("alu")
    df = pd.DataFrame(data)
    df.to_csv("reports/util_summary.csv", index=False)
    print(df)

if __name__ == "__main__":
    parse_utilization()