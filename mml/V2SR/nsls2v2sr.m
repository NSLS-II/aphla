function varargout = v2srlattice(varargin)

global THERING 

if nargin >=1
   Energy = varargin{1};
else
  Energy = 200e6;
end

% BEG_ = marker('BEG', 'IdentityPass');

D_0_cav = drift('DRIFT', inf, 'DriftPass');
cav = rfcavity('RFCAVITY', 0.0, 5000000.0, 499.681, 1320, CavityPass); %s= inf
sh1g2c30a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g2c30a = marker('BPM', 'IdentityPass'); %s= inf
qh1g2c30a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g2c30a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqhhg2c30a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g2c30a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g2c30a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh3g2c30a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g2c30a = marker('BPM', 'IdentityPass'); %s= inf
sh4g2c30a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ch2g2c30a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
cm1g4c30a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qm1g4c30a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c30a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c30a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c30a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c30b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c30b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c30b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c30b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c30b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c30b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ql3g6c30b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g6c30b = marker('BPM', 'IdentityPass'); %s= inf
sl3g6c30b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g6c30b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql2g6c30b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
sl2g6c30b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g6c30b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql1g6c30b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g6c30b = marker('BPM', 'IdentityPass'); %s= inf
sl1g6c30b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
sl1g2c01a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g2c01a = marker('BPM', 'IdentityPass'); %s= inf
ql1g2c01a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g2c01a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl2g2c01a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
ql2g2c01a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g2c01a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl3g2c01a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g2c01a = marker('BPM', 'IdentityPass'); %s= inf
ql3g2c01a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c01a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqmhg4c01a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qm1g4c01a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c01a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c01a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c01a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c01b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c01b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c01b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c01b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c01b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c01b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ch2g6c01b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
sh4g6c01b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g6c01b = marker('BPM', 'IdentityPass'); %s= inf
qh3g6c01b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g6c01b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g6c01b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g6c01b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qh1g6c01b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g6c01b = marker('BPM', 'IdentityPass'); %s= inf
sh1g6c01b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
sh1g2c02a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g2c02a = marker('BPM', 'IdentityPass'); %s= inf
qh1g2c02a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g2c02a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqhhg2c02a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g2c02a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g2c02a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh3g2c02a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g2c02a = marker('BPM', 'IdentityPass'); %s= inf
sh4g2c02a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ch2g2c02a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
cm1g4c02a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qm1g4c02a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c02a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c02a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c02a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c02b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c02b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c02b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c02b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c02b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c02b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ql3g6c02b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g6c02b = marker('BPM', 'IdentityPass'); %s= inf
sl3g6c02b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g6c02b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql2g6c02b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
sl2g6c02b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g6c02b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql1g6c02b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g6c02b = marker('BPM', 'IdentityPass'); %s= inf
sl1g6c02b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
sl1g2c03a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g2c03a = marker('BPM', 'IdentityPass'); %s= inf
ql1g2c03a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g2c03a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl2g2c03a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
ql2g2c03a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g2c03a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl3g2c03a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g2c03a = marker('BPM', 'IdentityPass'); %s= inf
ql3g2c03a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c03a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqmhg4c03a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qm1g4c03a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c03a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c03a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c03a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c03b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c03b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c03b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c03b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c03b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c03b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ch2g6c03b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
sh4g6c03b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g6c03b = marker('BPM', 'IdentityPass'); %s= inf
qh3g6c03b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g6c03b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g6c03b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g6c03b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qh1g6c03b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g6c03b = marker('BPM', 'IdentityPass'); %s= inf
sh1g6c03b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
sh1g2c04a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g2c04a = marker('BPM', 'IdentityPass'); %s= inf
qh1g2c04a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g2c04a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqhhg2c04a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g2c04a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g2c04a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh3g2c04a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g2c04a = marker('BPM', 'IdentityPass'); %s= inf
sh4g2c04a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ch2g2c04a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
cm1g4c04a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qm1g4c04a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c04a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c04a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c04a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c04b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c04b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c04b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c04b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c04b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c04b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ql3g6c04b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g6c04b = marker('BPM', 'IdentityPass'); %s= inf
sl3g6c04b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g6c04b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql2g6c04b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
sl2g6c04b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g6c04b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql1g6c04b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g6c04b = marker('BPM', 'IdentityPass'); %s= inf
sl1g6c04b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
sl1g2c05a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g2c05a = marker('BPM', 'IdentityPass'); %s= inf
ql1g2c05a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g2c05a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl2g2c05a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
ql2g2c05a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g2c05a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl3g2c05a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g2c05a = marker('BPM', 'IdentityPass'); %s= inf
ql3g2c05a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c05a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqmhg4c05a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qm1g4c05a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c05a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c05a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c05a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c05b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c05b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c05b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c05b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c05b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c05b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ch2g6c05b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
sh4g6c05b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g6c05b = marker('BPM', 'IdentityPass'); %s= inf
qh3g6c05b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g6c05b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g6c05b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g6c05b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qh1g6c05b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g6c05b = marker('BPM', 'IdentityPass'); %s= inf
sh1g6c05b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
sh1g2c06a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g2c06a = marker('BPM', 'IdentityPass'); %s= inf
qh1g2c06a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g2c06a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqhhg2c06a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g2c06a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g2c06a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh3g2c06a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g2c06a = marker('BPM', 'IdentityPass'); %s= inf
sh4g2c06a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ch2g2c06a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
cm1g4c06a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qm1g4c06a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c06a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c06a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c06a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c06b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c06b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c06b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c06b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c06b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c06b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ql3g6c06b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g6c06b = marker('BPM', 'IdentityPass'); %s= inf
sl3g6c06b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g6c06b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql2g6c06b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
sl2g6c06b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g6c06b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql1g6c06b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g6c06b = marker('BPM', 'IdentityPass'); %s= inf
sl1g6c06b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
sl1g2c07a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g2c07a = marker('BPM', 'IdentityPass'); %s= inf
ql1g2c07a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g2c07a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl2g2c07a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
ql2g2c07a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g2c07a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl3g2c07a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g2c07a = marker('BPM', 'IdentityPass'); %s= inf
ql3g2c07a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c07a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqmhg4c07a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qm1g4c07a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c07a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c07a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c07a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c07b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c07b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c07b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c07b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c07b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c07b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ch2g6c07b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
sh4g6c07b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g6c07b = marker('BPM', 'IdentityPass'); %s= inf
qh3g6c07b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g6c07b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g6c07b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g6c07b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qh1g6c07b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g6c07b = marker('BPM', 'IdentityPass'); %s= inf
sh1g6c07b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
sh1g2c08a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g2c08a = marker('BPM', 'IdentityPass'); %s= inf
qh1g2c08a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g2c08a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqhhg2c08a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g2c08a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g2c08a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh3g2c08a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g2c08a = marker('BPM', 'IdentityPass'); %s= inf
sh4g2c08a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ch2g2c08a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
cm1g4c08a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qm1g4c08a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c08a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c08a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c08a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c08b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c08b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c08b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c08b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c08b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c08b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ql3g6c08b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g6c08b = marker('BPM', 'IdentityPass'); %s= inf
sl3g6c08b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g6c08b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql2g6c08b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
sl2g6c08b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g6c08b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql1g6c08b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g6c08b = marker('BPM', 'IdentityPass'); %s= inf
sl1g6c08b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
sl1g2c09a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g2c09a = marker('BPM', 'IdentityPass'); %s= inf
ql1g2c09a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g2c09a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl2g2c09a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
ql2g2c09a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g2c09a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl3g2c09a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g2c09a = marker('BPM', 'IdentityPass'); %s= inf
ql3g2c09a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c09a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqmhg4c09a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qm1g4c09a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c09a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c09a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c09a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c09b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c09b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c09b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c09b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c09b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c09b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ch2g6c09b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
sh4g6c09b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g6c09b = marker('BPM', 'IdentityPass'); %s= inf
qh3g6c09b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g6c09b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g6c09b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g6c09b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qh1g6c09b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g6c09b = marker('BPM', 'IdentityPass'); %s= inf
sh1g6c09b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
sh1g2c10a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g2c10a = marker('BPM', 'IdentityPass'); %s= inf
qh1g2c10a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g2c10a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqhhg2c10a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g2c10a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g2c10a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh3g2c10a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g2c10a = marker('BPM', 'IdentityPass'); %s= inf
sh4g2c10a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ch2g2c10a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
cm1g4c10a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qm1g4c10a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c10a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c10a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c10a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c10b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c10b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c10b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c10b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c10b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c10b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ql3g6c10b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g6c10b = marker('BPM', 'IdentityPass'); %s= inf
sl3g6c10b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g6c10b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql2g6c10b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
sl2g6c10b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g6c10b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql1g6c10b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g6c10b = marker('BPM', 'IdentityPass'); %s= inf
sl1g6c10b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
sl1g2c11a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g2c11a = marker('BPM', 'IdentityPass'); %s= inf
ql1g2c11a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g2c11a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl2g2c11a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
ql2g2c11a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g2c11a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl3g2c11a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g2c11a = marker('BPM', 'IdentityPass'); %s= inf
ql3g2c11a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c11a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqmhg4c11a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qm1g4c11a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c11a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c11a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c11a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c11b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c11b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c11b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c11b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c11b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c11b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ch2g6c11b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
sh4g6c11b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g6c11b = marker('BPM', 'IdentityPass'); %s= inf
qh3g6c11b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g6c11b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g6c11b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g6c11b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qh1g6c11b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g6c11b = marker('BPM', 'IdentityPass'); %s= inf
sh1g6c11b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
sh1g2c12a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g2c12a = marker('BPM', 'IdentityPass'); %s= inf
qh1g2c12a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g2c12a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqhhg2c12a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g2c12a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g2c12a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh3g2c12a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g2c12a = marker('BPM', 'IdentityPass'); %s= inf
sh4g2c12a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ch2g2c12a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
cm1g4c12a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qm1g4c12a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c12a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c12a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c12a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c12b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c12b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c12b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c12b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c12b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c12b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ql3g6c12b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g6c12b = marker('BPM', 'IdentityPass'); %s= inf
sl3g6c12b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g6c12b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql2g6c12b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
sl2g6c12b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g6c12b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql1g6c12b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g6c12b = marker('BPM', 'IdentityPass'); %s= inf
sl1g6c12b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
sl1g2c13a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g2c13a = marker('BPM', 'IdentityPass'); %s= inf
ql1g2c13a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g2c13a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl2g2c13a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
ql2g2c13a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g2c13a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl3g2c13a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g2c13a = marker('BPM', 'IdentityPass'); %s= inf
ql3g2c13a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c13a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqmhg4c13a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qm1g4c13a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c13a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c13a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c13a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c13b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c13b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c13b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c13b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c13b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c13b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ch2g6c13b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
sh4g6c13b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g6c13b = marker('BPM', 'IdentityPass'); %s= inf
qh3g6c13b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g6c13b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g6c13b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g6c13b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qh1g6c13b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g6c13b = marker('BPM', 'IdentityPass'); %s= inf
sh1g6c13b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
sh1g2c14a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g2c14a = marker('BPM', 'IdentityPass'); %s= inf
qh1g2c14a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g2c14a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqhhg2c14a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g2c14a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g2c14a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh3g2c14a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g2c14a = marker('BPM', 'IdentityPass'); %s= inf
sh4g2c14a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ch2g2c14a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
cm1g4c14a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qm1g4c14a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c14a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c14a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c14a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c14b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c14b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c14b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c14b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c14b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c14b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ql3g6c14b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g6c14b = marker('BPM', 'IdentityPass'); %s= inf
sl3g6c14b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g6c14b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql2g6c14b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
sl2g6c14b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g6c14b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql1g6c14b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g6c14b = marker('BPM', 'IdentityPass'); %s= inf
sl1g6c14b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
sl1g2c15a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g2c15a = marker('BPM', 'IdentityPass'); %s= inf
ql1g2c15a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g2c15a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl2g2c15a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
ql2g2c15a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g2c15a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl3g2c15a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g2c15a = marker('BPM', 'IdentityPass'); %s= inf
ql3g2c15a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c15a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqmhg4c15a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qm1g4c15a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c15a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c15a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c15a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c15b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c15b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c15b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c15b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c15b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c15b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ch2g6c15b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
sh4g6c15b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g6c15b = marker('BPM', 'IdentityPass'); %s= inf
qh3g6c15b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g6c15b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g6c15b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g6c15b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qh1g6c15b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g6c15b = marker('BPM', 'IdentityPass'); %s= inf
sh1g6c15b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
sh1g2c16a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g2c16a = marker('BPM', 'IdentityPass'); %s= inf
qh1g2c16a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g2c16a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqhhg2c16a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g2c16a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g2c16a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh3g2c16a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g2c16a = marker('BPM', 'IdentityPass'); %s= inf
sh4g2c16a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ch2g2c16a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
cm1g4c16a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qm1g4c16a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c16a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c16a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c16a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c16b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c16b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c16b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c16b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c16b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c16b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ql3g6c16b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g6c16b = marker('BPM', 'IdentityPass'); %s= inf
sl3g6c16b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g6c16b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql2g6c16b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
sl2g6c16b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g6c16b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql1g6c16b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g6c16b = marker('BPM', 'IdentityPass'); %s= inf
sl1g6c16b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
sl1g2c17a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g2c17a = marker('BPM', 'IdentityPass'); %s= inf
ql1g2c17a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g2c17a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl2g2c17a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
ql2g2c17a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g2c17a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl3g2c17a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g2c17a = marker('BPM', 'IdentityPass'); %s= inf
ql3g2c17a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c17a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqmhg4c17a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qm1g4c17a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c17a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c17a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c17a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c17b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c17b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c17b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c17b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c17b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c17b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ch2g6c17b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
sh4g6c17b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g6c17b = marker('BPM', 'IdentityPass'); %s= inf
qh3g6c17b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g6c17b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g6c17b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g6c17b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qh1g6c17b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g6c17b = marker('BPM', 'IdentityPass'); %s= inf
sh1g6c17b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
sh1g2c18a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g2c18a = marker('BPM', 'IdentityPass'); %s= inf
qh1g2c18a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g2c18a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqhhg2c18a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g2c18a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g2c18a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh3g2c18a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g2c18a = marker('BPM', 'IdentityPass'); %s= inf
sh4g2c18a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ch2g2c18a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
cm1g4c18a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qm1g4c18a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c18a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c18a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c18a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c18b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c18b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c18b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c18b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c18b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c18b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ql3g6c18b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g6c18b = marker('BPM', 'IdentityPass'); %s= inf
sl3g6c18b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g6c18b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql2g6c18b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
sl2g6c18b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g6c18b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql1g6c18b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g6c18b = marker('BPM', 'IdentityPass'); %s= inf
sl1g6c18b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
sl1g2c19a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g2c19a = marker('BPM', 'IdentityPass'); %s= inf
ql1g2c19a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g2c19a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl2g2c19a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
ql2g2c19a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g2c19a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl3g2c19a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g2c19a = marker('BPM', 'IdentityPass'); %s= inf
ql3g2c19a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c19a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqmhg4c19a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qm1g4c19a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c19a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c19a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c19a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c19b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c19b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c19b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c19b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c19b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c19b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ch2g6c19b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
sh4g6c19b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g6c19b = marker('BPM', 'IdentityPass'); %s= inf
qh3g6c19b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g6c19b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g6c19b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g6c19b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qh1g6c19b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g6c19b = marker('BPM', 'IdentityPass'); %s= inf
sh1g6c19b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
sh1g2c20a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g2c20a = marker('BPM', 'IdentityPass'); %s= inf
qh1g2c20a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g2c20a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqhhg2c20a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g2c20a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g2c20a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh3g2c20a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g2c20a = marker('BPM', 'IdentityPass'); %s= inf
sh4g2c20a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ch2g2c20a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
cm1g4c20a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qm1g4c20a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c20a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c20a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c20a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c20b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c20b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c20b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c20b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c20b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c20b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ql3g6c20b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g6c20b = marker('BPM', 'IdentityPass'); %s= inf
sl3g6c20b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g6c20b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql2g6c20b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
sl2g6c20b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g6c20b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql1g6c20b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g6c20b = marker('BPM', 'IdentityPass'); %s= inf
sl1g6c20b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
sl1g2c21a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g2c21a = marker('BPM', 'IdentityPass'); %s= inf
ql1g2c21a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g2c21a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl2g2c21a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
ql2g2c21a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g2c21a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl3g2c21a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g2c21a = marker('BPM', 'IdentityPass'); %s= inf
ql3g2c21a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c21a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqmhg4c21a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qm1g4c21a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c21a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c21a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c21a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c21b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c21b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c21b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c21b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c21b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c21b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ch2g6c21b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
sh4g6c21b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g6c21b = marker('BPM', 'IdentityPass'); %s= inf
qh3g6c21b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g6c21b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g6c21b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g6c21b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qh1g6c21b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g6c21b = marker('BPM', 'IdentityPass'); %s= inf
sh1g6c21b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
sh1g2c22a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g2c22a = marker('BPM', 'IdentityPass'); %s= inf
qh1g2c22a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g2c22a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqhhg2c22a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g2c22a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g2c22a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh3g2c22a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g2c22a = marker('BPM', 'IdentityPass'); %s= inf
sh4g2c22a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ch2g2c22a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
cm1g4c22a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qm1g4c22a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c22a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c22a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c22a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c22b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c22b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c22b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c22b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c22b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c22b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ql3g6c22b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g6c22b = marker('BPM', 'IdentityPass'); %s= inf
sl3g6c22b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g6c22b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql2g6c22b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
sl2g6c22b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g6c22b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql1g6c22b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g6c22b = marker('BPM', 'IdentityPass'); %s= inf
sl1g6c22b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
sl1g2c23a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g2c23a = marker('BPM', 'IdentityPass'); %s= inf
ql1g2c23a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g2c23a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl2g2c23a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
ql2g2c23a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g2c23a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl3g2c23a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g2c23a = marker('BPM', 'IdentityPass'); %s= inf
ql3g2c23a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c23a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqmhg4c23a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qm1g4c23a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c23a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c23a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c23a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c23b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c23b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c23b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c23b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c23b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c23b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ch2g6c23b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
sh4g6c23b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g6c23b = marker('BPM', 'IdentityPass'); %s= inf
qh3g6c23b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g6c23b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g6c23b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g6c23b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qh1g6c23b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g6c23b = marker('BPM', 'IdentityPass'); %s= inf
sh1g6c23b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
sh1g2c24a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g2c24a = marker('BPM', 'IdentityPass'); %s= inf
qh1g2c24a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g2c24a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqhhg2c24a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g2c24a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g2c24a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh3g2c24a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g2c24a = marker('BPM', 'IdentityPass'); %s= inf
sh4g2c24a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ch2g2c24a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
cm1g4c24a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qm1g4c24a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c24a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c24a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c24a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c24b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c24b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c24b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c24b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c24b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c24b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ql3g6c24b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g6c24b = marker('BPM', 'IdentityPass'); %s= inf
sl3g6c24b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g6c24b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql2g6c24b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
sl2g6c24b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g6c24b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql1g6c24b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g6c24b = marker('BPM', 'IdentityPass'); %s= inf
sl1g6c24b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
sl1g2c25a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g2c25a = marker('BPM', 'IdentityPass'); %s= inf
ql1g2c25a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g2c25a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl2g2c25a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
ql2g2c25a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g2c25a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl3g2c25a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g2c25a = marker('BPM', 'IdentityPass'); %s= inf
ql3g2c25a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c25a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqmhg4c25a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qm1g4c25a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c25a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c25a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c25a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c25b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c25b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c25b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c25b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c25b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c25b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ch2g6c25b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
sh4g6c25b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g6c25b = marker('BPM', 'IdentityPass'); %s= inf
qh3g6c25b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g6c25b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g6c25b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g6c25b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qh1g6c25b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g6c25b = marker('BPM', 'IdentityPass'); %s= inf
sh1g6c25b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
sh1g2c26a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g2c26a = marker('BPM', 'IdentityPass'); %s= inf
qh1g2c26a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g2c26a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqhhg2c26a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g2c26a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g2c26a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh3g2c26a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g2c26a = marker('BPM', 'IdentityPass'); %s= inf
sh4g2c26a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ch2g2c26a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
cm1g4c26a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qm1g4c26a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c26a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c26a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c26a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c26b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c26b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c26b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c26b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c26b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c26b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ql3g6c26b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g6c26b = marker('BPM', 'IdentityPass'); %s= inf
sl3g6c26b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g6c26b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql2g6c26b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
sl2g6c26b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g6c26b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql1g6c26b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g6c26b = marker('BPM', 'IdentityPass'); %s= inf
sl1g6c26b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
sl1g2c27a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g2c27a = marker('BPM', 'IdentityPass'); %s= inf
ql1g2c27a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g2c27a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl2g2c27a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
ql2g2c27a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g2c27a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl3g2c27a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g2c27a = marker('BPM', 'IdentityPass'); %s= inf
ql3g2c27a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c27a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqmhg4c27a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qm1g4c27a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c27a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c27a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c27a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c27b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c27b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c27b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c27b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c27b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c27b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ch2g6c27b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
sh4g6c27b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g6c27b = marker('BPM', 'IdentityPass'); %s= inf
qh3g6c27b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g6c27b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g6c27b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g6c27b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qh1g6c27b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g6c27b = marker('BPM', 'IdentityPass'); %s= inf
sh1g6c27b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
sh1g2c28a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g2c28a = marker('BPM', 'IdentityPass'); %s= inf
qh1g2c28a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g2c28a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqhhg2c28a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g2c28a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g2c28a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh3g2c28a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g2c28a = marker('BPM', 'IdentityPass'); %s= inf
sh4g2c28a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ch2g2c28a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
cm1g4c28a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qm1g4c28a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c28a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c28a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c28a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c28b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c28b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c28b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c28b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c28b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c28b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ql3g6c28b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g6c28b = marker('BPM', 'IdentityPass'); %s= inf
sl3g6c28b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g6c28b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql2g6c28b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
sl2g6c28b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g6c28b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
ql1g6c28b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g6c28b = marker('BPM', 'IdentityPass'); %s= inf
sl1g6c28b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
sl1g2c29a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= inf
pl1g2c29a = marker('BPM', 'IdentityPass'); %s= inf
ql1g2c29a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= inf
cl1g2c29a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl2g2c29a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= inf
ql2g2c29a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= inf
cl2g2c29a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
sl3g2c29a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= inf
pl2g2c29a = marker('BPM', 'IdentityPass'); %s= inf
ql3g2c29a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c29a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= inf
sqmhg4c29a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= inf
qm1g4c29a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c29a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c29a = marker('BPM', 'IdentityPass'); %s= inf
qm2g4c29a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm2g4c29b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= inf
qm2g4c29b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= inf
sm1g4c29b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= inf
pm1g4c29b = marker('BPM', 'IdentityPass'); %s= inf
qm1g4c29b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= inf
cm1g4c29b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
ch2g6c29b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= inf
sh4g6c29b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= inf
ph2g6c29b = marker('BPM', 'IdentityPass'); %s= inf
qh3g6c29b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= inf
sh3g6c29b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= inf
qh2g6c29b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= inf
ch1g6c29b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= inf
qh1g6c29b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= inf
ph1g6c29b = marker('BPM', 'IdentityPass'); %s= inf
sh1g6c29b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= inf
LV2SR= [ D_0_cav cav sh1g2c30a ph1g2c30a qh1g2c30a ch1g2c30a sqhhg2c30a qh2g2c30a sh3g2c30a qh3g2c30a ph2g2c30a sh4g2c30a ch2g2c30a cm1g4c30a qm1g4c30a sm1g4c30a pm1g4c30a qm2g4c30a sm2g4c30b qm2g4c30b sm1g4c30b pm1g4c30b qm1g4c30b cm1g4c30b ql3g6c30b pl2g6c30b sl3g6c30b cl2g6c30b ql2g6c30b sl2g6c30b cl1g6c30b ql1g6c30b pl1g6c30b sl1g6c30b sl1g2c01a pl1g2c01a ql1g2c01a cl1g2c01a sl2g2c01a ql2g2c01a cl2g2c01a sl3g2c01a pl2g2c01a ql3g2c01a cm1g4c01a sqmhg4c01a qm1g4c01a sm1g4c01a pm1g4c01a qm2g4c01a sm2g4c01b qm2g4c01b sm1g4c01b pm1g4c01b qm1g4c01b cm1g4c01b ch2g6c01b sh4g6c01b ph2g6c01b qh3g6c01b sh3g6c01b qh2g6c01b ch1g6c01b qh1g6c01b ph1g6c01b sh1g6c01b sh1g2c02a ph1g2c02a qh1g2c02a ch1g2c02a sqhhg2c02a qh2g2c02a sh3g2c02a qh3g2c02a ph2g2c02a sh4g2c02a ch2g2c02a cm1g4c02a qm1g4c02a sm1g4c02a pm1g4c02a qm2g4c02a sm2g4c02b qm2g4c02b sm1g4c02b pm1g4c02b qm1g4c02b cm1g4c02b ql3g6c02b pl2g6c02b sl3g6c02b cl2g6c02b ql2g6c02b sl2g6c02b cl1g6c02b ql1g6c02b pl1g6c02b sl1g6c02b sl1g2c03a pl1g2c03a ql1g2c03a cl1g2c03a sl2g2c03a ql2g2c03a cl2g2c03a sl3g2c03a pl2g2c03a ql3g2c03a cm1g4c03a sqmhg4c03a qm1g4c03a sm1g4c03a pm1g4c03a qm2g4c03a sm2g4c03b qm2g4c03b sm1g4c03b pm1g4c03b qm1g4c03b cm1g4c03b ch2g6c03b sh4g6c03b ph2g6c03b qh3g6c03b sh3g6c03b qh2g6c03b ch1g6c03b qh1g6c03b ph1g6c03b sh1g6c03b sh1g2c04a ph1g2c04a qh1g2c04a ch1g2c04a sqhhg2c04a qh2g2c04a sh3g2c04a qh3g2c04a ph2g2c04a sh4g2c04a ch2g2c04a cm1g4c04a qm1g4c04a sm1g4c04a pm1g4c04a qm2g4c04a sm2g4c04b qm2g4c04b sm1g4c04b pm1g4c04b qm1g4c04b cm1g4c04b ql3g6c04b pl2g6c04b sl3g6c04b cl2g6c04b ql2g6c04b sl2g6c04b cl1g6c04b ql1g6c04b pl1g6c04b sl1g6c04b sl1g2c05a pl1g2c05a ql1g2c05a cl1g2c05a sl2g2c05a ql2g2c05a cl2g2c05a sl3g2c05a pl2g2c05a ql3g2c05a cm1g4c05a sqmhg4c05a qm1g4c05a sm1g4c05a pm1g4c05a qm2g4c05a sm2g4c05b qm2g4c05b sm1g4c05b pm1g4c05b qm1g4c05b cm1g4c05b ch2g6c05b sh4g6c05b ph2g6c05b qh3g6c05b sh3g6c05b qh2g6c05b ch1g6c05b qh1g6c05b ph1g6c05b sh1g6c05b sh1g2c06a ph1g2c06a qh1g2c06a ch1g2c06a sqhhg2c06a qh2g2c06a sh3g2c06a qh3g2c06a ph2g2c06a sh4g2c06a ch2g2c06a cm1g4c06a qm1g4c06a sm1g4c06a pm1g4c06a qm2g4c06a sm2g4c06b qm2g4c06b sm1g4c06b pm1g4c06b qm1g4c06b cm1g4c06b ql3g6c06b pl2g6c06b sl3g6c06b cl2g6c06b ql2g6c06b sl2g6c06b cl1g6c06b ql1g6c06b pl1g6c06b sl1g6c06b sl1g2c07a pl1g2c07a ql1g2c07a cl1g2c07a sl2g2c07a ql2g2c07a cl2g2c07a sl3g2c07a pl2g2c07a ql3g2c07a cm1g4c07a sqmhg4c07a qm1g4c07a sm1g4c07a pm1g4c07a qm2g4c07a sm2g4c07b qm2g4c07b sm1g4c07b pm1g4c07b qm1g4c07b cm1g4c07b ch2g6c07b sh4g6c07b ph2g6c07b qh3g6c07b sh3g6c07b qh2g6c07b ch1g6c07b qh1g6c07b ph1g6c07b sh1g6c07b sh1g2c08a ph1g2c08a qh1g2c08a ch1g2c08a sqhhg2c08a qh2g2c08a sh3g2c08a qh3g2c08a ph2g2c08a sh4g2c08a ch2g2c08a cm1g4c08a qm1g4c08a sm1g4c08a pm1g4c08a qm2g4c08a sm2g4c08b qm2g4c08b sm1g4c08b pm1g4c08b qm1g4c08b cm1g4c08b ql3g6c08b pl2g6c08b sl3g6c08b cl2g6c08b ql2g6c08b sl2g6c08b cl1g6c08b ql1g6c08b pl1g6c08b sl1g6c08b sl1g2c09a pl1g2c09a ql1g2c09a cl1g2c09a sl2g2c09a ql2g2c09a cl2g2c09a sl3g2c09a pl2g2c09a ql3g2c09a cm1g4c09a sqmhg4c09a qm1g4c09a sm1g4c09a pm1g4c09a qm2g4c09a sm2g4c09b qm2g4c09b sm1g4c09b pm1g4c09b qm1g4c09b cm1g4c09b ch2g6c09b sh4g6c09b ph2g6c09b qh3g6c09b sh3g6c09b qh2g6c09b ch1g6c09b qh1g6c09b ph1g6c09b sh1g6c09b sh1g2c10a ph1g2c10a qh1g2c10a ch1g2c10a sqhhg2c10a qh2g2c10a sh3g2c10a qh3g2c10a ph2g2c10a sh4g2c10a ch2g2c10a cm1g4c10a qm1g4c10a sm1g4c10a pm1g4c10a qm2g4c10a sm2g4c10b qm2g4c10b sm1g4c10b pm1g4c10b qm1g4c10b cm1g4c10b ql3g6c10b pl2g6c10b sl3g6c10b cl2g6c10b ql2g6c10b sl2g6c10b cl1g6c10b ql1g6c10b pl1g6c10b sl1g6c10b sl1g2c11a pl1g2c11a ql1g2c11a cl1g2c11a sl2g2c11a ql2g2c11a cl2g2c11a sl3g2c11a pl2g2c11a ql3g2c11a cm1g4c11a sqmhg4c11a qm1g4c11a sm1g4c11a pm1g4c11a qm2g4c11a sm2g4c11b qm2g4c11b sm1g4c11b pm1g4c11b qm1g4c11b cm1g4c11b ch2g6c11b sh4g6c11b ph2g6c11b qh3g6c11b sh3g6c11b qh2g6c11b ch1g6c11b qh1g6c11b ph1g6c11b sh1g6c11b sh1g2c12a ph1g2c12a qh1g2c12a ch1g2c12a sqhhg2c12a qh2g2c12a sh3g2c12a qh3g2c12a ph2g2c12a sh4g2c12a ch2g2c12a cm1g4c12a qm1g4c12a sm1g4c12a pm1g4c12a qm2g4c12a sm2g4c12b qm2g4c12b sm1g4c12b pm1g4c12b qm1g4c12b cm1g4c12b ql3g6c12b pl2g6c12b sl3g6c12b cl2g6c12b ql2g6c12b sl2g6c12b cl1g6c12b ql1g6c12b pl1g6c12b sl1g6c12b sl1g2c13a pl1g2c13a ql1g2c13a cl1g2c13a sl2g2c13a ql2g2c13a cl2g2c13a sl3g2c13a pl2g2c13a ql3g2c13a cm1g4c13a sqmhg4c13a qm1g4c13a sm1g4c13a pm1g4c13a qm2g4c13a sm2g4c13b qm2g4c13b sm1g4c13b pm1g4c13b qm1g4c13b cm1g4c13b ch2g6c13b sh4g6c13b ph2g6c13b qh3g6c13b sh3g6c13b qh2g6c13b ch1g6c13b qh1g6c13b ph1g6c13b sh1g6c13b sh1g2c14a ph1g2c14a qh1g2c14a ch1g2c14a sqhhg2c14a qh2g2c14a sh3g2c14a qh3g2c14a ph2g2c14a sh4g2c14a ch2g2c14a cm1g4c14a qm1g4c14a sm1g4c14a pm1g4c14a qm2g4c14a sm2g4c14b qm2g4c14b sm1g4c14b pm1g4c14b qm1g4c14b cm1g4c14b ql3g6c14b pl2g6c14b sl3g6c14b cl2g6c14b ql2g6c14b sl2g6c14b cl1g6c14b ql1g6c14b pl1g6c14b sl1g6c14b sl1g2c15a pl1g2c15a ql1g2c15a cl1g2c15a sl2g2c15a ql2g2c15a cl2g2c15a sl3g2c15a pl2g2c15a ql3g2c15a cm1g4c15a sqmhg4c15a qm1g4c15a sm1g4c15a pm1g4c15a qm2g4c15a sm2g4c15b qm2g4c15b sm1g4c15b pm1g4c15b qm1g4c15b cm1g4c15b ch2g6c15b sh4g6c15b ph2g6c15b qh3g6c15b sh3g6c15b qh2g6c15b ch1g6c15b qh1g6c15b ph1g6c15b sh1g6c15b sh1g2c16a ph1g2c16a qh1g2c16a ch1g2c16a sqhhg2c16a qh2g2c16a sh3g2c16a qh3g2c16a ph2g2c16a sh4g2c16a ch2g2c16a cm1g4c16a qm1g4c16a sm1g4c16a pm1g4c16a qm2g4c16a sm2g4c16b qm2g4c16b sm1g4c16b pm1g4c16b qm1g4c16b cm1g4c16b ql3g6c16b pl2g6c16b sl3g6c16b cl2g6c16b ql2g6c16b sl2g6c16b cl1g6c16b ql1g6c16b pl1g6c16b sl1g6c16b sl1g2c17a pl1g2c17a ql1g2c17a cl1g2c17a sl2g2c17a ql2g2c17a cl2g2c17a sl3g2c17a pl2g2c17a ql3g2c17a cm1g4c17a sqmhg4c17a qm1g4c17a sm1g4c17a pm1g4c17a qm2g4c17a sm2g4c17b qm2g4c17b sm1g4c17b pm1g4c17b qm1g4c17b cm1g4c17b ch2g6c17b sh4g6c17b ph2g6c17b qh3g6c17b sh3g6c17b qh2g6c17b ch1g6c17b qh1g6c17b ph1g6c17b sh1g6c17b sh1g2c18a ph1g2c18a qh1g2c18a ch1g2c18a sqhhg2c18a qh2g2c18a sh3g2c18a qh3g2c18a ph2g2c18a sh4g2c18a ch2g2c18a cm1g4c18a qm1g4c18a sm1g4c18a pm1g4c18a qm2g4c18a sm2g4c18b qm2g4c18b sm1g4c18b pm1g4c18b qm1g4c18b cm1g4c18b ql3g6c18b pl2g6c18b sl3g6c18b cl2g6c18b ql2g6c18b sl2g6c18b cl1g6c18b ql1g6c18b pl1g6c18b sl1g6c18b sl1g2c19a pl1g2c19a ql1g2c19a cl1g2c19a sl2g2c19a ql2g2c19a cl2g2c19a sl3g2c19a pl2g2c19a ql3g2c19a cm1g4c19a sqmhg4c19a qm1g4c19a sm1g4c19a pm1g4c19a qm2g4c19a sm2g4c19b qm2g4c19b sm1g4c19b pm1g4c19b qm1g4c19b cm1g4c19b ch2g6c19b sh4g6c19b ph2g6c19b qh3g6c19b sh3g6c19b qh2g6c19b ch1g6c19b qh1g6c19b ph1g6c19b sh1g6c19b sh1g2c20a ph1g2c20a qh1g2c20a ch1g2c20a sqhhg2c20a qh2g2c20a sh3g2c20a qh3g2c20a ph2g2c20a sh4g2c20a ch2g2c20a cm1g4c20a qm1g4c20a sm1g4c20a pm1g4c20a qm2g4c20a sm2g4c20b qm2g4c20b sm1g4c20b pm1g4c20b qm1g4c20b cm1g4c20b ql3g6c20b pl2g6c20b sl3g6c20b cl2g6c20b ql2g6c20b sl2g6c20b cl1g6c20b ql1g6c20b pl1g6c20b sl1g6c20b sl1g2c21a pl1g2c21a ql1g2c21a cl1g2c21a sl2g2c21a ql2g2c21a cl2g2c21a sl3g2c21a pl2g2c21a ql3g2c21a cm1g4c21a sqmhg4c21a qm1g4c21a sm1g4c21a pm1g4c21a qm2g4c21a sm2g4c21b qm2g4c21b sm1g4c21b pm1g4c21b qm1g4c21b cm1g4c21b ch2g6c21b sh4g6c21b ph2g6c21b qh3g6c21b sh3g6c21b qh2g6c21b ch1g6c21b qh1g6c21b ph1g6c21b sh1g6c21b sh1g2c22a ph1g2c22a qh1g2c22a ch1g2c22a sqhhg2c22a qh2g2c22a sh3g2c22a qh3g2c22a ph2g2c22a sh4g2c22a ch2g2c22a cm1g4c22a qm1g4c22a sm1g4c22a pm1g4c22a qm2g4c22a sm2g4c22b qm2g4c22b sm1g4c22b pm1g4c22b qm1g4c22b cm1g4c22b ql3g6c22b pl2g6c22b sl3g6c22b cl2g6c22b ql2g6c22b sl2g6c22b cl1g6c22b ql1g6c22b pl1g6c22b sl1g6c22b sl1g2c23a pl1g2c23a ql1g2c23a cl1g2c23a sl2g2c23a ql2g2c23a cl2g2c23a sl3g2c23a pl2g2c23a ql3g2c23a cm1g4c23a sqmhg4c23a qm1g4c23a sm1g4c23a pm1g4c23a qm2g4c23a sm2g4c23b qm2g4c23b sm1g4c23b pm1g4c23b qm1g4c23b cm1g4c23b ch2g6c23b sh4g6c23b ph2g6c23b qh3g6c23b sh3g6c23b qh2g6c23b ch1g6c23b qh1g6c23b ph1g6c23b sh1g6c23b sh1g2c24a ph1g2c24a qh1g2c24a ch1g2c24a sqhhg2c24a qh2g2c24a sh3g2c24a qh3g2c24a ph2g2c24a sh4g2c24a ch2g2c24a cm1g4c24a qm1g4c24a sm1g4c24a pm1g4c24a qm2g4c24a sm2g4c24b qm2g4c24b sm1g4c24b pm1g4c24b qm1g4c24b cm1g4c24b ql3g6c24b pl2g6c24b sl3g6c24b cl2g6c24b ql2g6c24b sl2g6c24b cl1g6c24b ql1g6c24b pl1g6c24b sl1g6c24b sl1g2c25a pl1g2c25a ql1g2c25a cl1g2c25a sl2g2c25a ql2g2c25a cl2g2c25a sl3g2c25a pl2g2c25a ql3g2c25a cm1g4c25a sqmhg4c25a qm1g4c25a sm1g4c25a pm1g4c25a qm2g4c25a sm2g4c25b qm2g4c25b sm1g4c25b pm1g4c25b qm1g4c25b cm1g4c25b ch2g6c25b sh4g6c25b ph2g6c25b qh3g6c25b sh3g6c25b qh2g6c25b ch1g6c25b qh1g6c25b ph1g6c25b sh1g6c25b sh1g2c26a ph1g2c26a qh1g2c26a ch1g2c26a sqhhg2c26a qh2g2c26a sh3g2c26a qh3g2c26a ph2g2c26a sh4g2c26a ch2g2c26a cm1g4c26a qm1g4c26a sm1g4c26a pm1g4c26a qm2g4c26a sm2g4c26b qm2g4c26b sm1g4c26b pm1g4c26b qm1g4c26b cm1g4c26b ql3g6c26b pl2g6c26b sl3g6c26b cl2g6c26b ql2g6c26b sl2g6c26b cl1g6c26b ql1g6c26b pl1g6c26b sl1g6c26b sl1g2c27a pl1g2c27a ql1g2c27a cl1g2c27a sl2g2c27a ql2g2c27a cl2g2c27a sl3g2c27a pl2g2c27a ql3g2c27a cm1g4c27a sqmhg4c27a qm1g4c27a sm1g4c27a pm1g4c27a qm2g4c27a sm2g4c27b qm2g4c27b sm1g4c27b pm1g4c27b qm1g4c27b cm1g4c27b ch2g6c27b sh4g6c27b ph2g6c27b qh3g6c27b sh3g6c27b qh2g6c27b ch1g6c27b qh1g6c27b ph1g6c27b sh1g6c27b sh1g2c28a ph1g2c28a qh1g2c28a ch1g2c28a sqhhg2c28a qh2g2c28a sh3g2c28a qh3g2c28a ph2g2c28a sh4g2c28a ch2g2c28a cm1g4c28a qm1g4c28a sm1g4c28a pm1g4c28a qm2g4c28a sm2g4c28b qm2g4c28b sm1g4c28b pm1g4c28b qm1g4c28b cm1g4c28b ql3g6c28b pl2g6c28b sl3g6c28b cl2g6c28b ql2g6c28b sl2g6c28b cl1g6c28b ql1g6c28b pl1g6c28b sl1g6c28b sl1g2c29a pl1g2c29a ql1g2c29a cl1g2c29a sl2g2c29a ql2g2c29a cl2g2c29a sl3g2c29a pl2g2c29a ql3g2c29a cm1g4c29a sqmhg4c29a qm1g4c29a sm1g4c29a pm1g4c29a qm2g4c29a sm2g4c29b qm2g4c29b sm1g4c29b pm1g4c29b qm1g4c29b cm1g4c29b ch2g6c29b sh4g6c29b ph2g6c29b qh3g6c29b sh3g6c29b qh2g6c29b ch1g6c29b qh1g6c29b ph1g6c29b sh1g6c29b ];


% END of BODY

buildlat(LV2SR);
THERING = setcellstruct(THERING, 'Energy', 1:length(THERING), Energy);

%for i=1:length(THERING),
%    s = findspos(THERING, i+1);
%  fprintf('%s L=%f, s=%f\n', THERING{i}.FamName, THERING{i}.Length, s);
%end

L0 = findspos(THERING, length(THERING)+1);
fprintf('   Total Length = %.6f meters  \n', L0)

