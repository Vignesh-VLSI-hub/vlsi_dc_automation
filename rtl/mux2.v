module mux2 (
  input clk,
  input sel,
  input a, b,
  output reg y
);
  always @(posedge clk)
    y <= sel ? a : b;
endmodule
