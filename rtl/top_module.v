module top_module (
    input  wire        clk,
    input  wire        sel,
    input  wire [3:0]  in1,
    input  wire [3:0]  in2,
    output wire [3:0]  result
);

    wire [3:0] mux_out;
    wire [3:0] sum;

    // Instantiate mux2
    mux2_small u_mux (
        .a(in1),
        .b(in2),
        .sel(sel),
        .y(mux_out)
    );

    // Instantiate adder
    adder u_adder (
        .a(mux_out),
        .b(in2),
        .sum(sum)
    );

    // Register output (adds Flip-Flop logic)
    reg [3:0] result_reg;
    always @(posedge clk) begin
        result_reg <= sum;
    end

    assign result = result_reg;

endmodule
