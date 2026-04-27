; Strict part 1 demo machine using the statement convention I / F.
; Flips each 0 to 1 and each 1 to 0, then halts on blank.
name: strict_flip_bits
init: I
final: F
blank: _
I 0 -> I 1 R
I 1 -> I 0 R
I _ -> F _ S
