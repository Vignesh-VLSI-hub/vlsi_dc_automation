import subprocess
import os
import sys
import shutil
import platform
from datetime import datetime

# === Display OS === 
detected_os = platform.system()
print(f"[🧠 SYSTEM] Detected OS: {detected_os}")

# === Vivado Path === change it if you needed
vivado_path = os.environ.get(
    "VIVADO_PATH",
    r"D:\xilinx\Vivado\2023.1\bin\vivado.bat" if detected_os == "Windows" else "/opt/Xilinx/Vivado/2023.1/bin/vivado"
)

if not os.path.exists(vivado_path):
    print(f"❌ Vivado not found at: {vivado_path}")
    sys.exit(1)

# === SDC Generator ===
try:
    import sdc_generator
    print("[⚙️ INFO] Generating constraints...")
    sdc_generator.generate_sdc()
except Exception as e:
    print(f"⚠️ Skipping SDC generation: {e}")

# === Cleanup ===
folders_to_delete = ["alu_project", "reports"]
files_to_delete = ["vivado.jou", "vivado.log", "vivado_run.log"]

for folder in folders_to_delete:
    if os.path.exists(folder):
        print(f"[🧹 CLEANUP] Deleting folder: {folder}")
        shutil.rmtree(folder)

for file in files_to_delete:
    if os.path.exists(file):
        print(f"[🧹 CLEANUP] Deleting file: {file}")
        os.remove(file)

os.makedirs("reports", exist_ok=True)

# === Run Vivado ===
print("[🚀 INFO] Launching Vivado...")
tcl_script = "run_synthesis.tcl"
log_file = "vivado_run.log"

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

# === Append Git Info ===
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

# === Extract Report Summary ===
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

# === Parse and Plot (From Scripts Folder) ===
try:
    from scripts import parse_reports
    parse_reports.parse_utilization()
except Exception as e:
    print(f"⚠️ Error in parse_reports.py: {e}")

try:
    from scripts import plot_utilization
    plot_utilization.plot_chart()
except Exception as e:
    print(f"⚠️ Error in plot_utilization.py: {e}")

print(f"\n[✅ SUCCESS] All reports and charts saved in: reports/, plots/")
