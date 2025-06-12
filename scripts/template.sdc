create_clock -name {{ clk_name }} -period {{ clk_period }} [get_ports {{ clk_port }}]

# Apply delays only to non-clock ports
set input_ports [remove_from_collection [all_inputs] [get_ports {{ clk_port }}]]
set output_ports [remove_from_collection [all_outputs] [get_ports {{ clk_port }}]]

set_input_delay {{ input_delay }} -clock {{ clk_name }} $input_ports
set_output_delay {{ output_delay }} -clock {{ clk_name }} $output_ports
