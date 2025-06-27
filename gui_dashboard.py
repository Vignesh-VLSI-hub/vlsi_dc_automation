import os
import platform
import subprocess
import shutil
from datetime import datetime
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scripts import sdc_generator, parse_reports, plot_utilization

class SynthesisDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("VLSI Synthesis Dashboard")
        self.root.geometry("1000x720")
        self.root.configure(bg="#1e1e2e")

        self.file_path = StringVar()
        self.status_text = StringVar(value="Waiting for input...")
        self.summary = {}

        self.build_ui()

    def build_ui(self):
        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("TLabel", font=("Segoe UI", 10), background="#1e1e2e", foreground="white")

        top_frame = Frame(self.root, bg="#1e1e2e")
        top_frame.pack(pady=10, fill=X)

        Label(top_frame, text="Select Verilog File:", bg="#1e1e2e", fg="white").pack(side=LEFT, padx=10)
        Button(top_frame, text="Browse", command=self.browse_file).pack(side=LEFT)
        Label(top_frame, textvariable=self.file_path, bg="#1e1e2e", fg="#44ff88").pack(side=LEFT, padx=10)

        Button(top_frame, text="Run Synthesis", command=self.run_synthesis).pack(side=RIGHT, padx=20)

        self.status_label = Label(self.root, textvariable=self.status_text, bg="#1e1e2e", fg="#cccccc")
        self.status_label.pack(pady=5)

        self.info_frame = Frame(self.root, bg="#1e1e2e")
        self.info_frame.pack(pady=10, fill=X)

        self.plot_frame = Frame(self.root, bg="#1e1e2e")
        self.plot_frame.pack(pady=10, fill=BOTH, expand=True)

    def browse_file(self):
        file = filedialog.askopenfilename(filetypes=[("Verilog files", "*.v")])
        if file:
            self.file_path.set(file)
            self.status_text.set("File selected: " + os.path.basename(file))

    def run_synthesis(self):
        filepath = self.file_path.get()
        if not filepath:
            messagebox.showerror("Error", "Please select a Verilog file.")
            return

        module = os.path.splitext(os.path.basename(filepath))[0]
        top_module = module
        rtl_path = os.path.join("rtl", f"{module}.v")
        # Clean previous
        for f in ["reports", "plots"]:
            if os.path.exists(f): shutil.rmtree(f)
        for f in ["vivado.jou", "vivado.log", "vivado_run.log"]:
            if os.path.exists(f): os.remove(f)
        os.makedirs("reports", exist_ok=True)
        os.makedirs("plots", exist_ok=True)
        if os.path.abspath(filepath) != os.path.abspath(rtl_path):
            shutil.copy(filepath, rtl_path)
        with open("selected_file.txt", "w") as f:
            f.write(rtl_path)

        sdc_generator.generate_sdc(clk_name="clk", clk_period=10.0, clk_port="clk", input_delay=5.0, output_delay=5.0)

        self.status_text.set("Running synthesis...")
        self.root.update()

        with open("vivado_run.log", "w", encoding="utf-8", errors="replace") as f:
            process = subprocess.Popen([
                os.environ.get("VIVADO_PATH", r"D:\\xilinx\\Vivado\\2023.1\\bin\\vivado.bat"),
                "-mode", "batch", "-source", "run_synthesis.tcl"
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8", errors="replace")
            for line in process.stdout:
                print(line, end="")
                f.write(line)
            process.wait()

        try:
            parse_reports.parse_utilization(module=top_module)
            self.summary = parse_reports.get_latest_summary()
            self.plot_results()
            self.display_info()
            self.status_text.set("✅ Synthesis completed.")
        except Exception as e:
            self.status_text.set(f"❌ Error: {e}")

    def display_info(self):
        for widget in self.info_frame.winfo_children(): widget.destroy()
        summary = self.summary

        Label(self.info_frame, text=f"Module: {summary.get('Module', 'N/A')}").pack(anchor="w")
        Label(self.info_frame, text=f"Platform: {platform.system()}").pack(anchor="w")
        Label(self.info_frame, text=f"Slack: {summary.get('Slack')} ns").pack(anchor="w")
        Label(self.info_frame, text=f"Delay: {summary.get('Delay')} ns").pack(anchor="w")
        Label(self.info_frame, text=f"Power: {summary.get('Power')} W").pack(anchor="w")
        Label(self.info_frame, text=f"LUTs: {summary.get('LUTs')} | FFs: {summary.get('FFs')}").pack(anchor="w")

        try:
            slack_val = float(summary.get("Slack", 0))
            if slack_val >= 0:
                verdict = "✅ Slack is Positive — Design is Good"
            else:
                verdict = "❗ Slack is Negative — Optimization Needed"
        except:
            verdict = "⚠️ Slack: Unable to evaluate"

        Label(self.info_frame, text=verdict, fg="#44ff88" if '✅' in verdict else "#ff4444").pack(anchor="w")

    def plot_results(self):
        for widget in self.plot_frame.winfo_children(): widget.destroy()

        fig = plot_utilization.get_chart()  # Ensure your script returns a matplotlib.figure.Figure
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)

if __name__ == "__main__":
    root = Tk()
    app = SynthesisDashboard(root)
    root.mainloop()
