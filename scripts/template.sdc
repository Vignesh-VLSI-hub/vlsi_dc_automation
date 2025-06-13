# Create primary clock
create_clock -name {{ clk_name }} -period {{ clk_period }} [get_ports {{ clk_port }}]

# Set input delay to all inputs except clock
foreach port [get_ports *] {
    if { $port ne "{{ clk_port }}" } {
        set_input_delay {{ input_delay }} -clock {{ clk_name }} $port
    }
}

# Set output delay to all outputs except clock
foreach port [get_ports *] {
    if { $port ne "{{ clk_port }}" } {
        set_output_delay {{ output_delay }} -clock {{ clk_name }} $port
    }
}