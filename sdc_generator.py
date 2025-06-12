import os
from jinja2 import Template

def generate_sdc():
    with open("scripts/template.sdc") as file:
        tmpl = Template(file.read())

    output = tmpl.render(
        clk_name="clk",
        clk_period=10.0,
        clk_port="clk",
        input_delay=2.0,
        output_delay=2.0
    )

    # ✅ Create the constraints directory if it doesn't exist
    os.makedirs("constraints", exist_ok=True)

    with open("constraints/generated.sdc", "w") as f:
        f.write(output)

if __name__ == "__main__":
    generate_sdc()
