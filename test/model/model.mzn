var 1..9: T;
var 0..9: H;
var 1..9: I;
var 0..9: S;
var 1..9: E;
var 0..9: A;
var 0..9: Y;

include "alldifferent.mzn";
constraint alldifferent([T,H,I,S,E,A,Y]);

constraint 1000 * T + 100 * H + 10 * I + S
                              + 10 * I + S
         = 1000 * E + 100 * A + 10 * S + Y;

solve satisfy;
