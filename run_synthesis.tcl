# ===============================
# Smart Vivado Synthesis Script
# All-in-One Report Generator
# ===============================

# Step 1: Create reports folder
file mkdir reports

# Step 2: Detect Verilog source files
set verilog_files [glob rtl/*.v]

if {[llength $verilog_files] == 0} {
    puts "❌ ERROR: No Verilog file found in rtl/ folder."
    exit 1
}

# Step 3: Extract top module name from first .v file
# (Fixes the 'count' bug by stripping only `.v` at the end)
set top_module [regsub {\.v$} [file tail [lindex $verilog_files 0]] ""]
puts "🧠 Top module detected: $top_module"

# Step 4: Create Vivado project
create_project ${top_module}_project ./${top_module}_project -part xc7z020clg400-1 -force

# Step 5: Read all Verilog sources
foreach file $verilog_files {
    puts "📂 Adding $file"
    read_verilog $file
}

# Step 6: Read constraints if available
if {[file exists constraints/generated.sdc]} {
    puts "⏱️  Loading SDC constraints..."
    read_xdc constraints/generated.sdc
} else {
    puts "⚠️  No constraint file found. Proceeding without SDC."
}

# Step 7: Run synthesis
puts "🛠️  Running synthesis..."
synth_design -top $top_module

# Step 8: Create a single, consolidated summary report
set summary_path "reports/synthesis_summary.txt"
set fp [open $summary_path w]

puts $fp "====== VLSI SYNTHESIS SUMMARY REPORT ======"
puts $fp "Top Module       : $top_module"
puts $fp "Target Part      : xc7z020clg400-1"
puts $fp "Generated On     : [clock format [clock seconds] -format {%Y-%m-%d %H:%M:%S}]"
puts $fp "--------------------------------------------"

# Resource utilization
puts $fp "\n▶️ SYNTHESIS UTILIZATION"
puts $fp [report_utilization -return_string]

# Optional: hierarchical breakdown
puts $fp "\n🔧 CELL BREAKDOWN"
puts $fp [report_utilization -hierarchical -return_string]

# Clocking report
puts $fp "\n🕒 CLOCK UTILIZATION"
puts $fp [report_clock_utilization -return_string]

# Timing summary
puts $fp "\n⏱️ TIMING SUMMARY"
puts $fp [report_timing_summary -return_string]

# Worst slack path
puts $fp "\n⛓️ WORST SLACK PATH"
puts $fp [report_timing -max_paths 1 -sort_by slack -delay_type max -path_type summary -return_string]

# Power estimate
puts $fp "\n⚡ POWER ESTIMATION"
puts $fp [report_power -return_string]

close $fp
puts "✅ All-in-one report written to $summary_path"

# Done
exit
