import os
import sys
import subprocess
import shutil
import platform
from datetime import datetime
from scripts import sdc_generator, parse_reports, plot_utilization

# === OS detection ===
detected_os = platform.system()
print(f"[🧠 SYSTEM] Detected OS: {detected_os}")

# === Vivado Path ===
vivado_path = os.environ.get(
    "VIVADO_PATH",
    r"D:\xilinx\Vivado\2023.1\bin\vivado.bat" if detected_os == "Windows" else "/opt/Xilinx/Vivado/2023.1/bin/vivado"
)
if not os.path.exists(vivado_path):
    print(f"❌ Vivado not found at {vivado_path}")
    sys.exit(1)

# === Clean previous outputs ===
folders = ["reports", "plots"]
files = ["vivado.jou", "vivado.log", "vivado_run.log"]

for path in folders:
    if os.path.exists(path):
        print(f"[🧹 CLEANUP] Deleting folder: {path}")
        shutil.rmtree(path)
for file in files:
    if os.path.exists(file):
        print(f"[🧹 CLEANUP] Deleting file: {file}")
        os.remove(file)

os.makedirs("reports", exist_ok=True)
os.makedirs("plots", exist_ok=True)

# === Select Verilog file ===
rtl_files = sorted([f for f in os.listdir("rtl") if f.endswith(".v")])
if not rtl_files:
    print("❌ No .v files found in rtl/")
    sys.exit(1)

print("\nAvailable RTL files:")
for idx, file in enumerate(rtl_files, 1):
    print(f"{idx}. {file}")

try:
    choice = int(input("\nEnter file number to synthesize: ")) - 1
    selected_file = rtl_files[choice]
except (ValueError, IndexError):
    print("❌ Invalid selection")
    sys.exit(1)

top_module = os.path.splitext(selected_file)[0]
print(f"\n🔁 Synthesizing: {selected_file} as top module '{top_module}'")

# === Generate SDC ===
sdc_generator.generate_sdc(
    clk_name="clk", clk_period=10.0,
    clk_port="clk", input_delay=5.0, output_delay=5.0
)

# === Run Vivado ===
print("[🚀 INFO] Running synthesis...")
with open("vivado_run.log", "w", encoding="utf-8", errors="replace") as f:
    process = subprocess.Popen(
        [vivado_path, "-mode", "batch", "-source", "run_synthesis.tcl"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        encoding="utf-8", errors="replace"
    )
    for line in process.stdout:
        print(line, end="")
        f.write(line)
    process.wait()

# === Add Git info to report ===
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

# === Parse + Plot ===
try:
    parse_reports.parse_utilization(module=top_module)
    plot_utilization.plot_chart()
except Exception as e:
    print(f"⚠️ Error during reporting or plotting: {e}")

print("\n[✅ SUCCESS] Reports and plots saved in reports/, plots/")
