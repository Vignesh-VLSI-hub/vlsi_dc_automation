# sdc_generator.py
import os
from jinja2 import Template

def generate_sdc(clk_name, clk_period, clk_port, input_delay, output_delay, out_path="constraints/generated.sdc"):
    with open("scripts/template.sdc") as file:
        tmpl = Template(file.read())

    output = tmpl.render(
        clk_name=clk_name,
        clk_period=clk_period,
        clk_port=clk_port,
        input_delay=input_delay,
        output_delay=output_delay
    )

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(output)
