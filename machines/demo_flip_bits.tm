; Fully tested demo machine.
; Flips every 0 to 1 and every 1 to 0, then halts on blank.
name: demo_flip_bits
init: q0
final: qf
blank: _
q0 0 -> q0 1 R
q0 1 -> q0 0 R
q0 _ -> qf _ S
