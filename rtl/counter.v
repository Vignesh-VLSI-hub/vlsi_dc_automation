module counter (
    input clk,             // Clock input
    input reset,           // Active-high reset
    output reg [3:0] out   // 4-bit output counter
);

always @(posedge clk or posedge reset) begin
    if (reset)
        out <= 4'b0000;
    else
        out <= out + 1;
end

endmodule
