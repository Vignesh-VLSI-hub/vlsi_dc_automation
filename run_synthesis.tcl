# ================================================================
# Smart Vivado Synthesis Script ─ hierarchical‑ready
# ================================================================

# ── 1. Make sure we have a destination for reports ──────────────
file mkdir reports

# ── 2. Read the file that Python marked as "top" ────────────────
set fp [open "selected_file.txt" r]
set selected_file_path [gets $fp]
close $fp

if {![file exists $selected_file_path]} {
    puts "❌  RTL file not found: $selected_file_path"
    exit 1
}

# ── 3. Figure out the top‑level module name  ────────────────────
set top_module [regsub {\.v$} [file tail $selected_file_path] ""]
puts "🧠  Top module detected: $top_module"

# ── 4. Create / clean Vivado project  ───────────────────────────
create_project ${top_module}_project ./${top_module}_project \
    -part xc7z020clg400-1 -force

# ── 5. Collect **all** Verilog under rtl/ (recursively) ─────────
#     Vivado’s glob isn’t recursive, so we walk the tree.
proc recursive_glob {dir pattern} {
    set results [list]
    foreach f [glob -nocomplain -directory $dir *] {
        if {[file isdirectory $f]} {
            set results [concat $results [recursive_glob $f $pattern]]
        } elseif {[string match $pattern [file tail $f]]} {
            lappend results $f
        }
    }
    return $results
}

set rtl_files [recursive_glob "rtl" "*.v"]

if {[llength $rtl_files] == 0} {
    puts "❌  No Verilog source found under rtl/"
    exit 1
}

puts "📂  Adding RTL files:"
foreach file $rtl_files {
    puts "   • $file"
    read_verilog $file
}

# ── 6. Constraints (SDC / XDC) ──────────────────────────────────
if {[file exists constraints/generated.sdc]} {
    puts "⏱️   Loading SDC constraints..."
    read_xdc constraints/generated.sdc
} else {
    puts "⚠️   No constraint file found. Proceeding without SDC."
}

# ── 7. Synthesize ───────────────────────────────────────────────
puts "🛠️   Running synthesis..."
if {[catch {synth_design -top $top_module} synthErr]} {
    puts "❌  Synthesis failed:\n$synthErr"
    exit 1
}

# ── 8. Generate consolidated report ─────────────────────────────
set summary_path "reports/synthesis_summary_${top_module}.txt"
set fp [open $summary_path w]

puts $fp "====== VLSI SYNTHESIS SUMMARY REPORT ======"
puts $fp "Top Module       : $top_module"
puts $fp "Target Part      : xc7z020clg400-1"
puts $fp "Generated On     : [clock format [clock seconds] -format {%Y-%m-%d %H:%M:%S}]"
puts $fp "--------------------------------------------"

puts $fp "\n▶️  SYNTHESIS UTILIZATION"
puts $fp [report_utilization -return_string]

puts $fp "\n🔧  CELL BREAKDOWN"
puts $fp [report_utilization -hierarchical -return_string]

puts $fp "\n🕒  CLOCK UTILIZATION"
puts $fp [report_clock_utilization -return_string]

puts $fp "\n⏱️  TIMING SUMMARY"
puts $fp [report_timing_summary -return_string]

puts $fp "\n⛓️  WORST SLACK PATH"
puts $fp [report_timing -max_paths 1 -sort_by slack -delay_type max -path_type summary -return_string]

puts $fp "\n⚡  POWER ESTIMATION"
puts $fp [report_power -return_string]

close $fp
puts "✅  All‑in‑one report written to $summary_path"
puts "✅  SYNTHESIS_OK"   ;# <-- simple flag line for Python/G‑UI
file copy -force $summary_path "reports/synthesis_summary.txt"
exit
