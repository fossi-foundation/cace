v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 220 200 220 280 {
lab=#net1}
N 260 170 340 170 {
lab=#net1}
N 280 170 280 220 {
lab=#net1}
N 220 220 280 220 {
lab=#net1}
N 380 200 380 280 {
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
N 160 430 260 430 {
lab=Ib}
N 120 380 180 380 {
lab=Ib}
N 180 380 180 430 {
lab=Ib}
N 120 460 120 480 {
lab=VSS}
N 300 460 300 480 {
lab=VSS}
N 220 120 220 140 {
lab=VDD}
N 380 120 380 140 {
lab=VDD}
N 100 500 380 500 {
lab=VSS}
N 120 480 120 500 {
lab=VSS}
N 300 480 300 500 {
lab=VSS}
N 100 100 380 100 {
lab=VDD}
N 380 100 380 120 {
lab=VDD}
N 220 100 220 120 {
lab=VDD}
N 120 360 120 400 {
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
N 520 130 520 170 {
lab=VDD}
N 520 170 530 170 {
lab=VDD}
N 570 170 580 170 {
lab=VDD}
N 580 130 580 170 {
lab=VDD}
N 520 130 580 130 {
lab=VDD}
N 570 130 570 140 {
lab=VDD}
N 520 440 530 440 {
lab=VSS}
N 520 440 520 480 {
lab=VSS}
N 520 480 570 480 {
lab=VSS}
N 570 470 570 480 {
lab=VSS}
N 570 440 580 440 {
lab=VSS}
N 580 440 580 480 {
lab=VSS}
N 570 480 580 480 {
lab=VSS}
N 570 400 570 410 {
lab=node}
N 570 200 570 220 {
lab=Vout}
N 520 310 530 310 {
lab=VSS}
N 520 310 520 350 {
lab=VSS}
N 520 350 570 350 {
lab=VSS}
N 570 340 570 350 {
lab=VSS}
N 570 310 580 310 {
lab=VSS}
N 580 310 580 350 {
lab=VSS}
N 570 350 580 350 {
lab=VSS}
N 570 270 570 280 {
lab=node}
C {devices/ipin.sym} 180 310 0 0 {name=p1 lab=Vp}
C {devices/ipin.sym} 420 310 0 1 {name=p2 lab=Vn}
C {devices/opin.sym} 410 240 0 0 {name=p3 lab=Vout
}
C {devices/iopin.sym} 100 100 0 1 {name=p4 lab=VDD}
C {devices/iopin.sym} 110 500 2 0 {name=p5 lab=VSS}
C {devices/ipin.sym} 120 360 1 0 {name=p6 lab=Ib}
C {sky130_fd_pr/nfet_01v8.sym} 200 310 0 0 {name=M4
L=0.5
W=20
nf=4
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {devices/lab_wire.sym} 230 310 0 1 {name=p7 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/pfet_01v8.sym} 360 170 0 0 {name=M1
L=1
W=2
nf=2
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {devices/lab_wire.sym} 390 170 0 1 {name=p9 sig_type=std_logic lab=VDD}
C {sky130_fd_pr/pfet_01v8.sym} 240 170 0 1 {name=M2
L=1
W=2
nf=2
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {devices/lab_wire.sym} 210 170 0 0 {name=p10 sig_type=std_logic lab=VDD}
C {sky130_fd_pr/nfet_01v8.sym} 400 310 0 1 {name=M3
L=0.5
W=20
nf=4
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {devices/lab_wire.sym} 370 310 0 0 {name=p11 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/nfet_01v8.sym} 280 430 0 0 {name=M5
L=1
W=2
nf=2
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {devices/lab_wire.sym} 310 430 0 1 {name=p12 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/nfet_01v8.sym} 140 430 0 1 {name=M6
L=1
W=2
nf=2
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {devices/lab_wire.sym} 110 430 0 0 {name=p13 sig_type=std_logic lab=VSS}
C {sky130_fd_pr/pfet_01v8.sym} 550 170 0 0 {name=M7
L=1
W=2
nf=2
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 550 310 0 0 {name=M8
L=0.5
W=20
nf=4
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 550 440 0 0 {name=M9
L=1
W=2
nf=2
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {devices/lab_wire.sym} 580 130 0 1 {name=p8 sig_type=std_logic lab=VDD}
C {devices/lab_wire.sym} 520 480 0 1 {name=p14 sig_type=std_logic lab=VSS}
C {devices/lab_wire.sym} 570 220 0 1 {name=p16 sig_type=std_logic lab=Vout}
C {devices/lab_wire.sym} 300 370 0 1 {name=p17 sig_type=std_logic lab=node}
C {devices/lab_wire.sym} 520 350 0 1 {name=p15 sig_type=std_logic lab=VSS}
C {devices/lab_wire.sym} 570 400 0 1 {name=p19 sig_type=std_logic lab=node}
C {devices/lab_wire.sym} 570 270 0 1 {name=p18 sig_type=std_logic lab=node}
