import subprocess
import os
import sys
import shutil
import platform
from datetime import datetime
import yaml

# === Display OS === 
detected_os = platform.system()
print(f"[🧠 SYSTEM] Detected OS: {detected_os}")

# === Vivado Path ===
vivado_path = os.environ.get(
    "VIVADO_PATH",
    r"D:\xilinx\Vivado\2023.1\bin\vivado.bat" if detected_os == "Windows" else "/opt/Xilinx/Vivado/2023.1/bin/vivado"
)

if not os.path.exists(vivado_path):
    print(f"\n❌ Vivado not found at: {vivado_path}")
    sys.exit(1)

# === Load Configuration ===
config_file = "design_config.yaml"
if not os.path.exists(config_file):
    print(f"\n❌ Config file not found: {config_file}")
    sys.exit(1)

with open(config_file) as f:
    config = yaml.safe_load(f)
    designs = config.get("designs", [])

# === Cleanup ===
folders_to_delete = ["reports", "plots"]
files_to_delete = ["vivado.jou", "vivado.log", "vivado_run.log", "reports/util_summary.csv"]

for folder in folders_to_delete:
    if os.path.exists(folder):
        print(f"[🧹 CLEANUP] Deleting folder: {folder}")
        shutil.rmtree(folder)

for file in files_to_delete:
    if os.path.exists(file):
        print(f"[🧹 CLEANUP] Deleting file: {file}")
        os.remove(file)

os.makedirs("reports", exist_ok=True)

# === Get Verilog Files ===
rtl_files = sorted([f for f in os.listdir("rtl") if f.endswith(".v")])

# === Synthesis for each design ===
for i, design in enumerate(designs):
    try:
        rtl_index = i if i < len(rtl_files) else 0
        design_file = os.path.join("rtl", rtl_files[rtl_index])
        top_module = os.path.splitext(os.path.basename(design_file))[0]
        print(f"\n🔁 Synthesizing: {design_file} as top module '{top_module}'")

        # === Generate SDC ===
        from scripts import sdc_generator
        sdc_generator.generate_sdc(
            clk_name=design["clock_port"],
            clk_period=design["clock_period"],
            clk_port=design["clock_port"],
            input_delay=design["input_delay"],
            output_delay=design["output_delay"]
        )

        # === Run Vivado ===
        tcl_script = "run_synthesis.tcl"
        log_file = f"reports/vivado_run_{top_module}.log"
        print("[🚀 INFO] Launching Vivado...")

        with open(log_file, "w", encoding="utf-8", errors="replace") as f:
            process = subprocess.Popen(
                [vivado_path, "-mode", "batch", "-source", tcl_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding="utf-8",
                errors="replace"
            )
            for line in process.stdout:
                print(line, end='')
                f.write(line)
            process.wait()

        # === Add Git Info ===
        summary_path = "reports/synthesis_summary.txt"
        try:
            commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
        except Exception:
            commit = "N/A"

        if os.path.exists(summary_path):
            with open(summary_path, "a", encoding="utf-8") as f:
                f.write(f"\n🔖 Git Commit: {commit}")
                f.write(f"\n📅 Build Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                f.write(f"\n💻 Platform: {detected_os}\n")

        # === Summary Output ===
        def extract_summary(path, keyword):
            if not os.path.exists(path):
                return "N/A"
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if keyword in line:
                        return line.strip()
            return "Not Found"

        print("\n[📊 REPORT SUMMARY]")
        print("Slack:        ", extract_summary(summary_path, "Slack"))
        print("Worst Delay:  ", extract_summary(summary_path, "Data Path Delay"))
        print("LUT Usage:    ", extract_summary(summary_path, "Slice LUTs*"))
        print("FF Usage:     ", extract_summary(summary_path, "Slice Registers"))
        print("Power (Dyn.): ", extract_summary(summary_path, "Dynamic"))

        # === Parse Report ===
        from scripts import parse_reports
        parse_reports.parse_utilization(module=top_module)

    except Exception as e:
        print(f"❌ Error during synthesis for {top_module}: {e}")

# === Plot Chart ===
try:
    from scripts import plot_utilization
    plot_utilization.plot_chart()
except Exception as e:
    print(f"⚠️ Error in plot_utilization.py: {e}")

print("\n[✅ SUCCESS] All reports and charts saved in: reports/, plots/")