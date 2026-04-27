; Small looping machine used for timeout tests.
name: demo_loop
init: q0
final: qf
blank: _
q0 0 -> q0 0 R
q0 1 -> q0 1 R
q0 _ -> q0 _ S
