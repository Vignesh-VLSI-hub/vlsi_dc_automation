module mac64 (
    input wire clk,
    input wire rst,
    input wire [63:0] a,
    input wire [63:0] b,
    input wire [63:0] acc_in,
    output reg [127:0] acc_out
);

    reg [127:0] product;
    reg [127:0] acc_stage;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            product <= 0;
            acc_stage <= 0;
            acc_out <= 0;
        end else begin
            product <= a * b;
            acc_stage <= product + acc_in;
            acc_out <= acc_stage;
        end
    end
endmodule
