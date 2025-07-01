import os
import platform
import subprocess
import shutil
import threading
from datetime import datetime
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scripts import sdc_generator, parse_reports, plot_utilization


class SynthesisDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("VLSI Synthesis Dashboard")
        self.root.geometry("1280x800")
        self.root.configure(bg="#1e1e2e")

        self.file_path = StringVar()
        self.status_text = StringVar(value="🔁 Waiting for input...")
        self.summary = {}

        self.build_ui()

    def build_ui(self):
        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 10), padding=5)
        style.configure("TLabel", font=("Segoe UI", 10), background="#1e1e2e", foreground="white")

        # === Top bar ===
        top_frame = Frame(self.root, bg="#1e1e2e")
        top_frame.pack(pady=10, fill=X)

        Label(top_frame, text="🔍 Select Verilog File:", bg="#1e1e2e", fg="white", font=("Segoe UI", 11, "bold")).pack(side=LEFT, padx=10)
        Button(top_frame, text="Browse", command=self.browse_file).pack(side=LEFT)
        Label(top_frame, textvariable=self.file_path, bg="#1e1e2e", fg="#88ff88", font=("Consolas", 10)).pack(side=LEFT, padx=10)
        Button(top_frame, text="View Charts", command=self.show_chart_gallery).pack(side=RIGHT, padx=10)
        Button(top_frame, text="Run Synthesis", command=self.run_thread).pack(side=RIGHT, padx=10)

        # === Status ===
        Label(self.root, textvariable=self.status_text, bg="#1e1e2e", fg="lightgray", font=("Segoe UI", 10, "italic")).pack(pady=5)

        # === Main Body ===
        self.main_frame = Frame(self.root, bg="#1e1e2e")
        self.main_frame.pack(fill=BOTH, expand=True)

        self.info_frame = Frame(self.main_frame, bg="#252535", bd=1, relief=SOLID)
        self.info_frame.pack(side=LEFT, fill=Y, padx=10, pady=10)

        self.plot_frame = Frame(self.main_frame, bg="#1e1e2e")
        self.plot_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)

        self.log_text = Text(self.root, height=10, bg="#0e0e0e", fg="lime", insertbackground="white", font=("Consolas", 10))
        self.log_text.pack(fill=X, padx=10, pady=5)

    def browse_file(self):
        file = filedialog.askopenfilename(filetypes=[("Verilog files", "*.v")])
        if file:
            self.file_path.set(file)
            self.status_text.set("📂 File selected: " + os.path.basename(file))

    def run_thread(self):
        thread = threading.Thread(target=self.run_synthesis)
        thread.start()

    def run_synthesis(self):
        filepath = self.file_path.get()
        if not filepath:
            messagebox.showerror("Error", "Please select a Verilog file.")
            return

        module = os.path.splitext(os.path.basename(filepath))[0]
        rtl_path = os.path.join("rtl", f"{module}.v")

        # Clean output folders
        for f in ["reports", "plots"]:
            if os.path.exists(f): shutil.rmtree(f)
        for f in ["vivado.jou", "vivado.log", "vivado_run.log"]:
            if os.path.exists(f): os.remove(f)
        for d in [".Xil", ".cache"]:
            if os.path.exists(d): shutil.rmtree(d, ignore_errors=True)

        os.makedirs("reports", exist_ok=True)
        os.makedirs("plots", exist_ok=True)

        if os.path.abspath(filepath) != os.path.abspath(rtl_path):
            shutil.copy(filepath, rtl_path)

        with open("selected_file.txt", "w") as f:
            f.write(rtl_path)

        sdc_generator.generate_sdc(clk_name="clk", clk_period=10.0, clk_port="clk", input_delay=5.0, output_delay=5.0)

        self.status_text.set("🧠 Synthesis Running...")
        self.log_text.delete(1.0, END)
        self.root.update()

        with open("vivado_run.log", "w", encoding="utf-8", errors="replace") as f:
            process = subprocess.Popen([
                os.environ.get("VIVADO_PATH", r"D:\\xilinx\\Vivado\\2023.1\\bin\\vivado.bat"),
                "-mode", "batch", "-source", "run_synthesis.tcl"
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8", errors="replace")
            for line in process.stdout:
                self.log_text.insert(END, line)
                self.log_text.see(END)
                f.write(line)
            process.wait()

        # Final report & plots
        try:
            from scripts import parse_reports, plot_utilization
            parse_reports.parse_utilization(module=module)
            plot_utilization.plot_chart()
            self.summary = parse_reports.get_latest_summary()
            self.display_info()
            self.plot_results()
            self.status_text.set("✅ Synthesis completed.")
        except Exception as e:
            self.status_text.set(f"❌ Error: {e}")

    def display_info(self):
        for widget in self.info_frame.winfo_children():
            widget.destroy()

        Label(self.info_frame, text="📊 Synthesis Summary", bg="#252535", fg="#ffffff", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=10, pady=8)

        for key in ["Module", "Slack", "Delay", "Power", "LUTs", "FFs", "DSPs", "BRAM", "IO"]:
            value = self.summary.get(key, "N/A")
            Label(self.info_frame, text=f"{key}: {value}", bg="#252535", fg="white", font=("Segoe UI", 10)).pack(anchor="w", padx=15, pady=2)

        # Slack verdict
        try:
            slack_val = float(self.summary.get("Slack", 0))
            verdict = "✅ Design is Good" if slack_val >= 0 else "❗ Slack Negative — Needs Fix"
        except:
            verdict = "⚠️ Slack unknown"

        Label(self.info_frame, text=verdict, bg="#252535", fg="#00ffaa" if '✅' in verdict else "#ff4444", font=("Segoe UI", 10, "italic")).pack(anchor="w", padx=15, pady=10)

    def plot_results(self):
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        fig = plot_utilization.get_chart()
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)

    def show_chart_gallery(self):
        import glob
        from PIL import Image, ImageTk

        chart_win = Toplevel(self.root)
        chart_win.title("📈 All Charts & Heatmaps")
        chart_win.geometry("1200x700")
        chart_win.configure(bg="#202020")

        scroll = Canvas(chart_win, bg="#202020")
        scroll.pack(fill=BOTH, expand=True, side=LEFT)

        frame = Frame(scroll, bg="#202020")
        scroll.create_window((0, 0), window=frame, anchor="nw")

        chart_files = glob.glob("plots/*.png")
        for file in chart_files:
            try:
                img = Image.open(file).resize((400, 300))
                img_tk = ImageTk.PhotoImage(img)
                label = Label(frame, image=img_tk, bg="#202020")
                label.image = img_tk
                label.pack(side=LEFT, padx=10, pady=10)
            except Exception as e:
                print(f"Image load error: {e}")

        frame.update_idletasks()
        scroll.config(scrollregion=scroll.bbox("all"))


if __name__ == "__main__":
    root = Tk()
    app = SynthesisDashboard(root)
    root.mainloop()
