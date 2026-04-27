; Fully tested 2-tape demo machine.
; Copies the content of tape 1 to tape 2 and halts on the first blank.
name: demo_copy_2tapes
init: q0
final: qf
blank: _
tapes: 2
q0 0,_ -> q0 0,0 R,R
q0 1,_ -> q0 1,1 R,R
q0 #,_ -> q0 #,# R,R
q0 _,_ -> qf _,_ S,S
