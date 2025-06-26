# ===============================
# Smart Vivado Synthesis Script
# Single File Accurate Execution
# ===============================

# Step 1: Create reports folder
file mkdir reports

# Step 2: Read selected file path from Python
set fp [open "selected_file.txt" r]
set selected_file_path [gets $fp]
close $fp

# Validate file
if {![file exists $selected_file_path]} {
    puts "❌ ERROR: RTL file not found: $selected_file_path"
    exit 1
}

# Step 3: Extract top module name
set top_module [regsub {\.v$} [file tail $selected_file_path] ""]

puts "🧠 Top module detected: $top_module"

# Step 4: Create project
create_project ${top_module}_project ./${top_module}_project -part xc7z020clg400-1 -force

# Step 5: Read selected Verilog file
puts "📂 Adding RTL file: $selected_file_path"
read_verilog $selected_file_path

# Step 6: Read constraints if available
if {[file exists constraints/generated.sdc]} {
    puts "⏱️  Loading SDC constraints..."
    read_xdc constraints/generated.sdc
} else {
    puts "⚠️  No constraint file found. Proceeding without SDC."
}

# Step 7: Synthesis
puts "🛠️  Running synthesis..."
synth_design -top $top_module

# Step 8: Report summary
set summary_path "reports/synthesis_summary.txt"
set fp [open $summary_path w]

puts $fp "====== VLSI SYNTHESIS SUMMARY REPORT ======"
puts $fp "Top Module       : $top_module"
puts $fp "Target Part      : xc7z020clg400-1"
puts $fp "Generated On     : [clock format [clock seconds] -format {%Y-%m-%d %H:%M:%S}]"
puts $fp "--------------------------------------------"

# Utilization
puts $fp "\n▶️ SYNTHESIS UTILIZATION"
puts $fp [report_utilization -return_string]

# Hierarchical breakdown
puts $fp "\n🔧 CELL BREAKDOWN"
puts $fp [report_utilization -hierarchical -return_string]

# Clock info
puts $fp "\n🕒 CLOCK UTILIZATION"
puts $fp [report_clock_utilization -return_string]

# Timing summary
puts $fp "\n⏱️ TIMING SUMMARY"
puts $fp [report_timing_summary -return_string]

# Worst path
puts $fp "\n⛓️ WORST SLACK PATH"
puts $fp [report_timing -max_paths 1 -sort_by slack -delay_type max -path_type summary -return_string]

# Power
puts $fp "\n⚡ POWER ESTIMATION"
puts $fp [report_power -return_string]

close $fp
puts "✅ All-in-one report written to $summary_path"

# Done
exit
