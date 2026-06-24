v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 220 220 220 280 {
lab=#net1}
N 280 170 340 170 {
lab=#net1}
N 280 170 280 220 {
lab=#net1}
N 220 220 280 220 {
lab=#net1}
N 380 240 380 280 {
lab=Vout}
N 220 340 220 370 {
lab=node}
N 220 370 300 370 {
lab=node}
N 300 370 300 400 {
lab=node}
N 300 370 380 370 {
lab=node}
N 380 340 380 370 {
lab=node}
N 180 430 260 430 {
lab=Ib}
N 120 380 180 380 {
lab=Ib}
N 180 380 180 430 {
lab=Ib}
N 120 460 120 500 {
lab=VSS}
N 300 460 300 500 {
lab=VSS}
N 300 500 380 500 {
lab=VSS}
N 220 100 380 100 {
lab=VDD}
N 380 100 380 140 {
lab=VDD}
N 220 100 220 140 {
lab=VDD}
N 120 380 120 400 {
lab=Ib}
N 220 310 230 310 {
lab=VSS}
N 380 170 390 170 {
lab=VDD}
N 210 170 220 170 {
lab=VDD}
N 370 310 380 310 {
lab=VSS}
N 300 430 310 430 {
lab=VSS}
N 110 430 120 430 {
lab=VSS}
N 380 240 410 240 {
lab=Vout}
N 260 170 280 170 {
lab=#net1}
N 220 200 220 220 {
lab=#net1}
N 120 360 120 380 {
lab=Ib}
N 160 430 180 430 {
lab=Ib}
N 100 500 120 500 {
lab=VSS}
N 120 500 300 500 {
lab=VSS}
N 100 100 220 100 {
lab=VDD}
N 380 200 380 240 {
lab=Vout}
N 110 430 110 460 {lab=VSS}
N 110 460 120 460 {lab=VSS}
N 310 430 310 460 {lab=VSS}
N 300 460 310 460 {lab=VSS}
N 210 140 210 170 {lab=VDD}
N 210 140 220 140 {lab=VDD}
N 390 140 390 170 {lab=VDD}
N 380 140 390 140 {lab=VDD}
C {devices/ipin.sym} 180 310 0 0 {name=p1 lab=Vp}
C {devices/ipin.sym} 420 310 0 1 {name=p2 lab=Vn}
C {devices/opin.sym} 410 240 0 0 {name=p3 lab=Vout
}
C {devices/iopin.sym} 100 100 0 1 {name=p4 lab=VDD}
C {devices/iopin.sym} 110 500 2 0 {name=p5 lab=VSS}
C {devices/ipin.sym} 120 360 1 0 {name=p6 lab=Ib}
C {devices/lab_wire.sym} 230 310 0 1 {name=p7 sig_type=std_logic lab=VSS}
C {devices/lab_wire.sym} 370 310 0 0 {name=p11 sig_type=std_logic lab=VSS}
C {devices/lab_wire.sym} 300 370 0 1 {name=p17 sig_type=std_logic lab=node}
C {sg13g2_pr/sg13_lv_nmos.sym} 280 430 0 0 {name=M10
l=1u
w=2u
ng=2
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 360 170 0 0 {name=M11
l=1u
w=2u
ng=2
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 140 430 0 1 {name=M1
l=1u
w=2u
ng=2
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 240 170 0 1 {name=M2
l=1u
w=2u
ng=2
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 400 310 0 1 {name=M3
l=0.5u
w=20u
ng=4
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 200 310 0 0 {name=M4
l=0.5u
w=20u
ng=4
m=1
model=sg13_lv_nmos
spiceprefix=X
}
