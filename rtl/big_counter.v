module big_counter(input clk, input rst, output [31:0] out);
  reg [31:0] counter;
  always @(posedge clk or posedge rst) begin
    if (rst)
      counter <= 32'b0;
    else
      counter <= counter + 32'hFFFFF;  // Big jump = high toggling
  end
  assign out = counter;
endmodule
