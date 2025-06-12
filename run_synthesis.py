import subprocess
import os
import sys
import shutil
import platform
from datetime import datetime

# === CONFIG ===
tcl_script = "run_synthesis.tcl"
log_file = "vivado_run.log"
report_dir = "reports"
folders_to_delete = ["alu_project", report_dir]
files_to_delete = ["vivado.jou", "vivado.log", log_file]

# === Detect OS + Vivado path ===
if platform.system() == "Windows":
    default_vivado = r"D:\xilinx\Vivado\2023.1\bin\vivado.bat"
else:
    default_vivado = "/opt/Xilinx/Vivado/2023.1/bin/vivado"

vivado_path = os.environ.get("VIVADO_PATH", default_vivado)

if not os.path.exists(vivado_path):
    print(f"❌ Vivado not found at: {vivado_path}")
    print("➡️  Set VIVADO_PATH environment variable to override.")
    sys.exit(1)

# === Run SDC Generator ===
import sdc_generator
sdc_generator.generate_sdc()

# === Cleanup Section ===
for folder in folders_to_delete:
    if os.path.exists(folder):
        print(f"[🧹 CLEANUP] Deleting folder: {folder}")
        shutil.rmtree(folder)

for file in files_to_delete:
    if os.path.exists(file):
        print(f"[🧹 CLEANUP] Deleting file: {file}")
        os.remove(file)

# Recreate reports folder
os.makedirs(report_dir, exist_ok=True)

# === Run Vivado Batch ===
print("[🚀 INFO] Launching Vivado synthesis...")
cmd = [vivado_path, "-mode", "batch", "-source", tcl_script]

process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    encoding="utf-8",
    errors="replace"
)

with open(log_file, "w", encoding="utf-8", errors="replace") as f:
    for line in process.stdout:
        print(line, end='')
        f.write(line)
    process.wait()

# === Optional Git Commit Logging ===
try:
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
except Exception:
    commit = "N/A"

summary_path = os.path.join(report_dir, "synthesis_summary.txt")
if os.path.exists(summary_path):
    with open(summary_path, "a", encoding="utf-8") as f:
        f.write(f"\n\n🔖 Git Commit: {commit}")
        f.write(f"\n📅 Build Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# === Post-processing: Extract Key Report Metrics ===
def extract_summary(report_file, keyword):
    if not os.path.exists(report_file):
        return "N/A"
    with open(report_file, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            if keyword in line:
                return line.strip()
    return "Not Found"

print("\n[📊 REPORT SUMMARY]")
print("Slack:       ", extract_summary(summary_path, "Slack"))
print("Worst Delay: ", extract_summary(summary_path, "Data Path Delay"))
print("LUT Usage:   ", extract_summary(summary_path, "Slice LUTs*"))
print("FF Usage:    ", extract_summary(summary_path, "Slice Registers"))
print("Power:       ", extract_summary(summary_path, "Dynamic"))

print(f"\n[✅ SUCCESS] All reports saved in: {report_dir}/")
