function varargout = v2srlattice(varargin)

global THERING 

if nargin >=1
   Energy = varargin{1};
else
  Energy = 200e6;
end

% BEG_ = marker('BEG', 'IdentityPass');

D_0_fh2g1c30a = drift('DRIFT', 4.29379, 'DriftPass'); % +4.29379= sb(4.29379)
fh2g1c30a = drift('FCOR', 0.044, 'DriftPass'); %s= 4.29379 + 0.044
D_1_sh1g2c30a = drift('DRIFT', 0.31221, 'DriftPass'); % +0.31221= sb(4.65)
sh1g2c30a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 4.65 + 0.2
D_2_ph1g2c30a = drift('DRIFT', 0.085, 'DriftPass'); % +0.085= sb(4.935)
ph1g2c30a = drift('BPM', 0.0, 'DriftPass'); %s= 4.935 + 0.0
D_3_qh1g2c30a = drift('DRIFT', 0.0775, 'DriftPass'); % +0.0775= sb(5.0125)
qh1g2c30a = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 5.0125 + 0.275
D_4_ch1g2c30a = drift('DRIFT', 0.245, 'DriftPass'); % +0.245= sb(5.5325)
ch1g2c30a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 5.5325 + 0.0
D_5_sqhhg2c30a = drift('DRIFT', 8.881784197e-16, 'DriftPass'); % +8.881784197e-16= sb(5.5325)
sqhhg2c30a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 5.5325 + 0.1
D_6_qh2g2c30a = drift('DRIFT', 0.4595, 'DriftPass'); % +0.4595= sb(6.092)
qh2g2c30a = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 6.092 + 0.448
D_7_sh3g2c30a = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(6.73)
sh3g2c30a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 6.73 + 0.2
D_8_qh3g2c30a = drift('DRIFT', 0.1825, 'DriftPass'); % +0.1825= sb(7.1125)
qh3g2c30a = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 7.1125 + 0.275
D_9_ph2g2c30a = drift('DRIFT', 0.07252, 'DriftPass'); % +0.07252= sb(7.46002)
ph2g2c30a = drift('BPM', 0.0, 'DriftPass'); %s= 7.46002 + 0.0
D_10_sh4g2c30a = drift('DRIFT', 0.08998, 'DriftPass'); % +0.08998= sb(7.55)
sh4g2c30a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 7.55 + 0.2
D_11_ch2g2c30a = drift('DRIFT', 0.2485, 'DriftPass'); % +0.2485= sb(7.9985)
ch2g2c30a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 7.9985 + 0.3
D_12_b1g3c30a = drift('DRIFT', 0.0315, 'DriftPass'); % +0.0315= sb(8.33)
b1g3c30a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 8.33 + 2.62
D_13_cm1g4c30a = drift('DRIFT', 0.501, 'DriftPass'); % +0.501= sb(11.451)
cm1g4c30a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 11.451 + 0.2
D_14_qm1g4c30a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(11.925)
qm1g4c30a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 11.925 + 0.25
D_15_sm1g4c30a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(12.375)
sm1g4c30a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 12.375 + 0.2
D_16_fm1g4c30a = drift('DRIFT', 0.2332, 'DriftPass'); % +0.2332= sb(12.8082)
fm1g4c30a = drift('FCOR', 0.044, 'DriftPass'); %s= 12.8082 + 0.044
D_17_pm1g4c30a = drift('DRIFT', 0.2924, 'DriftPass'); % +0.2924= sb(13.1446)
pm1g4c30a = drift('BPM', 0.0, 'DriftPass'); %s= 13.1446 + 0.0
D_18_qm2g4c30a = drift('DRIFT', 0.0839, 'DriftPass'); % +0.0839= sb(13.2285)
qm2g4c30a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 13.2285 + 0.283
D_19_sm2g4c30b = drift('DRIFT', 0.1835, 'DriftPass'); % +0.1835= sb(13.695)
sm2g4c30b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 13.695 + 0.25
D_20_qm2g4c30b = drift('DRIFT', 0.1835, 'DriftPass'); % +0.1835= sb(14.1285)
qm2g4c30b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 14.1285 + 0.283
D_21_sm1g4c30b = drift('DRIFT', 0.5035, 'DriftPass'); % +0.5035= sb(14.915)
sm1g4c30b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 14.915 + 0.2
D_22_pm1g4c30b = drift('DRIFT', 0.2623, 'DriftPass'); % +0.2623= sb(15.3773)
pm1g4c30b = drift('BPM', 0.0, 'DriftPass'); %s= 15.3773 + 0.0
D_23_qm1g4c30b = drift('DRIFT', 0.0877, 'DriftPass'); % +0.0877= sb(15.465)
qm1g4c30b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 15.465 + 0.25
D_24_cm1g4c30b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(15.824)
cm1g4c30b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 15.824 + 0.3
D_25_b1g5c30b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(16.69)
b1g5c30b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 16.69 + 2.62
D_26_ql3g6c30b = drift('DRIFT', 0.5875, 'DriftPass'); % +0.5875= sb(19.8975)
ql3g6c30b = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 19.8975 + 0.275
D_27_pl2g6c30b = drift('DRIFT', 0.0747, 'DriftPass'); % +0.0747= sb(20.2472)
pl2g6c30b = drift('BPM', 0.0, 'DriftPass'); %s= 20.2472 + 0.0
D_28_sl3g6c30b = drift('DRIFT', 0.0878, 'DriftPass'); % +0.0878= sb(20.335)
sl3g6c30b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 20.335 + 0.2
D_29_cl2g6c30b = drift('DRIFT', 0.1575, 'DriftPass'); % +0.1575= sb(20.6925)
cl2g6c30b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 20.6925 + 0.2
D_30_ql2g6c30b = drift('DRIFT', 0.2081, 'DriftPass'); % +0.2081= sb(21.1006)
ql2g6c30b = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 21.1006 + 0.448
D_31_sl2g6c30b = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(21.7986)
sl2g6c30b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 21.7986 + 0.2
D_32_cl1g6c30b = drift('DRIFT', 0.1313, 'DriftPass'); % +0.1313= sb(22.1299)
cl1g6c30b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 22.1299 + 0.2
D_33_ql1g6c30b = drift('DRIFT', 0.1312, 'DriftPass'); % +0.1312= sb(22.4611)
ql1g6c30b = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 22.4611 + 0.275
D_34_pl1g6c30b = drift('DRIFT', 0.0748, 'DriftPass'); % +0.0748= sb(22.8109)
pl1g6c30b = drift('BPM', 0.0, 'DriftPass'); %s= 22.8109 + 0.0
D_35_sl1g6c30b = drift('DRIFT', 0.0877, 'DriftPass'); % +0.0877= sb(22.8986)
sl1g6c30b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 22.8986 + 0.2
D_36_fl1g1c01a = drift('DRIFT', 0.4465, 'DriftPass'); % +0.4465= sb(23.5451)
fl1g1c01a = drift('FCOR', 0.044, 'DriftPass'); %s= 23.5451 + 0.044
D_37_fl2g1c01a = drift('DRIFT', 5.7532, 'DriftPass'); % +5.7532= sb(29.3423)
fl2g1c01a = drift('FCOR', 0.044, 'DriftPass'); %s= 29.3423 + 0.044
D_38_sl1g2c01a = drift('DRIFT', 0.3123, 'DriftPass'); % +0.3123= sb(29.6986)
sl1g2c01a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 29.6986 + 0.2
D_39_pl1g2c01a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(29.9886)
pl1g2c01a = drift('BPM', 0.0, 'DriftPass'); %s= 29.9886 + 0.0
D_40_ql1g2c01a = drift('DRIFT', 0.0725, 'DriftPass'); % +0.0725= sb(30.0611)
ql1g2c01a = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 30.0611 + 0.275
D_41_cl1g2c01a = drift('DRIFT', 0.1312, 'DriftPass'); % +0.1312= sb(30.4673)
cl1g2c01a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 30.4673 + 0.2
D_42_sl2g2c01a = drift('DRIFT', 0.1313, 'DriftPass'); % +0.1313= sb(30.7986)
sl2g2c01a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 30.7986 + 0.2
D_43_ql2g2c01a = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(31.2486)
ql2g2c01a = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 31.2486 + 0.448
D_44_cl2g2c01a = drift('DRIFT', 0.2081, 'DriftPass'); % +0.2081= sb(31.9047)
cl2g2c01a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 31.9047 + 0.2
D_45_sl3g2c01a = drift('DRIFT', 0.1575, 'DriftPass'); % +0.1575= sb(32.2622)
sl3g2c01a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 32.2622 + 0.2
D_46_pl2g2c01a = drift('DRIFT', 0.0901, 'DriftPass'); % +0.0901= sb(32.5523)
pl2g2c01a = drift('BPM', 0.0, 'DriftPass'); %s= 32.5523 + 0.0
D_47_ql3g2c01a = drift('DRIFT', 0.0724, 'DriftPass'); % +0.0724= sb(32.6247)
ql3g2c01a = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 32.6247 + 0.275
D_48_b1g3c01a = drift('DRIFT', 0.5875, 'DriftPass'); % +0.5875= sb(33.4872)
b1g3c01a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 33.4872 + 2.62
D_49_cm1g4c01a = drift('DRIFT', 0.601, 'DriftPass'); % +0.601= sb(36.7082)
cm1g4c01a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 36.7082 + 0.0
sqmhg4c01a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 36.7082 + 0.1
D_51_qm1g4c01a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(37.0822)
qm1g4c01a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 37.0822 + 0.25
D_52_sm1g4c01a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(37.5322)
sm1g4c01a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 37.5322 + 0.2
D_53_fm1g4c01a = drift('DRIFT', 0.2332, 'DriftPass'); % +0.2332= sb(37.9654)
fm1g4c01a = drift('FCOR', 0.044, 'DriftPass'); %s= 37.9654 + 0.044
D_54_pm1g4c01a = drift('DRIFT', 0.2924, 'DriftPass'); % +0.2924= sb(38.3018)
pm1g4c01a = drift('BPM', 0.0, 'DriftPass'); %s= 38.3018 + 0.0
D_55_qm2g4c01a = drift('DRIFT', 0.0839, 'DriftPass'); % +0.0839= sb(38.3857)
qm2g4c01a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 38.3857 + 0.283
D_56_sm2g4c01b = drift('DRIFT', 0.1835, 'DriftPass'); % +0.1835= sb(38.8522)
sm2g4c01b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 38.8522 + 0.25
D_57_qm2g4c01b = drift('DRIFT', 0.1835, 'DriftPass'); % +0.1835= sb(39.2857)
qm2g4c01b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 39.2857 + 0.283
D_58_sm1g4c01b = drift('DRIFT', 0.5035, 'DriftPass'); % +0.5035= sb(40.0722)
sm1g4c01b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 40.0722 + 0.2
D_59_pm1g4c01b = drift('DRIFT', 0.2623, 'DriftPass'); % +0.2623= sb(40.5345)
pm1g4c01b = drift('BPM', 0.0, 'DriftPass'); %s= 40.5345 + 0.0
D_60_qm1g4c01b = drift('DRIFT', 0.0877, 'DriftPass'); % +0.0877= sb(40.6222)
qm1g4c01b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 40.6222 + 0.25
D_61_cm1g4c01b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(40.9812)
cm1g4c01b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 40.9812 + 0.3
D_62_b1g5c01b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(41.8472)
b1g5c01b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 41.8472 + 2.62
D_63_ch2g6c01b = drift('DRIFT', 0.2163, 'DriftPass'); % +0.2163= sb(44.6835)
ch2g6c01b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 44.6835 + 0.3
D_64_sh4g6c01b = drift('DRIFT', 0.0637, 'DriftPass'); % +0.0637= sb(45.0472)
sh4g6c01b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 45.0472 + 0.2
D_65_ph2g6c01b = drift('DRIFT', 0.0896, 'DriftPass'); % +0.0896= sb(45.3368)
ph2g6c01b = drift('BPM', 0.0, 'DriftPass'); %s= 45.3368 + 0.0
D_66_qh3g6c01b = drift('DRIFT', 0.0729, 'DriftPass'); % +0.0729= sb(45.4097)
qh3g6c01b = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 45.4097 + 0.275
D_67_sh3g6c01b = drift('DRIFT', 0.1825, 'DriftPass'); % +0.1825= sb(45.8672)
sh3g6c01b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 45.8672 + 0.2
D_68_qh2g6c01b = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(46.2572)
qh2g6c01b = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 46.2572 + 0.448
D_69_ch1g6c01b = drift('DRIFT', 0.4845, 'DriftPass'); % +0.4845= sb(47.1897)
ch1g6c01b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 47.1897 + 0.2
D_70_qh1g6c01b = drift('DRIFT', 0.12, 'DriftPass'); % +0.12= sb(47.5097)
qh1g6c01b = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 47.5097 + 0.275
D_71_ph1g6c01b = drift('DRIFT', 0.0771, 'DriftPass'); % +0.0771= sb(47.8618)
ph1g6c01b = drift('BPM', 0.0, 'DriftPass'); %s= 47.8618 + 0.0
D_72_sh1g6c01b = drift('DRIFT', 0.0854, 'DriftPass'); % +0.0854= sb(47.9472)
sh1g6c01b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 47.9472 + 0.2
D_73_fh1g1c02a = drift('DRIFT', 0.4409, 'DriftPass'); % +0.4409= sb(48.5881)
fh1g1c02a = drift('FCOR', 0.044, 'DriftPass'); %s= 48.5881 + 0.044
D_74_fh2g1c02a = drift('DRIFT', 8.4589, 'DriftPass'); % +8.4589= sb(57.091)
fh2g1c02a = drift('FCOR', 0.044, 'DriftPass'); %s= 57.091 + 0.044
D_75_sh1g2c02a = drift('DRIFT', 0.3122, 'DriftPass'); % +0.3122= sb(57.4472)
sh1g2c02a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 57.4472 + 0.2
D_76_ph1g2c02a = drift('DRIFT', 0.085, 'DriftPass'); % +0.085= sb(57.7322)
ph1g2c02a = drift('BPM', 0.0, 'DriftPass'); %s= 57.7322 + 0.0
D_77_qh1g2c02a = drift('DRIFT', 0.0775, 'DriftPass'); % +0.0775= sb(57.8097)
qh1g2c02a = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 57.8097 + 0.275
D_78_ch1g2c02a = drift('DRIFT', 0.245, 'DriftPass'); % +0.245= sb(58.3297)
ch1g2c02a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 58.3297 + 0.0
sqhhg2c02a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 58.3297 + 0.1
D_80_qh2g2c02a = drift('DRIFT', 0.4595, 'DriftPass'); % +0.4595= sb(58.8892)
qh2g2c02a = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 58.8892 + 0.448
D_81_sh3g2c02a = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(59.5272)
sh3g2c02a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 59.5272 + 0.2
D_82_qh3g2c02a = drift('DRIFT', 0.1825, 'DriftPass'); % +0.1825= sb(59.9097)
qh3g2c02a = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 59.9097 + 0.275
D_83_ph2g2c02a = drift('DRIFT', 0.0725, 'DriftPass'); % +0.0725= sb(60.2572)
ph2g2c02a = drift('BPM', 0.0, 'DriftPass'); %s= 60.2572 + 0.0
D_84_sh4g2c02a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(60.3472)
sh4g2c02a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 60.3472 + 0.2
D_85_ch2g2c02a = drift('DRIFT', 0.2485, 'DriftPass'); % +0.2485= sb(60.7957)
ch2g2c02a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 60.7957 + 0.3
D_86_b1g3c02a = drift('DRIFT', 0.0315, 'DriftPass'); % +0.0315= sb(61.1272)
b1g3c02a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 61.1272 + 2.62
D_87_cm1g4c02a = drift('DRIFT', 0.501, 'DriftPass'); % +0.501= sb(64.2482)
cm1g4c02a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 64.2482 + 0.2
D_88_qm1g4c02a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(64.7222)
qm1g4c02a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 64.7222 + 0.25
D_89_sm1g4c02a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(65.1722)
sm1g4c02a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 65.1722 + 0.2
D_90_fm1g4c02a = drift('DRIFT', 0.2332, 'DriftPass'); % +0.2332= sb(65.6054)
fm1g4c02a = drift('FCOR', 0.044, 'DriftPass'); %s= 65.6054 + 0.044
D_91_pm1g4c02a = drift('DRIFT', 0.2924, 'DriftPass'); % +0.2924= sb(65.9418)
pm1g4c02a = drift('BPM', 0.0, 'DriftPass'); %s= 65.9418 + 0.0
D_92_qm2g4c02a = drift('DRIFT', 0.0839, 'DriftPass'); % +0.0839= sb(66.0257)
qm2g4c02a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 66.0257 + 0.283
D_93_sm2g4c02b = drift('DRIFT', 0.1835, 'DriftPass'); % +0.1835= sb(66.4922)
sm2g4c02b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 66.4922 + 0.25
D_94_qm2g4c02b = drift('DRIFT', 0.1835, 'DriftPass'); % +0.1835= sb(66.9257)
qm2g4c02b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 66.9257 + 0.283
D_95_sm1g4c02b = drift('DRIFT', 0.5035, 'DriftPass'); % +0.5035= sb(67.7122)
sm1g4c02b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 67.7122 + 0.2
D_96_pm1g4c02b = drift('DRIFT', 0.2623, 'DriftPass'); % +0.2623= sb(68.1745)
pm1g4c02b = drift('BPM', 0.0, 'DriftPass'); %s= 68.1745 + 0.0
D_97_qm1g4c02b = drift('DRIFT', 0.0877, 'DriftPass'); % +0.0877= sb(68.2622)
qm1g4c02b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 68.2622 + 0.25
D_98_cm1g4c02b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(68.6212)
cm1g4c02b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 68.6212 + 0.3
D_99_b1g5c02b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(69.4872)
b1g5c02b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 69.4872 + 2.62
D_100_ql3g6c02b = drift('DRIFT', 0.5875, 'DriftPass'); % +0.5875= sb(72.6947)
ql3g6c02b = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 72.6947 + 0.275
D_101_pl2g6c02b = drift('DRIFT', 0.0747, 'DriftPass'); % +0.0747= sb(73.0444)
pl2g6c02b = drift('BPM', 0.0, 'DriftPass'); %s= 73.0444 + 0.0
D_102_sl3g6c02b = drift('DRIFT', 0.0878, 'DriftPass'); % +0.0878= sb(73.1322)
sl3g6c02b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 73.1322 + 0.2
D_103_cl2g6c02b = drift('DRIFT', 0.1575, 'DriftPass'); % +0.1575= sb(73.4897)
cl2g6c02b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 73.4897 + 0.2
D_104_ql2g6c02b = drift('DRIFT', 0.2081, 'DriftPass'); % +0.2081= sb(73.8978)
ql2g6c02b = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 73.8978 + 0.448
D_105_sl2g6c02b = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(74.5958)
sl2g6c02b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 74.5958 + 0.2
D_106_cl1g6c02b = drift('DRIFT', 0.1312, 'DriftPass'); % +0.1312= sb(74.927)
cl1g6c02b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 74.927 + 0.2
D_107_ql1g6c02b = drift('DRIFT', 0.1313, 'DriftPass'); % +0.1313= sb(75.2583)
ql1g6c02b = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 75.2583 + 0.275
D_108_pl1g6c02b = drift('DRIFT', 0.0748, 'DriftPass'); % +0.0748= sb(75.6081)
pl1g6c02b = drift('BPM', 0.0, 'DriftPass'); %s= 75.6081 + 0.0
D_109_sl1g6c02b = drift('DRIFT', 0.0877, 'DriftPass'); % +0.0877= sb(75.6958)
sl1g6c02b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 75.6958 + 0.2
D_110_fl1g1c03a = drift('DRIFT', 0.4465, 'DriftPass'); % +0.4465= sb(76.3423)
fl1g1c03a = drift('FCOR', 0.044, 'DriftPass'); %s= 76.3423 + 0.044
D_111_pu1g1c03a = drift('DRIFT', 0.2667, 'DriftPass'); % +0.2667= sb(76.653)
pu1g1c03a = drift('UBPM', 0.0, 'DriftPass'); %s= 76.653 + 0.0
D_112_cu1g1c03id1 = drift('DRIFT', 1.0428, 'DriftPass'); % +1.0428= sb(77.6958)
cu1g1c03id1 = drift('IDCOR', 0.0, 'DriftPass'); %s= 77.6958 + 0.0
cs1g1c03id1 = drift('IDSIMCOR', 0.0, 'DriftPass'); %s= 77.6958 + 0.0
ivu20g1c03c = drift('INSERTION', 3.0, 'DriftPass'); %s= 77.6958 + 3.0
cu2g1c03id2 = drift('IDCOR', 0.0, 'DriftPass'); %s= 80.6958 + 0.0
cs2g1c03id2 = drift('IDSIMCOR', 0.0, 'DriftPass'); %s= 80.6958 + 0.0
D_117_pu4g1c03a = drift('DRIFT', 1.1786, 'DriftPass'); % +1.1786= sb(81.8744)
pu4g1c03a = drift('UBPM', 0.0, 'DriftPass'); %s= 81.8744 + 0.0
D_118_fl2g1c03a = drift('DRIFT', 0.2651, 'DriftPass'); % +0.2651= sb(82.1395)
fl2g1c03a = drift('FCOR', 0.044, 'DriftPass'); %s= 82.1395 + 0.044
D_119_sl1g2c03a = drift('DRIFT', 0.3123, 'DriftPass'); % +0.3123= sb(82.4958)
sl1g2c03a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 82.4958 + 0.2
D_120_pl1g2c03a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(82.7858)
pl1g2c03a = drift('BPM', 0.0, 'DriftPass'); %s= 82.7858 + 0.0
D_121_ql1g2c03a = drift('DRIFT', 0.0725, 'DriftPass'); % +0.0725= sb(82.8583)
ql1g2c03a = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 82.8583 + 0.275
D_122_cl1g2c03a = drift('DRIFT', 0.1312, 'DriftPass'); % +0.1312= sb(83.2645)
cl1g2c03a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 83.2645 + 0.2
D_123_sl2g2c03a = drift('DRIFT', 0.1313, 'DriftPass'); % +0.1313= sb(83.5958)
sl2g2c03a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 83.5958 + 0.2
D_124_ql2g2c03a = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(84.0458)
ql2g2c03a = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 84.0458 + 0.448
D_125_cl2g2c03a = drift('DRIFT', 0.2081, 'DriftPass'); % +0.2081= sb(84.7019)
cl2g2c03a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 84.7019 + 0.2
D_126_sl3g2c03a = drift('DRIFT', 0.1575, 'DriftPass'); % +0.1575= sb(85.0594)
sl3g2c03a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 85.0594 + 0.2
D_127_pl2g2c03a = drift('DRIFT', 0.0901, 'DriftPass'); % +0.0901= sb(85.3495)
pl2g2c03a = drift('BPM', 0.0, 'DriftPass'); %s= 85.3495 + 0.0
D_128_ql3g2c03a = drift('DRIFT', 0.0724, 'DriftPass'); % +0.0724= sb(85.4219)
ql3g2c03a = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 85.4219 + 0.275
D_129_b2g3c03a = drift('DRIFT', 0.5875, 'DriftPass'); % +0.5875= sb(86.2844)
b2g3c03a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 86.2844 + 2.62
D_130_cm1g4c03a = drift('DRIFT', 0.601, 'DriftPass'); % +0.601= sb(89.5054)
cm1g4c03a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 89.5054 + 0.0
D_131_sqmhg4c03a = drift('DRIFT', 1.42108547152e-14, 'DriftPass'); % +1.42108547152e-14= sb(89.5054)
sqmhg4c03a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 89.5054 + 0.1
D_132_qm1g4c03a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(89.8794)
qm1g4c03a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 89.8794 + 0.25
D_133_sm1g4c03a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(90.3294)
sm1g4c03a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 90.3294 + 0.2
D_134_fm1g4c03a = drift('DRIFT', 0.2332, 'DriftPass'); % +0.2332= sb(90.7626)
fm1g4c03a = drift('FCOR', 0.044, 'DriftPass'); %s= 90.7626 + 0.044
D_135_pm1g4c03a = drift('DRIFT', 0.2924, 'DriftPass'); % +0.2924= sb(91.099)
pm1g4c03a = drift('BPM', 0.0, 'DriftPass'); %s= 91.099 + 0.0
D_136_qm2g4c03a = drift('DRIFT', 0.0839, 'DriftPass'); % +0.0839= sb(91.1829)
qm2g4c03a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 91.1829 + 0.283
D_137_sm2g4c03b = drift('DRIFT', 0.1835, 'DriftPass'); % +0.1835= sb(91.6494)
sm2g4c03b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 91.6494 + 0.25
D_138_qm2g4c03b = drift('DRIFT', 0.1835, 'DriftPass'); % +0.1835= sb(92.0829)
qm2g4c03b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 92.0829 + 0.283
D_139_sm1g4c03b = drift('DRIFT', 0.5035, 'DriftPass'); % +0.5035= sb(92.8694)
sm1g4c03b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 92.8694 + 0.2
D_140_pm1g4c03b = drift('DRIFT', 0.2623, 'DriftPass'); % +0.2623= sb(93.3317)
pm1g4c03b = drift('BPM', 0.0, 'DriftPass'); %s= 93.3317 + 0.0
D_141_qm1g4c03b = drift('DRIFT', 0.0877, 'DriftPass'); % +0.0877= sb(93.4194)
qm1g4c03b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 93.4194 + 0.25
D_142_cm1g4c03b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(93.7784)
cm1g4c03b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 93.7784 + 0.3
D_143_b2g5c03b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(94.6444)
b2g5c03b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 94.6444 + 2.62
D_144_ch2g6c03b = drift('DRIFT', 0.2163, 'DriftPass'); % +0.2163= sb(97.4807)
ch2g6c03b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 97.4807 + 0.3
D_145_sh4g6c03b = drift('DRIFT', 0.0637, 'DriftPass'); % +0.0637= sb(97.8444)
sh4g6c03b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 97.8444 + 0.2
D_146_ph2g6c03b = drift('DRIFT', 0.0896, 'DriftPass'); % +0.0896= sb(98.134)
ph2g6c03b = drift('BPM', 0.0, 'DriftPass'); %s= 98.134 + 0.0
D_147_qh3g6c03b = drift('DRIFT', 0.0729, 'DriftPass'); % +0.0729= sb(98.2069)
qh3g6c03b = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 98.2069 + 0.275
D_148_sh3g6c03b = drift('DRIFT', 0.1825, 'DriftPass'); % +0.1825= sb(98.6644)
sh3g6c03b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 98.6644 + 0.2
D_149_qh2g6c03b = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(99.0544)
qh2g6c03b = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 99.0544 + 0.448
D_150_ch1g6c03b = drift('DRIFT', 0.4846, 'DriftPass'); % +0.4846= sb(99.987)
ch1g6c03b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 99.987 + 0.2
D_151_qh1g6c03b = drift('DRIFT', 0.12, 'DriftPass'); % +0.12= sb(100.307)
qh1g6c03b = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 100.307 + 0.275
D_152_ph1g6c03b = drift('DRIFT', 0.077, 'DriftPass'); % +0.077= sb(100.659)
ph1g6c03b = drift('BPM', 0.0, 'DriftPass'); %s= 100.659 + 0.0
D_153_sh1g6c03b = drift('DRIFT', 0.085, 'DriftPass'); % +0.085= sb(100.744)
sh1g6c03b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 100.744 + 0.2
D_154_fh1g1c04a = drift('DRIFT', 0.441, 'DriftPass'); % +0.441= sb(101.385)
fh1g1c04a = drift('FCOR', 0.044, 'DriftPass'); %s= 101.385 + 0.044
D_155_fh2g1c04a = drift('DRIFT', 8.459, 'DriftPass'); % +8.459= sb(109.888)
fh2g1c04a = drift('FCOR', 0.044, 'DriftPass'); %s= 109.888 + 0.044
D_156_sh1g2c04a = drift('DRIFT', 0.312, 'DriftPass'); % +0.312= sb(110.244)
sh1g2c04a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 110.244 + 0.2
D_157_ph1g2c04a = drift('DRIFT', 0.085, 'DriftPass'); % +0.085= sb(110.529)
ph1g2c04a = drift('BPM', 0.0, 'DriftPass'); %s= 110.529 + 0.0
D_158_qh1g2c04a = drift('DRIFT', 0.078, 'DriftPass'); % +0.078= sb(110.607)
qh1g2c04a = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 110.607 + 0.275
D_159_ch1g2c04a = drift('DRIFT', 0.245, 'DriftPass'); % +0.245= sb(111.127)
ch1g2c04a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 111.127 + 0.0
D_160_sqhhg2c04a = drift('DRIFT', 1.42108547152e-14, 'DriftPass'); % +1.42108547152e-14= sb(111.127)
sqhhg2c04a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 111.127 + 0.1
D_161_qh2g2c04a = drift('DRIFT', 0.459, 'DriftPass'); % +0.459= sb(111.686)
qh2g2c04a = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 111.686 + 0.448
D_162_sh3g2c04a = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(112.324)
sh3g2c04a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 112.324 + 0.2
D_163_qh3g2c04a = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(112.707)
qh3g2c04a = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 112.707 + 0.275
D_164_ph2g2c04a = drift('DRIFT', 0.072, 'DriftPass'); % +0.072= sb(113.054)
ph2g2c04a = drift('BPM', 0.0, 'DriftPass'); %s= 113.054 + 0.0
D_165_sh4g2c04a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(113.144)
sh4g2c04a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 113.144 + 0.2
D_166_ch2g2c04a = drift('DRIFT', 0.249, 'DriftPass'); % +0.249= sb(113.593)
ch2g2c04a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 113.593 + 0.3
D_167_b1g3c04a = drift('DRIFT', 0.031, 'DriftPass'); % +0.031= sb(113.924)
b1g3c04a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 113.924 + 2.62
D_168_cm1g4c04a = drift('DRIFT', 0.501, 'DriftPass'); % +0.501= sb(117.045)
cm1g4c04a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 117.045 + 0.2
D_169_qm1g4c04a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(117.519)
qm1g4c04a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 117.519 + 0.25
D_170_sm1g4c04a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(117.969)
sm1g4c04a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 117.969 + 0.2
D_171_fm1g4c04a = drift('DRIFT', 0.234, 'DriftPass'); % +0.234= sb(118.403)
fm1g4c04a = drift('FCOR', 0.044, 'DriftPass'); %s= 118.403 + 0.044
D_172_pm1g4c04a = drift('DRIFT', 0.292, 'DriftPass'); % +0.292= sb(118.739)
pm1g4c04a = drift('BPM', 0.0, 'DriftPass'); %s= 118.739 + 0.0
D_173_qm2g4c04a = drift('DRIFT', 0.084, 'DriftPass'); % +0.084= sb(118.823)
qm2g4c04a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 118.823 + 0.283
D_174_sm2g4c04b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(119.289)
sm2g4c04b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 119.289 + 0.25
D_175_qm2g4c04b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(119.723)
qm2g4c04b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 119.723 + 0.283
D_176_sm1g4c04b = drift('DRIFT', 0.503, 'DriftPass'); % +0.503= sb(120.509)
sm1g4c04b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 120.509 + 0.2
D_177_pm1g4c04b = drift('DRIFT', 0.263, 'DriftPass'); % +0.263= sb(120.972)
pm1g4c04b = drift('BPM', 0.0, 'DriftPass'); %s= 120.972 + 0.0
D_178_qm1g4c04b = drift('DRIFT', 0.087, 'DriftPass'); % +0.087= sb(121.059)
qm1g4c04b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 121.059 + 0.25
D_179_cm1g4c04b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(121.418)
cm1g4c04b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 121.418 + 0.3
D_180_b1g5c04b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(122.284)
b1g5c04b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 122.284 + 2.62
D_181_ql3g6c04b = drift('DRIFT', 0.588, 'DriftPass'); % +0.588= sb(125.492)
ql3g6c04b = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 125.492 + 0.275
D_182_pl2g6c04b = drift('DRIFT', 0.075, 'DriftPass'); % +0.075= sb(125.842)
pl2g6c04b = drift('BPM', 0.0, 'DriftPass'); %s= 125.842 + 0.0
D_183_sl3g6c04b = drift('DRIFT', 0.087, 'DriftPass'); % +0.087= sb(125.929)
sl3g6c04b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 125.929 + 0.2
D_184_cl2g6c04b = drift('DRIFT', 0.158, 'DriftPass'); % +0.158= sb(126.287)
cl2g6c04b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 126.287 + 0.2
D_185_ql2g6c04b = drift('DRIFT', 0.208, 'DriftPass'); % +0.208= sb(126.695)
ql2g6c04b = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 126.695 + 0.448
D_186_sl2g6c04b = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(127.393)
sl2g6c04b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 127.393 + 0.2
D_187_cl1g6c04b = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(127.724)
cl1g6c04b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 127.724 + 0.2
D_188_ql1g6c04b = drift('DRIFT', 0.132, 'DriftPass'); % +0.132= sb(128.056)
ql1g6c04b = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 128.056 + 0.275
D_189_pl1g6c04b = drift('DRIFT', 0.074, 'DriftPass'); % +0.074= sb(128.405)
pl1g6c04b = drift('BPM', 0.0, 'DriftPass'); %s= 128.405 + 0.0
D_190_sl1g6c04b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(128.493)
sl1g6c04b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 128.493 + 0.2
D_191_fl1g1c05a = drift('DRIFT', 0.447, 'DriftPass'); % +0.447= sb(129.14)
fl1g1c05a = drift('FCOR', 0.044, 'DriftPass'); %s= 129.14 + 0.044
D_192_pu1g1c05a = drift('DRIFT', 0.146, 'DriftPass'); % +0.146= sb(129.33)
pu1g1c05a = drift('UBPM', 0.0, 'DriftPass'); %s= 129.33 + 0.0
D_193_pu2g1c05a = drift('DRIFT', 2.663, 'DriftPass'); % +2.663= sb(131.993)
pu2g1c05a = drift('UBPM', 0.0, 'DriftPass'); %s= 131.993 + 0.0
D_194_cu1g1c05id2 = drift('DRIFT', 0.556, 'DriftPass'); % +0.556= sb(132.549)
cu1g1c05id2 = drift('IDCOR', 0.0, 'DriftPass'); %s= 132.549 + 0.0
cs1g1c05id2 = drift('IDSIMCOR', 0.0, 'DriftPass'); %s= 132.549 + 0.0
ivu21g1c05d = drift('INSERTION', 1.5, 'DriftPass'); %s= 132.549 + 1.5
cu2g1c05id2 = drift('IDCOR', 0.0, 'DriftPass'); %s= 134.049 + 0.0
cs2g1c05id2 = drift('IDSIMCOR', 0.0, 'DriftPass'); %s= 134.049 + 0.0
D_199_pu4g1c05a = drift('DRIFT', 0.49, 'DriftPass'); % +0.49= sb(134.539)
pu4g1c05a = drift('UBPM', 0.0, 'DriftPass'); %s= 134.539 + 0.0
D_200_fl2g1c05a = drift('DRIFT', 0.398, 'DriftPass'); % +0.398= sb(134.937)
fl2g1c05a = drift('FCOR', 0.044, 'DriftPass'); %s= 134.937 + 0.044
D_201_sl1g2c05a = drift('DRIFT', 0.312, 'DriftPass'); % +0.312= sb(135.293)
sl1g2c05a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 135.293 + 0.2
D_202_pl1g2c05a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(135.583)
pl1g2c05a = drift('BPM', 0.0, 'DriftPass'); %s= 135.583 + 0.0
D_203_ql1g2c05a = drift('DRIFT', 0.072, 'DriftPass'); % +0.072= sb(135.655)
ql1g2c05a = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 135.655 + 0.275
D_204_cl1g2c05a = drift('DRIFT', 0.132, 'DriftPass'); % +0.132= sb(136.062)
cl1g2c05a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 136.062 + 0.2
D_205_sl2g2c05a = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(136.393)
sl2g2c05a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 136.393 + 0.2
D_206_ql2g2c05a = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(136.843)
ql2g2c05a = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 136.843 + 0.448
D_207_cl2g2c05a = drift('DRIFT', 0.208, 'DriftPass'); % +0.208= sb(137.499)
cl2g2c05a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 137.499 + 0.2
D_208_sl3g2c05a = drift('DRIFT', 0.158, 'DriftPass'); % +0.158= sb(137.857)
sl3g2c05a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 137.857 + 0.2
D_209_pl2g2c05a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(138.147)
pl2g2c05a = drift('BPM', 0.0, 'DriftPass'); %s= 138.147 + 0.0
D_210_ql3g2c05a = drift('DRIFT', 0.072, 'DriftPass'); % +0.072= sb(138.219)
ql3g2c05a = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 138.219 + 0.275
D_211_b1g3c05a = drift('DRIFT', 0.588, 'DriftPass'); % +0.588= sb(139.082)
b1g3c05a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 139.082 + 2.62
D_212_cm1g4c05a = drift('DRIFT', 0.601, 'DriftPass'); % +0.601= sb(142.303)
cm1g4c05a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 142.303 + 0.0
sqmhg4c05a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 142.303 + 0.1
D_214_qm1g4c05a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(142.677)
qm1g4c05a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 142.677 + 0.25
D_215_sm1g4c05a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(143.127)
sm1g4c05a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 143.127 + 0.2
D_216_fm1g4c05a = drift('DRIFT', 0.233, 'DriftPass'); % +0.233= sb(143.56)
fm1g4c05a = drift('FCOR', 0.044, 'DriftPass'); %s= 143.56 + 0.044
D_217_pm1g4c05a = drift('DRIFT', 0.292, 'DriftPass'); % +0.292= sb(143.896)
pm1g4c05a = drift('BPM', 0.0, 'DriftPass'); %s= 143.896 + 0.0
D_218_qm2g4c05a = drift('DRIFT', 0.084, 'DriftPass'); % +0.084= sb(143.98)
qm2g4c05a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 143.98 + 0.283
D_219_sm2g4c05b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(144.447)
sm2g4c05b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 144.447 + 0.25
D_220_qm2g4c05b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(144.88)
qm2g4c05b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 144.88 + 0.283
D_221_sm1g4c05b = drift('DRIFT', 0.504, 'DriftPass'); % +0.504= sb(145.667)
sm1g4c05b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 145.667 + 0.2
D_222_pm1g4c05b = drift('DRIFT', 0.262, 'DriftPass'); % +0.262= sb(146.129)
pm1g4c05b = drift('BPM', 0.0, 'DriftPass'); %s= 146.129 + 0.0
D_223_qm1g4c05b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(146.217)
qm1g4c05b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 146.217 + 0.25
D_224_cm1g4c05b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(146.576)
cm1g4c05b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 146.576 + 0.3
D_225_b1g5c05b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(147.442)
b1g5c05b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 147.442 + 2.62
D_226_ch2g6c05b = drift('DRIFT', 0.216, 'DriftPass'); % +0.216= sb(150.278)
ch2g6c05b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 150.278 + 0.3
D_227_sh4g6c05b = drift('DRIFT', 0.064, 'DriftPass'); % +0.064= sb(150.642)
sh4g6c05b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 150.642 + 0.2
D_228_ph2g6c05b = drift('DRIFT', 0.089, 'DriftPass'); % +0.089= sb(150.931)
ph2g6c05b = drift('BPM', 0.0, 'DriftPass'); %s= 150.931 + 0.0
D_229_qh3g6c05b = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(151.004)
qh3g6c05b = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 151.004 + 0.275
D_230_sh3g6c05b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(151.462)
sh3g6c05b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 151.462 + 0.2
D_231_qh2g6c05b = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(151.852)
qh2g6c05b = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 151.852 + 0.448
D_232_ch1g6c05b = drift('DRIFT', 0.484, 'DriftPass'); % +0.484= sb(152.784)
ch1g6c05b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 152.784 + 0.2
D_233_qh1g6c05b = drift('DRIFT', 0.12, 'DriftPass'); % +0.12= sb(153.104)
qh1g6c05b = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 153.104 + 0.275
D_234_ph1g6c05b = drift('DRIFT', 0.077, 'DriftPass'); % +0.077= sb(153.456)
ph1g6c05b = drift('BPM', 0.0, 'DriftPass'); %s= 153.456 + 0.0
D_235_sh1g6c05b = drift('DRIFT', 0.086, 'DriftPass'); % +0.086= sb(153.542)
sh1g6c05b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 153.542 + 0.2
D_236_fh1g1c06a = drift('DRIFT', 0.44, 'DriftPass'); % +0.44= sb(154.182)
fh1g1c06a = drift('FCOR', 0.044, 'DriftPass'); %s= 154.182 + 0.044
D_237_fh2g1c06a = drift('DRIFT', 8.459, 'DriftPass'); % +8.459= sb(162.685)
fh2g1c06a = drift('FCOR', 0.044, 'DriftPass'); %s= 162.685 + 0.044
D_238_sh1g2c06a = drift('DRIFT', 0.313, 'DriftPass'); % +0.313= sb(163.042)
sh1g2c06a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 163.042 + 0.2
D_239_ph1g2c06a = drift('DRIFT', 0.085, 'DriftPass'); % +0.085= sb(163.327)
ph1g2c06a = drift('BPM', 0.0, 'DriftPass'); %s= 163.327 + 0.0
D_240_qh1g2c06a = drift('DRIFT', 0.077, 'DriftPass'); % +0.077= sb(163.404)
qh1g2c06a = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 163.404 + 0.275
D_241_ch1g2c06a = drift('DRIFT', 0.245, 'DriftPass'); % +0.245= sb(163.924)
ch1g2c06a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 163.924 + 0.0
sqhhg2c06a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 163.924 + 0.1
D_243_qh2g2c06a = drift('DRIFT', 0.46, 'DriftPass'); % +0.46= sb(164.484)
qh2g2c06a = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 164.484 + 0.448
D_244_sh3g2c06a = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(165.122)
sh3g2c06a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 165.122 + 0.2
D_245_qh3g2c06a = drift('DRIFT', 0.182, 'DriftPass'); % +0.182= sb(165.504)
qh3g2c06a = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 165.504 + 0.275
D_246_ph2g2c06a = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(165.852)
ph2g2c06a = drift('BPM', 0.0, 'DriftPass'); %s= 165.852 + 0.0
D_247_sh4g2c06a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(165.942)
sh4g2c06a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 165.942 + 0.2
D_248_ch2g2c06a = drift('DRIFT', 0.248, 'DriftPass'); % +0.248= sb(166.39)
ch2g2c06a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 166.39 + 0.3
D_249_b1g3c06a = drift('DRIFT', 0.032, 'DriftPass'); % +0.032= sb(166.722)
b1g3c06a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 166.722 + 2.62
D_250_cm1g4c06a = drift('DRIFT', 0.501, 'DriftPass'); % +0.501= sb(169.843)
cm1g4c06a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 169.843 + 0.2
D_251_qm1g4c06a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(170.317)
qm1g4c06a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 170.317 + 0.25
D_252_sm1g4c06a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(170.767)
sm1g4c06a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 170.767 + 0.2
D_253_fm1g4c06a = drift('DRIFT', 0.233, 'DriftPass'); % +0.233= sb(171.2)
fm1g4c06a = drift('FCOR', 0.044, 'DriftPass'); %s= 171.2 + 0.044
D_254_pm1g4c06a = drift('DRIFT', 0.292, 'DriftPass'); % +0.292= sb(171.536)
pm1g4c06a = drift('BPM', 0.0, 'DriftPass'); %s= 171.536 + 0.0
D_255_qm2g4c06a = drift('DRIFT', 0.084, 'DriftPass'); % +0.084= sb(171.62)
qm2g4c06a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 171.62 + 0.283
D_256_sm2g4c06b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(172.087)
sm2g4c06b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 172.087 + 0.25
D_257_qm2g4c06b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(172.52)
qm2g4c06b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 172.52 + 0.283
D_258_sm1g4c06b = drift('DRIFT', 0.504, 'DriftPass'); % +0.504= sb(173.307)
sm1g4c06b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 173.307 + 0.2
D_259_pm1g4c06b = drift('DRIFT', 0.262, 'DriftPass'); % +0.262= sb(173.769)
pm1g4c06b = drift('BPM', 0.0, 'DriftPass'); %s= 173.769 + 0.0
D_260_qm1g4c06b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(173.857)
qm1g4c06b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 173.857 + 0.25
D_261_cm1g4c06b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(174.216)
cm1g4c06b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 174.216 + 0.3
D_262_b1g5c06b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(175.082)
b1g5c06b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 175.082 + 2.62
D_263_ql3g6c06b = drift('DRIFT', 0.587, 'DriftPass'); % +0.587= sb(178.289)
ql3g6c06b = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 178.289 + 0.275
D_264_pl2g6c06b = drift('DRIFT', 0.075, 'DriftPass'); % +0.075= sb(178.639)
pl2g6c06b = drift('BPM', 0.0, 'DriftPass'); %s= 178.639 + 0.0
D_265_sl3g6c06b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(178.727)
sl3g6c06b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 178.727 + 0.2
D_266_cl2g6c06b = drift('DRIFT', 0.157, 'DriftPass'); % +0.157= sb(179.084)
cl2g6c06b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 179.084 + 0.2
D_267_ql2g6c06b = drift('DRIFT', 0.208, 'DriftPass'); % +0.208= sb(179.492)
ql2g6c06b = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 179.492 + 0.448
D_268_sl2g6c06b = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(180.19)
sl2g6c06b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 180.19 + 0.2
D_269_cl1g6c06b = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(180.521)
cl1g6c06b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 180.521 + 0.2
D_270_ql1g6c06b = drift('DRIFT', 0.132, 'DriftPass'); % +0.132= sb(180.853)
ql1g6c06b = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 180.853 + 0.275
D_271_pl1g6c06b = drift('DRIFT', 0.074, 'DriftPass'); % +0.074= sb(181.202)
pl1g6c06b = drift('BPM', 0.0, 'DriftPass'); %s= 181.202 + 0.0
D_272_sl1g6c06b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(181.29)
sl1g6c06b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 181.29 + 0.2
D_273_fl1g1c07a = drift('DRIFT', 0.447, 'DriftPass'); % +0.447= sb(181.937)
fl1g1c07a = drift('FCOR', 0.044, 'DriftPass'); %s= 181.937 + 0.044
D_274_fl2g1c07a = drift('DRIFT', 5.753, 'DriftPass'); % +5.753= sb(187.734)
fl2g1c07a = drift('FCOR', 0.044, 'DriftPass'); %s= 187.734 + 0.044
D_275_sl1g2c07a = drift('DRIFT', 0.312, 'DriftPass'); % +0.312= sb(188.09)
sl1g2c07a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 188.09 + 0.2
D_276_pl1g2c07a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(188.38)
pl1g2c07a = drift('BPM', 0.0, 'DriftPass'); %s= 188.38 + 0.0
D_277_ql1g2c07a = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(188.453)
ql1g2c07a = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 188.453 + 0.275
D_278_cl1g2c07a = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(188.859)
cl1g2c07a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 188.859 + 0.2
D_279_sl2g2c07a = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(189.19)
sl2g2c07a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 189.19 + 0.2
D_280_ql2g2c07a = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(189.64)
ql2g2c07a = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 189.64 + 0.448
D_281_cl2g2c07a = drift('DRIFT', 0.208, 'DriftPass'); % +0.208= sb(190.296)
cl2g2c07a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 190.296 + 0.2
D_282_sl3g2c07a = drift('DRIFT', 0.158, 'DriftPass'); % +0.158= sb(190.654)
sl3g2c07a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 190.654 + 0.2
D_283_pl2g2c07a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(190.944)
pl2g2c07a = drift('BPM', 0.0, 'DriftPass'); %s= 190.944 + 0.0
D_284_ql3g2c07a = drift('DRIFT', 0.072, 'DriftPass'); % +0.072= sb(191.016)
ql3g2c07a = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 191.016 + 0.275
D_285_b1g3c07a = drift('DRIFT', 0.588, 'DriftPass'); % +0.588= sb(191.879)
b1g3c07a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 191.879 + 2.62
D_286_cm1g4c07a = drift('DRIFT', 0.601, 'DriftPass'); % +0.601= sb(195.1)
cm1g4c07a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 195.1 + 0.0
sqmhg4c07a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 195.1 + 0.1
D_288_qm1g4c07a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(195.474)
qm1g4c07a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 195.474 + 0.25
D_289_sm1g4c07a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(195.924)
sm1g4c07a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 195.924 + 0.2
D_290_fm1g4c07a = drift('DRIFT', 0.233, 'DriftPass'); % +0.233= sb(196.357)
fm1g4c07a = drift('FCOR', 0.044, 'DriftPass'); %s= 196.357 + 0.044
D_291_pm1g4c07a = drift('DRIFT', 0.292, 'DriftPass'); % +0.292= sb(196.693)
pm1g4c07a = drift('BPM', 0.0, 'DriftPass'); %s= 196.693 + 0.0
D_292_qm2g4c07a = drift('DRIFT', 0.084, 'DriftPass'); % +0.084= sb(196.777)
qm2g4c07a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 196.777 + 0.283
D_293_sm2g4c07b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(197.244)
sm2g4c07b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 197.244 + 0.25
D_294_qm2g4c07b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(197.677)
qm2g4c07b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 197.677 + 0.283
D_295_sm1g4c07b = drift('DRIFT', 0.504, 'DriftPass'); % +0.504= sb(198.464)
sm1g4c07b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 198.464 + 0.2
D_296_pm1g4c07b = drift('DRIFT', 0.262, 'DriftPass'); % +0.262= sb(198.926)
pm1g4c07b = drift('BPM', 0.0, 'DriftPass'); %s= 198.926 + 0.0
D_297_qm1g4c07b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(199.014)
qm1g4c07b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 199.014 + 0.25
D_298_cm1g4c07b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(199.373)
cm1g4c07b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 199.373 + 0.3
D_299_b1g5c07b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(200.239)
b1g5c07b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 200.239 + 2.62
D_300_ch2g6c07b = drift('DRIFT', 0.216, 'DriftPass'); % +0.216= sb(203.075)
ch2g6c07b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 203.075 + 0.3
D_301_sh4g6c07b = drift('DRIFT', 0.064, 'DriftPass'); % +0.064= sb(203.439)
sh4g6c07b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 203.439 + 0.2
D_302_ph2g6c07b = drift('DRIFT', 0.089, 'DriftPass'); % +0.089= sb(203.728)
ph2g6c07b = drift('BPM', 0.0, 'DriftPass'); %s= 203.728 + 0.0
D_303_qh3g6c07b = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(203.801)
qh3g6c07b = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 203.801 + 0.275
D_304_sh3g6c07b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(204.259)
sh3g6c07b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 204.259 + 0.2
D_305_qh2g6c07b = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(204.649)
qh2g6c07b = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 204.649 + 0.448
D_306_ch1g6c07b = drift('DRIFT', 0.484, 'DriftPass'); % +0.484= sb(205.581)
ch1g6c07b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 205.581 + 0.2
D_307_qh1g6c07b = drift('DRIFT', 0.12, 'DriftPass'); % +0.12= sb(205.901)
qh1g6c07b = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 205.901 + 0.275
D_308_ph1g6c07b = drift('DRIFT', 0.077, 'DriftPass'); % +0.077= sb(206.253)
ph1g6c07b = drift('BPM', 0.0, 'DriftPass'); %s= 206.253 + 0.0
D_309_sh1g6c07b = drift('DRIFT', 0.086, 'DriftPass'); % +0.086= sb(206.339)
sh1g6c07b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 206.339 + 0.2
D_310_fh1g1c08a = drift('DRIFT', 0.441, 'DriftPass'); % +0.441= sb(206.98)
fh1g1c08a = drift('FCOR', 0.044, 'DriftPass'); %s= 206.98 + 0.044
D_311_pu1g1c08a = drift('DRIFT', 0.503, 'DriftPass'); % +0.503= sb(207.527)
pu1g1c08a = drift('UBPM', 0.0, 'DriftPass'); %s= 207.527 + 0.0
D_312_cu1g1c08id1 = drift('DRIFT', 0.071, 'DriftPass'); % +0.071= sb(207.598)
cu1g1c08id1 = drift('IDCOR', 0.0, 'DriftPass'); %s= 207.598 + 0.0
cs1g1c08id1 = drift('IDSIMCOR', 0.0, 'DriftPass'); %s= 207.598 + 0.0
dw100g1c08u = drift('INSERTION', 3.4, 'DriftPass'); %s= 207.598 + 3.4
cu2g1c08id1 = drift('IDCOR', 0.0, 'DriftPass'); %s= 210.998 + 0.0
cs2g1c08id1 = drift('IDSIMCOR', 0.0, 'DriftPass'); %s= 210.998 + 0.0
D_317_cu1g1c08id2 = drift('DRIFT', 0.381, 'DriftPass'); % +0.381= sb(211.379)
cu1g1c08id2 = drift('IDCOR', 0.0, 'DriftPass'); %s= 211.379 + 0.0
cs1g1c08id2 = drift('IDSIMCOR', 0.0, 'DriftPass'); %s= 211.379 + 0.0
dw100g1c08d = drift('INSERTION', 3.4, 'DriftPass'); %s= 211.379 + 3.4
cu2g1c08id2 = drift('IDCOR', 0.0, 'DriftPass'); %s= 214.779 + 0.0
cs2g1c08id2 = drift('IDSIMCOR', 0.0, 'DriftPass'); %s= 214.779 + 0.0
D_322_pu4g1c08a = drift('DRIFT', 0.087, 'DriftPass'); % +0.087= sb(214.866)
pu4g1c08a = drift('UBPM', 0.0, 'DriftPass'); %s= 214.866 + 0.0
D_323_fh2g1c08a = drift('DRIFT', 0.617, 'DriftPass'); % +0.617= sb(215.483)
fh2g1c08a = drift('FCOR', 0.044, 'DriftPass'); %s= 215.483 + 0.044
D_324_sh1g2c08a = drift('DRIFT', 0.312, 'DriftPass'); % +0.312= sb(215.839)
sh1g2c08a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 215.839 + 0.2
D_325_ph1g2c08a = drift('DRIFT', 0.085, 'DriftPass'); % +0.085= sb(216.124)
ph1g2c08a = drift('BPM', 0.0, 'DriftPass'); %s= 216.124 + 0.0
D_326_qh1g2c08a = drift('DRIFT', 0.077, 'DriftPass'); % +0.077= sb(216.201)
qh1g2c08a = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 216.201 + 0.275
D_327_ch1g2c08a = drift('DRIFT', 0.245, 'DriftPass'); % +0.245= sb(216.721)
ch1g2c08a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 216.721 + 0.0
sqhhg2c08a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 216.721 + 0.1
D_329_qh2g2c08a = drift('DRIFT', 0.46, 'DriftPass'); % +0.46= sb(217.281)
qh2g2c08a = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 217.281 + 0.448
D_330_sh3g2c08a = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(217.919)
sh3g2c08a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 217.919 + 0.2
D_331_qh3g2c08a = drift('DRIFT', 0.182, 'DriftPass'); % +0.182= sb(218.301)
qh3g2c08a = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 218.301 + 0.275
D_332_ph2g2c08a = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(218.649)
ph2g2c08a = drift('BPM', 0.0, 'DriftPass'); %s= 218.649 + 0.0
D_333_sh4g2c08a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(218.739)
sh4g2c08a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 218.739 + 0.2
D_334_ch2g2c08a = drift('DRIFT', 0.248, 'DriftPass'); % +0.248= sb(219.187)
ch2g2c08a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 219.187 + 0.3
D_335_b1g3c08a = drift('DRIFT', 0.032, 'DriftPass'); % +0.032= sb(219.519)
b1g3c08a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 219.519 + 2.62
D_336_cm1g4c08a = drift('DRIFT', 0.501, 'DriftPass'); % +0.501= sb(222.64)
cm1g4c08a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 222.64 + 0.2
D_337_qm1g4c08a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(223.114)
qm1g4c08a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 223.114 + 0.25
D_338_sm1g4c08a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(223.564)
sm1g4c08a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 223.564 + 0.2
D_339_fm1g4c08a = drift('DRIFT', 0.233, 'DriftPass'); % +0.233= sb(223.997)
fm1g4c08a = drift('FCOR', 0.044, 'DriftPass'); %s= 223.997 + 0.044
D_340_pm1g4c08a = drift('DRIFT', 0.292, 'DriftPass'); % +0.292= sb(224.333)
pm1g4c08a = drift('BPM', 0.0, 'DriftPass'); %s= 224.333 + 0.0
D_341_qm2g4c08a = drift('DRIFT', 0.084, 'DriftPass'); % +0.084= sb(224.417)
qm2g4c08a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 224.417 + 0.283
D_342_sm2g4c08b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(224.884)
sm2g4c08b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 224.884 + 0.25
D_343_qm2g4c08b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(225.317)
qm2g4c08b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 225.317 + 0.283
D_344_sm1g4c08b = drift('DRIFT', 0.504, 'DriftPass'); % +0.504= sb(226.104)
sm1g4c08b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 226.104 + 0.2
D_345_pm1g4c08b = drift('DRIFT', 0.262, 'DriftPass'); % +0.262= sb(226.566)
pm1g4c08b = drift('BPM', 0.0, 'DriftPass'); %s= 226.566 + 0.0
D_346_qm1g4c08b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(226.654)
qm1g4c08b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 226.654 + 0.25
D_347_cm1g4c08b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(227.013)
cm1g4c08b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 227.013 + 0.3
D_348_b1g5c08b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(227.879)
b1g5c08b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 227.879 + 2.62
D_349_ql3g6c08b = drift('DRIFT', 0.587, 'DriftPass'); % +0.587= sb(231.086)
ql3g6c08b = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 231.086 + 0.275
D_350_pl2g6c08b = drift('DRIFT', 0.075, 'DriftPass'); % +0.075= sb(231.436)
pl2g6c08b = drift('BPM', 0.0, 'DriftPass'); %s= 231.436 + 0.0
D_351_sl3g6c08b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(231.524)
sl3g6c08b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 231.524 + 0.2
D_352_cl2g6c08b = drift('DRIFT', 0.157, 'DriftPass'); % +0.157= sb(231.881)
cl2g6c08b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 231.881 + 0.2
D_353_ql2g6c08b = drift('DRIFT', 0.208, 'DriftPass'); % +0.208= sb(232.289)
ql2g6c08b = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 232.289 + 0.448
D_354_sl2g6c08b = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(232.987)
sl2g6c08b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 232.987 + 0.2
D_355_cl1g6c08b = drift('DRIFT', 0.132, 'DriftPass'); % +0.132= sb(233.319)
cl1g6c08b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 233.319 + 0.2
D_356_ql1g6c08b = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(233.65)
ql1g6c08b = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 233.65 + 0.275
D_357_pl1g6c08b = drift('DRIFT', 0.075, 'DriftPass'); % +0.075= sb(234.0)
pl1g6c08b = drift('BPM', 0.0, 'DriftPass'); %s= 234.0 + 0.0
D_358_sl1g6c08b = drift('DRIFT', 0.087, 'DriftPass'); % +0.087= sb(234.087)
sl1g6c08b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 234.087 + 0.2
D_359_fl1g1c09a = drift('DRIFT', 0.447, 'DriftPass'); % +0.447= sb(234.734)
fl1g1c09a = drift('FCOR', 0.044, 'DriftPass'); %s= 234.734 + 0.044
D_360_fl2g1c09a = drift('DRIFT', 5.753, 'DriftPass'); % +5.753= sb(240.531)
fl2g1c09a = drift('FCOR', 0.044, 'DriftPass'); %s= 240.531 + 0.044
D_361_sl1g2c09a = drift('DRIFT', 0.312, 'DriftPass'); % +0.312= sb(240.887)
sl1g2c09a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 240.887 + 0.2
D_362_pl1g2c09a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(241.177)
pl1g2c09a = drift('BPM', 0.0, 'DriftPass'); %s= 241.177 + 0.0
D_363_ql1g2c09a = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(241.25)
ql1g2c09a = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 241.25 + 0.275
D_364_cl1g2c09a = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(241.656)
cl1g2c09a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 241.656 + 0.2
D_365_sl2g2c09a = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(241.987)
sl2g2c09a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 241.987 + 0.2
D_366_ql2g2c09a = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(242.437)
ql2g2c09a = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 242.437 + 0.448
D_367_cl2g2c09a = drift('DRIFT', 0.208, 'DriftPass'); % +0.208= sb(243.093)
cl2g2c09a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 243.093 + 0.2
D_368_sl3g2c09a = drift('DRIFT', 0.158, 'DriftPass'); % +0.158= sb(243.451)
sl3g2c09a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 243.451 + 0.2
D_369_pl2g2c09a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(243.741)
pl2g2c09a = drift('BPM', 0.0, 'DriftPass'); %s= 243.741 + 0.0
D_370_ql3g2c09a = drift('DRIFT', 0.072, 'DriftPass'); % +0.072= sb(243.813)
ql3g2c09a = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 243.813 + 0.275
D_371_b1g3c09a = drift('DRIFT', 0.588, 'DriftPass'); % +0.588= sb(244.676)
b1g3c09a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 244.676 + 2.62
D_372_cm1g4c09a = drift('DRIFT', 0.601, 'DriftPass'); % +0.601= sb(247.897)
cm1g4c09a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 247.897 + 0.0
D_373_sqmhg4c09a = drift('DRIFT', 2.84217094304e-14, 'DriftPass'); % +2.84217094304e-14= sb(247.897)
sqmhg4c09a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 247.897 + 0.1
D_374_qm1g4c09a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(248.271)
qm1g4c09a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 248.271 + 0.25
D_375_sm1g4c09a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(248.721)
sm1g4c09a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 248.721 + 0.2
D_376_fm1g4c09a = drift('DRIFT', 0.233, 'DriftPass'); % +0.233= sb(249.154)
fm1g4c09a = drift('FCOR', 0.044, 'DriftPass'); %s= 249.154 + 0.044
D_377_pm1g4c09a = drift('DRIFT', 0.293, 'DriftPass'); % +0.293= sb(249.491)
pm1g4c09a = drift('BPM', 0.0, 'DriftPass'); %s= 249.491 + 0.0
D_378_qm2g4c09a = drift('DRIFT', 0.083, 'DriftPass'); % +0.083= sb(249.574)
qm2g4c09a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 249.574 + 0.283
D_379_sm2g4c09b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(250.041)
sm2g4c09b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 250.041 + 0.25
D_380_qm2g4c09b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(250.474)
qm2g4c09b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 250.474 + 0.283
D_381_sm1g4c09b = drift('DRIFT', 0.504, 'DriftPass'); % +0.504= sb(251.261)
sm1g4c09b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 251.261 + 0.2
D_382_pm1g4c09b = drift('DRIFT', 0.262, 'DriftPass'); % +0.262= sb(251.723)
pm1g4c09b = drift('BPM', 0.0, 'DriftPass'); %s= 251.723 + 0.0
D_383_qm1g4c09b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(251.811)
qm1g4c09b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 251.811 + 0.25
D_384_cm1g4c09b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(252.17)
cm1g4c09b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 252.17 + 0.3
D_385_b1g5c09b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(253.036)
b1g5c09b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 253.036 + 2.62
D_386_ch2g6c09b = drift('DRIFT', 0.216, 'DriftPass'); % +0.216= sb(255.872)
ch2g6c09b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 255.872 + 0.3
D_387_sh4g6c09b = drift('DRIFT', 0.064, 'DriftPass'); % +0.064= sb(256.236)
sh4g6c09b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 256.236 + 0.2
D_388_ph2g6c09b = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(256.526)
ph2g6c09b = drift('BPM', 0.0, 'DriftPass'); %s= 256.526 + 0.0
D_389_qh3g6c09b = drift('DRIFT', 0.072, 'DriftPass'); % +0.072= sb(256.598)
qh3g6c09b = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 256.598 + 0.275
D_390_sh3g6c09b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(257.056)
sh3g6c09b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 257.056 + 0.2
D_391_qh2g6c09b = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(257.446)
qh2g6c09b = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 257.446 + 0.448
D_392_ch1g6c09b = drift('DRIFT', 0.484, 'DriftPass'); % +0.484= sb(258.378)
ch1g6c09b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 258.378 + 0.2
D_393_qh1g6c09b = drift('DRIFT', 0.12, 'DriftPass'); % +0.12= sb(258.698)
qh1g6c09b = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 258.698 + 0.275
D_394_ph1g6c09b = drift('DRIFT', 0.078, 'DriftPass'); % +0.078= sb(259.051)
ph1g6c09b = drift('BPM', 0.0, 'DriftPass'); %s= 259.051 + 0.0
D_395_sh1g6c09b = drift('DRIFT', 0.085, 'DriftPass'); % +0.085= sb(259.136)
sh1g6c09b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 259.136 + 0.2
D_396_fh1g1c10a = drift('DRIFT', 0.441, 'DriftPass'); % +0.441= sb(259.777)
fh1g1c10a = drift('FCOR', 0.044, 'DriftPass'); %s= 259.777 + 0.044
D_397_pu1g1c10a = drift('DRIFT', 0.266, 'DriftPass'); % +0.266= sb(260.087)
pu1g1c10a = drift('UBPM', 0.0, 'DriftPass'); %s= 260.087 + 0.0
D_398_cu1g1c10id1 = drift('DRIFT', 2.399, 'DriftPass'); % +2.399= sb(262.486)
cu1g1c10id1 = drift('IDCOR', 0.0, 'DriftPass'); %s= 262.486 + 0.0
cs1g1c10id1 = drift('IDSIMCOR', 0.0, 'DriftPass'); %s= 262.486 + 0.0
ivu22g1c10c = drift('INSERTION', 3.0, 'DriftPass'); %s= 262.486 + 3.0
cu2g1c10id2 = drift('IDCOR', 0.0, 'DriftPass'); %s= 265.486 + 0.0
cs2g1c10id2 = drift('IDSIMCOR', 0.0, 'DriftPass'); %s= 265.486 + 0.0
D_403_pu4g1c10a = drift('DRIFT', 2.529, 'DriftPass'); % +2.529= sb(268.015)
pu4g1c10a = drift('UBPM', 0.0, 'DriftPass'); %s= 268.015 + 0.0
D_404_fh2g1c10a = drift('DRIFT', 0.265, 'DriftPass'); % +0.265= sb(268.28)
fh2g1c10a = drift('FCOR', 0.044, 'DriftPass'); %s= 268.28 + 0.044
D_405_sh1g2c10a = drift('DRIFT', 0.312, 'DriftPass'); % +0.312= sb(268.636)
sh1g2c10a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 268.636 + 0.2
D_406_ph1g2c10a = drift('DRIFT', 0.085, 'DriftPass'); % +0.085= sb(268.921)
ph1g2c10a = drift('BPM', 0.0, 'DriftPass'); %s= 268.921 + 0.0
D_407_qh1g2c10a = drift('DRIFT', 0.0770000000001, 'DriftPass'); % +0.0770000000001= sb(268.998)
qh1g2c10a = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 268.998 + 0.275
D_408_ch1g2c10a = drift('DRIFT', 0.245, 'DriftPass'); % +0.245= sb(269.518)
ch1g2c10a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 269.518 + 0.0
sqhhg2c10a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 269.518 + 0.1
D_410_qh2g2c10a = drift('DRIFT', 0.46, 'DriftPass'); % +0.46= sb(270.078)
qh2g2c10a = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 270.078 + 0.448
D_411_sh3g2c10a = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(270.716)
sh3g2c10a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 270.716 + 0.2
D_412_qh3g2c10a = drift('DRIFT', 0.182, 'DriftPass'); % +0.182= sb(271.098)
qh3g2c10a = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 271.098 + 0.275
D_413_ph2g2c10a = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(271.446)
ph2g2c10a = drift('BPM', 0.0, 'DriftPass'); %s= 271.446 + 0.0
D_414_sh4g2c10a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(271.536)
sh4g2c10a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 271.536 + 0.2
D_415_ch2g2c10a = drift('DRIFT', 0.248, 'DriftPass'); % +0.248= sb(271.984)
ch2g2c10a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 271.984 + 0.3
D_416_b1g3c10a = drift('DRIFT', 0.032, 'DriftPass'); % +0.032= sb(272.316)
b1g3c10a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 272.316 + 2.62
D_417_cm1g4c10a = drift('DRIFT', 0.501, 'DriftPass'); % +0.501= sb(275.437)
cm1g4c10a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 275.437 + 0.2
D_418_qm1g4c10a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(275.911)
qm1g4c10a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 275.911 + 0.25
D_419_sm1g4c10a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(276.361)
sm1g4c10a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 276.361 + 0.2
D_420_fm1g4c10a = drift('DRIFT', 0.233, 'DriftPass'); % +0.233= sb(276.794)
fm1g4c10a = drift('FCOR', 0.044, 'DriftPass'); %s= 276.794 + 0.044
D_421_pm1g4c10a = drift('DRIFT', 0.293, 'DriftPass'); % +0.293= sb(277.131)
pm1g4c10a = drift('BPM', 0.0, 'DriftPass'); %s= 277.131 + 0.0
D_422_qm2g4c10a = drift('DRIFT', 0.083, 'DriftPass'); % +0.083= sb(277.214)
qm2g4c10a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 277.214 + 0.283
D_423_sm2g4c10b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(277.681)
sm2g4c10b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 277.681 + 0.25
D_424_qm2g4c10b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(278.114)
qm2g4c10b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 278.114 + 0.283
D_425_sm1g4c10b = drift('DRIFT', 0.504, 'DriftPass'); % +0.504= sb(278.901)
sm1g4c10b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 278.901 + 0.2
D_426_pm1g4c10b = drift('DRIFT', 0.262, 'DriftPass'); % +0.262= sb(279.363)
pm1g4c10b = drift('BPM', 0.0, 'DriftPass'); %s= 279.363 + 0.0
D_427_qm1g4c10b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(279.451)
qm1g4c10b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 279.451 + 0.25
D_428_cm1g4c10b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(279.81)
cm1g4c10b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 279.81 + 0.3
D_429_b1g5c10b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(280.676)
b1g5c10b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 280.676 + 2.62
D_430_ql3g6c10b = drift('DRIFT', 0.587, 'DriftPass'); % +0.587= sb(283.883)
ql3g6c10b = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 283.883 + 0.275
D_431_pl2g6c10b = drift('DRIFT', 0.075, 'DriftPass'); % +0.075= sb(284.233)
pl2g6c10b = drift('BPM', 0.0, 'DriftPass'); %s= 284.233 + 0.0
D_432_sl3g6c10b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(284.321)
sl3g6c10b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 284.321 + 0.2
D_433_cl2g6c10b = drift('DRIFT', 0.157, 'DriftPass'); % +0.157= sb(284.678)
cl2g6c10b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 284.678 + 0.2
D_434_ql2g6c10b = drift('DRIFT', 0.209, 'DriftPass'); % +0.209= sb(285.087)
ql2g6c10b = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 285.087 + 0.448
D_435_sl2g6c10b = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(285.785)
sl2g6c10b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 285.785 + 0.2
D_436_cl1g6c10b = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(286.116)
cl1g6c10b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 286.116 + 0.2
D_437_ql1g6c10b = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(286.447)
ql1g6c10b = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 286.447 + 0.275
D_438_pl1g6c10b = drift('DRIFT', 0.075, 'DriftPass'); % +0.075= sb(286.797)
pl1g6c10b = drift('BPM', 0.0, 'DriftPass'); %s= 286.797 + 0.0
D_439_sl1g6c10b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(286.885)
sl1g6c10b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 286.885 + 0.2
D_440_fl1g1c11a = drift('DRIFT', 0.446, 'DriftPass'); % +0.446= sb(287.531)
fl1g1c11a = drift('FCOR', 0.044, 'DriftPass'); %s= 287.531 + 0.044
D_441_pu1g1c11a = drift('DRIFT', 0.267, 'DriftPass'); % +0.267= sb(287.842)
pu1g1c11a = drift('UBPM', 0.0, 'DriftPass'); %s= 287.842 + 0.0
D_442_cu1g1c11id1 = drift('DRIFT', 1.043, 'DriftPass'); % +1.043= sb(288.885)
cu1g1c11id1 = drift('IDCOR', 0.0, 'DriftPass'); %s= 288.885 + 0.0
cs1g1c11id1 = drift('IDSIMCOR', 0.0, 'DriftPass'); %s= 288.885 + 0.0
ivu20g1c11c = drift('INSERTION', 3.0, 'DriftPass'); %s= 288.885 + 3.0
cu2g1c11id2 = drift('IDCOR', 0.0, 'DriftPass'); %s= 291.885 + 0.0
cs2g1c11id2 = drift('IDSIMCOR', 0.0, 'DriftPass'); %s= 291.885 + 0.0
D_447_pu4g1c11a = drift('DRIFT', 1.178, 'DriftPass'); % +1.178= sb(293.063)
pu4g1c11a = drift('UBPM', 0.0, 'DriftPass'); %s= 293.063 + 0.0
D_448_fl2g1c11a = drift('DRIFT', 0.265, 'DriftPass'); % +0.265= sb(293.328)
fl2g1c11a = drift('FCOR', 0.044, 'DriftPass'); %s= 293.328 + 0.044
D_449_sl1g2c11a = drift('DRIFT', 0.313, 'DriftPass'); % +0.313= sb(293.685)
sl1g2c11a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 293.685 + 0.2
D_450_pl1g2c11a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(293.975)
pl1g2c11a = drift('BPM', 0.0, 'DriftPass'); %s= 293.975 + 0.0
D_451_ql1g2c11a = drift('DRIFT', 0.072, 'DriftPass'); % +0.072= sb(294.047)
ql1g2c11a = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 294.047 + 0.275
D_452_cl1g2c11a = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(294.453)
cl1g2c11a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 294.453 + 0.2
D_453_sl2g2c11a = drift('DRIFT', 0.132, 'DriftPass'); % +0.132= sb(294.785)
sl2g2c11a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 294.785 + 0.2
D_454_ql2g2c11a = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(295.235)
ql2g2c11a = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 295.235 + 0.448
D_455_cl2g2c11a = drift('DRIFT', 0.208, 'DriftPass'); % +0.208= sb(295.891)
cl2g2c11a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 295.891 + 0.2
D_456_sl3g2c11a = drift('DRIFT', 0.157, 'DriftPass'); % +0.157= sb(296.248)
sl3g2c11a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 296.248 + 0.2
D_457_pl2g2c11a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(296.538)
pl2g2c11a = drift('BPM', 0.0, 'DriftPass'); %s= 296.538 + 0.0
D_458_ql3g2c11a = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(296.611)
ql3g2c11a = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 296.611 + 0.275
D_459_b1g3c11a = drift('DRIFT', 0.587, 'DriftPass'); % +0.587= sb(297.473)
b1g3c11a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 297.473 + 2.62
D_460_cm1g4c11a = drift('DRIFT', 0.601, 'DriftPass'); % +0.601= sb(300.694)
cm1g4c11a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 300.694 + 0.0
sqmhg4c11a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 300.694 + 0.1
D_462_qm1g4c11a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(301.068)
qm1g4c11a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 301.068 + 0.25
D_463_sm1g4c11a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(301.518)
sm1g4c11a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 301.518 + 0.2
D_464_fm1g4c11a = drift('DRIFT', 0.233, 'DriftPass'); % +0.233= sb(301.951)
fm1g4c11a = drift('FCOR', 0.044, 'DriftPass'); %s= 301.951 + 0.044
D_465_pm1g4c11a = drift('DRIFT', 0.293, 'DriftPass'); % +0.293= sb(302.288)
pm1g4c11a = drift('BPM', 0.0, 'DriftPass'); %s= 302.288 + 0.0
D_466_qm2g4c11a = drift('DRIFT', 0.0839999999999, 'DriftPass'); % +0.0839999999999= sb(302.372)
qm2g4c11a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 302.372 + 0.283
D_467_sm2g4c11b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(302.838)
sm2g4c11b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 302.838 + 0.25
D_468_qm2g4c11b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(303.272)
qm2g4c11b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 303.272 + 0.283
D_469_sm1g4c11b = drift('DRIFT', 0.503, 'DriftPass'); % +0.503= sb(304.058)
sm1g4c11b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 304.058 + 0.2
D_470_pm1g4c11b = drift('DRIFT', 0.262, 'DriftPass'); % +0.262= sb(304.52)
pm1g4c11b = drift('BPM', 0.0, 'DriftPass'); %s= 304.52 + 0.0
D_471_qm1g4c11b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(304.608)
qm1g4c11b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 304.608 + 0.25
D_472_cm1g4c11b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(304.967)
cm1g4c11b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 304.967 + 0.3
D_473_b1g5c11b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(305.833)
b1g5c11b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 305.833 + 2.62
D_474_ch2g6c11b = drift('DRIFT', 0.217, 'DriftPass'); % +0.217= sb(308.67)
ch2g6c11b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 308.67 + 0.3
D_475_sh4g6c11b = drift('DRIFT', 0.063, 'DriftPass'); % +0.063= sb(309.033)
sh4g6c11b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 309.033 + 0.2
D_476_ph2g6c11b = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(309.323)
ph2g6c11b = drift('BPM', 0.0, 'DriftPass'); %s= 309.323 + 0.0
D_477_qh3g6c11b = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(309.396)
qh3g6c11b = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 309.396 + 0.275
D_478_sh3g6c11b = drift('DRIFT', 0.182, 'DriftPass'); % +0.182= sb(309.853)
sh3g6c11b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 309.853 + 0.2
D_479_qh2g6c11b = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(310.243)
qh2g6c11b = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 310.243 + 0.448
D_480_ch1g6c11b = drift('DRIFT', 0.485, 'DriftPass'); % +0.485= sb(311.176)
ch1g6c11b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 311.176 + 0.2
D_481_qh1g6c11b = drift('DRIFT', 0.12, 'DriftPass'); % +0.12= sb(311.496)
qh1g6c11b = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 311.496 + 0.275
D_482_ph1g6c11b = drift('DRIFT', 0.077, 'DriftPass'); % +0.077= sb(311.848)
ph1g6c11b = drift('BPM', 0.0, 'DriftPass'); %s= 311.848 + 0.0
D_483_sh1g6c11b = drift('DRIFT', 0.085, 'DriftPass'); % +0.085= sb(311.933)
sh1g6c11b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 311.933 + 0.2
D_484_fh1g1c12a = drift('DRIFT', 0.441, 'DriftPass'); % +0.441= sb(312.574)
fh1g1c12a = drift('FCOR', 0.044, 'DriftPass'); %s= 312.574 + 0.044
D_485_fh2g1c12a = drift('DRIFT', 8.459, 'DriftPass'); % +8.459= sb(321.077)
fh2g1c12a = drift('FCOR', 0.044, 'DriftPass'); %s= 321.077 + 0.044
D_486_sh1g2c12a = drift('DRIFT', 0.312, 'DriftPass'); % +0.312= sb(321.433)
sh1g2c12a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 321.433 + 0.2
D_487_ph1g2c12a = drift('DRIFT', 0.085, 'DriftPass'); % +0.085= sb(321.718)
ph1g2c12a = drift('BPM', 0.0, 'DriftPass'); %s= 321.718 + 0.0
D_488_qh1g2c12a = drift('DRIFT', 0.078, 'DriftPass'); % +0.078= sb(321.796)
qh1g2c12a = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 321.796 + 0.275
D_489_ch1g2c12a = drift('DRIFT', 0.245, 'DriftPass'); % +0.245= sb(322.316)
ch1g2c12a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 322.316 + 0.0
sqhhg2c12a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 322.316 + 0.1
D_491_qh2g2c12a = drift('DRIFT', 0.459, 'DriftPass'); % +0.459= sb(322.875)
qh2g2c12a = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 322.875 + 0.448
D_492_sh3g2c12a = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(323.513)
sh3g2c12a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 323.513 + 0.2
D_493_qh3g2c12a = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(323.896)
qh3g2c12a = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 323.896 + 0.275
D_494_ph2g2c12a = drift('DRIFT', 0.072, 'DriftPass'); % +0.072= sb(324.243)
ph2g2c12a = drift('BPM', 0.0, 'DriftPass'); %s= 324.243 + 0.0
D_495_sh4g2c12a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(324.333)
sh4g2c12a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 324.333 + 0.2
D_496_ch2g2c12a = drift('DRIFT', 0.249, 'DriftPass'); % +0.249= sb(324.782)
ch2g2c12a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 324.782 + 0.3
D_497_b1g3c12a = drift('DRIFT', 0.031, 'DriftPass'); % +0.031= sb(325.113)
b1g3c12a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 325.113 + 2.62
D_498_cm1g4c12a = drift('DRIFT', 0.501, 'DriftPass'); % +0.501= sb(328.234)
cm1g4c12a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 328.234 + 0.2
D_499_qm1g4c12a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(328.708)
qm1g4c12a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 328.708 + 0.25
D_500_sm1g4c12a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(329.158)
sm1g4c12a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 329.158 + 0.2
D_501_fm1g4c12a = drift('DRIFT', 0.233, 'DriftPass'); % +0.233= sb(329.591)
fm1g4c12a = drift('FCOR', 0.044, 'DriftPass'); %s= 329.591 + 0.044
D_502_pm1g4c12a = drift('DRIFT', 0.293, 'DriftPass'); % +0.293= sb(329.928)
pm1g4c12a = drift('BPM', 0.0, 'DriftPass'); %s= 329.928 + 0.0
D_503_qm2g4c12a = drift('DRIFT', 0.084, 'DriftPass'); % +0.084= sb(330.012)
qm2g4c12a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 330.012 + 0.283
D_504_sm2g4c12b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(330.478)
sm2g4c12b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 330.478 + 0.25
D_505_qm2g4c12b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(330.912)
qm2g4c12b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 330.912 + 0.283
D_506_sm1g4c12b = drift('DRIFT', 0.503, 'DriftPass'); % +0.503= sb(331.698)
sm1g4c12b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 331.698 + 0.2
D_507_pm1g4c12b = drift('DRIFT', 0.262, 'DriftPass'); % +0.262= sb(332.16)
pm1g4c12b = drift('BPM', 0.0, 'DriftPass'); %s= 332.16 + 0.0
D_508_qm1g4c12b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(332.248)
qm1g4c12b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 332.248 + 0.25
D_509_cm1g4c12b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(332.607)
cm1g4c12b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 332.607 + 0.3
D_510_b1g5c12b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(333.473)
b1g5c12b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 333.473 + 2.62
D_511_ql3g6c12b = drift('DRIFT', 0.588, 'DriftPass'); % +0.588= sb(336.681)
ql3g6c12b = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 336.681 + 0.275
D_512_pl2g6c12b = drift('DRIFT', 0.074, 'DriftPass'); % +0.074= sb(337.03)
pl2g6c12b = drift('BPM', 0.0, 'DriftPass'); %s= 337.03 + 0.0
D_513_sl3g6c12b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(337.118)
sl3g6c12b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 337.118 + 0.2
D_514_cl2g6c12b = drift('DRIFT', 0.158, 'DriftPass'); % +0.158= sb(337.476)
cl2g6c12b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 337.476 + 0.2
D_515_ql2g6c12b = drift('DRIFT', 0.208, 'DriftPass'); % +0.208= sb(337.884)
ql2g6c12b = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 337.884 + 0.448
D_516_sl2g6c12b = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(338.582)
sl2g6c12b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 338.582 + 0.2
D_517_cl1g6c12b = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(338.913)
cl1g6c12b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 338.913 + 0.2
D_518_ql1g6c12b = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(339.244)
ql1g6c12b = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 339.244 + 0.275
D_519_pl1g6c12b = drift('DRIFT', 0.075, 'DriftPass'); % +0.075= sb(339.594)
pl1g6c12b = drift('BPM', 0.0, 'DriftPass'); %s= 339.594 + 0.0
D_520_sl1g6c12b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(339.682)
sl1g6c12b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 339.682 + 0.2
D_521_fl1g1c13a = drift('DRIFT', 0.446, 'DriftPass'); % +0.446= sb(340.328)
fl1g1c13a = drift('FCOR', 0.044, 'DriftPass'); %s= 340.328 + 0.044
D_522_fl2g1c13a = drift('DRIFT', 5.753, 'DriftPass'); % +5.753= sb(346.125)
fl2g1c13a = drift('FCOR', 0.044, 'DriftPass'); %s= 346.125 + 0.044
D_523_sl1g2c13a = drift('DRIFT', 0.313, 'DriftPass'); % +0.313= sb(346.482)
sl1g2c13a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 346.482 + 0.2
D_524_pl1g2c13a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(346.772)
pl1g2c13a = drift('BPM', 0.0, 'DriftPass'); %s= 346.772 + 0.0
D_525_ql1g2c13a = drift('DRIFT', 0.0720000000001, 'DriftPass'); % +0.0720000000001= sb(346.844)
ql1g2c13a = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 346.844 + 0.275
D_526_cl1g2c13a = drift('DRIFT', 0.132, 'DriftPass'); % +0.132= sb(347.251)
cl1g2c13a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 347.251 + 0.2
D_527_sl2g2c13a = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(347.582)
sl2g2c13a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 347.582 + 0.2
D_528_ql2g2c13a = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(348.032)
ql2g2c13a = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 348.032 + 0.448
D_529_cl2g2c13a = drift('DRIFT', 0.208, 'DriftPass'); % +0.208= sb(348.688)
cl2g2c13a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 348.688 + 0.2
D_530_sl3g2c13a = drift('DRIFT', 0.157, 'DriftPass'); % +0.157= sb(349.045)
sl3g2c13a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 349.045 + 0.2
D_531_pl2g2c13a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(349.335)
pl2g2c13a = drift('BPM', 0.0, 'DriftPass'); %s= 349.335 + 0.0
D_532_ql3g2c13a = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(349.408)
ql3g2c13a = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 349.408 + 0.275
D_533_b2g3c13a = drift('DRIFT', 0.587, 'DriftPass'); % +0.587= sb(350.27)
b2g3c13a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 350.27 + 2.62
D_534_cm1g4c13a = drift('DRIFT', 0.601, 'DriftPass'); % +0.601= sb(353.491)
cm1g4c13a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 353.491 + 0.0
sqmhg4c13a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 353.491 + 0.1
D_536_qm1g4c13a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(353.865)
qm1g4c13a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 353.865 + 0.25
D_537_sm1g4c13a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(354.315)
sm1g4c13a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 354.315 + 0.2
D_538_fm1g4c13a = drift('DRIFT', 0.234, 'DriftPass'); % +0.234= sb(354.749)
fm1g4c13a = drift('FCOR', 0.044, 'DriftPass'); %s= 354.749 + 0.044
D_539_pm1g4c13a = drift('DRIFT', 0.292, 'DriftPass'); % +0.292= sb(355.085)
pm1g4c13a = drift('BPM', 0.0, 'DriftPass'); %s= 355.085 + 0.0
D_540_qm2g4c13a = drift('DRIFT', 0.084, 'DriftPass'); % +0.084= sb(355.169)
qm2g4c13a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 355.169 + 0.283
D_541_sm2g4c13b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(355.635)
sm2g4c13b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 355.635 + 0.25
D_542_qm2g4c13b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(356.069)
qm2g4c13b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 356.069 + 0.283
D_543_sm1g4c13b = drift('DRIFT', 0.503, 'DriftPass'); % +0.503= sb(356.855)
sm1g4c13b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 356.855 + 0.2
D_544_pm1g4c13b = drift('DRIFT', 0.263, 'DriftPass'); % +0.263= sb(357.318)
pm1g4c13b = drift('BPM', 0.0, 'DriftPass'); %s= 357.318 + 0.0
D_545_qm1g4c13b = drift('DRIFT', 0.087, 'DriftPass'); % +0.087= sb(357.405)
qm1g4c13b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 357.405 + 0.25
D_546_cm1g4c13b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(357.764)
cm1g4c13b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 357.764 + 0.3
D_547_b2g5c13b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(358.63)
b2g5c13b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 358.63 + 2.62
D_548_ch2g6c13b = drift('DRIFT', 0.217, 'DriftPass'); % +0.217= sb(361.467)
ch2g6c13b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 361.467 + 0.3
D_549_sh4g6c13b = drift('DRIFT', 0.063, 'DriftPass'); % +0.063= sb(361.83)
sh4g6c13b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 361.83 + 0.2
D_550_ph2g6c13b = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(362.12)
ph2g6c13b = drift('BPM', 0.0, 'DriftPass'); %s= 362.12 + 0.0
D_551_qh3g6c13b = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(362.193)
qh3g6c13b = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 362.193 + 0.275
D_552_sh3g6c13b = drift('DRIFT', 0.182, 'DriftPass'); % +0.182= sb(362.65)
sh3g6c13b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 362.65 + 0.2
D_553_qh2g6c13b = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(363.04)
qh2g6c13b = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 363.04 + 0.448
D_554_ch1g6c13b = drift('DRIFT', 0.485, 'DriftPass'); % +0.485= sb(363.973)
ch1g6c13b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 363.973 + 0.2
D_555_qh1g6c13b = drift('DRIFT', 0.12, 'DriftPass'); % +0.12= sb(364.293)
qh1g6c13b = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 364.293 + 0.275
D_556_ph1g6c13b = drift('DRIFT', 0.077, 'DriftPass'); % +0.077= sb(364.645)
ph1g6c13b = drift('BPM', 0.0, 'DriftPass'); %s= 364.645 + 0.0
D_557_sh1g6c13b = drift('DRIFT', 0.085, 'DriftPass'); % +0.085= sb(364.73)
sh1g6c13b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 364.73 + 0.2
D_558_fh1g1c14a = drift('DRIFT', 0.441, 'DriftPass'); % +0.441= sb(365.371)
fh1g1c14a = drift('FCOR', 0.044, 'DriftPass'); %s= 365.371 + 0.044
D_559_fh2g1c14a = drift('DRIFT', 8.459, 'DriftPass'); % +8.459= sb(373.874)
fh2g1c14a = drift('FCOR', 0.044, 'DriftPass'); %s= 373.874 + 0.044
D_560_sh1g2c14a = drift('DRIFT', 0.312, 'DriftPass'); % +0.312= sb(374.23)
sh1g2c14a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 374.23 + 0.2
D_561_ph1g2c14a = drift('DRIFT', 0.085, 'DriftPass'); % +0.085= sb(374.515)
ph1g2c14a = drift('BPM', 0.0, 'DriftPass'); %s= 374.515 + 0.0
D_562_qh1g2c14a = drift('DRIFT', 0.078, 'DriftPass'); % +0.078= sb(374.593)
qh1g2c14a = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 374.593 + 0.275
D_563_ch1g2c14a = drift('DRIFT', 0.245, 'DriftPass'); % +0.245= sb(375.113)
ch1g2c14a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 375.113 + 0.0
sqhhg2c14a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 375.113 + 0.1
D_565_qh2g2c14a = drift('DRIFT', 0.459, 'DriftPass'); % +0.459= sb(375.672)
qh2g2c14a = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 375.672 + 0.448
D_566_sh3g2c14a = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(376.31)
sh3g2c14a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 376.31 + 0.2
D_567_qh3g2c14a = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(376.693)
qh3g2c14a = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 376.693 + 0.275
D_568_ph2g2c14a = drift('DRIFT', 0.072, 'DriftPass'); % +0.072= sb(377.04)
ph2g2c14a = drift('BPM', 0.0, 'DriftPass'); %s= 377.04 + 0.0
D_569_sh4g2c14a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(377.13)
sh4g2c14a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 377.13 + 0.2
D_570_ch2g2c14a = drift('DRIFT', 0.249, 'DriftPass'); % +0.249= sb(377.579)
ch2g2c14a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 377.579 + 0.3
D_571_b1g3c14a = drift('DRIFT', 0.0309999999999, 'DriftPass'); % +0.0309999999999= sb(377.91)
b1g3c14a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 377.91 + 2.62
D_572_cm1g4c14a = drift('DRIFT', 0.501, 'DriftPass'); % +0.501= sb(381.031)
cm1g4c14a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 381.031 + 0.2
D_573_qm1g4c14a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(381.505)
qm1g4c14a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 381.505 + 0.25
D_574_sm1g4c14a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(381.955)
sm1g4c14a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 381.955 + 0.2
D_575_fm1g4c14a = drift('DRIFT', 0.234, 'DriftPass'); % +0.234= sb(382.389)
fm1g4c14a = drift('FCOR', 0.044, 'DriftPass'); %s= 382.389 + 0.044
D_576_pm1g4c14a = drift('DRIFT', 0.292, 'DriftPass'); % +0.292= sb(382.725)
pm1g4c14a = drift('BPM', 0.0, 'DriftPass'); %s= 382.725 + 0.0
D_577_qm2g4c14a = drift('DRIFT', 0.0839999999999, 'DriftPass'); % +0.0839999999999= sb(382.809)
qm2g4c14a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 382.809 + 0.283
D_578_sm2g4c14b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(383.275)
sm2g4c14b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 383.275 + 0.25
D_579_qm2g4c14b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(383.709)
qm2g4c14b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 383.709 + 0.283
D_580_sm1g4c14b = drift('DRIFT', 0.503, 'DriftPass'); % +0.503= sb(384.495)
sm1g4c14b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 384.495 + 0.2
D_581_pm1g4c14b = drift('DRIFT', 0.263, 'DriftPass'); % +0.263= sb(384.958)
pm1g4c14b = drift('BPM', 0.0, 'DriftPass'); %s= 384.958 + 0.0
D_582_qm1g4c14b = drift('DRIFT', 0.087, 'DriftPass'); % +0.087= sb(385.045)
qm1g4c14b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 385.045 + 0.25
D_583_cm1g4c14b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(385.404)
cm1g4c14b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 385.404 + 0.3
D_584_b1g5c14b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(386.27)
b1g5c14b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 386.27 + 2.62
D_585_ql3g6c14b = drift('DRIFT', 0.588, 'DriftPass'); % +0.588= sb(389.478)
ql3g6c14b = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 389.478 + 0.275
D_586_pl2g6c14b = drift('DRIFT', 0.075, 'DriftPass'); % +0.075= sb(389.828)
pl2g6c14b = drift('BPM', 0.0, 'DriftPass'); %s= 389.828 + 0.0
D_587_sl3g6c14b = drift('DRIFT', 0.087, 'DriftPass'); % +0.087= sb(389.915)
sl3g6c14b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 389.915 + 0.2
D_588_cl2g6c14b = drift('DRIFT', 0.158, 'DriftPass'); % +0.158= sb(390.273)
cl2g6c14b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 390.273 + 0.2
D_589_ql2g6c14b = drift('DRIFT', 0.208, 'DriftPass'); % +0.208= sb(390.681)
ql2g6c14b = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 390.681 + 0.448
D_590_sl2g6c14b = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(391.379)
sl2g6c14b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 391.379 + 0.2
D_591_cl1g6c14b = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(391.71)
cl1g6c14b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 391.71 + 0.2
D_592_ql1g6c14b = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(392.041)
ql1g6c14b = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 392.041 + 0.275
D_593_pl1g6c14b = drift('DRIFT', 0.075, 'DriftPass'); % +0.075= sb(392.391)
pl1g6c14b = drift('BPM', 0.0, 'DriftPass'); %s= 392.391 + 0.0
D_594_sl1g6c14b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(392.479)
sl1g6c14b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 392.479 + 0.2
D_595_fl1g1c15a = drift('DRIFT', 0.447, 'DriftPass'); % +0.447= sb(393.126)
fl1g1c15a = drift('FCOR', 0.044, 'DriftPass'); %s= 393.126 + 0.044
D_596_fl2g1c15a = drift('DRIFT', 5.753, 'DriftPass'); % +5.753= sb(398.923)
fl2g1c15a = drift('FCOR', 0.044, 'DriftPass'); %s= 398.923 + 0.044
D_597_sl1g2c15a = drift('DRIFT', 0.312, 'DriftPass'); % +0.312= sb(399.279)
sl1g2c15a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 399.279 + 0.2
D_598_pl1g2c15a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(399.569)
pl1g2c15a = drift('BPM', 0.0, 'DriftPass'); %s= 399.569 + 0.0
D_599_ql1g2c15a = drift('DRIFT', 0.072, 'DriftPass'); % +0.072= sb(399.641)
ql1g2c15a = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 399.641 + 0.275
D_600_cl1g2c15a = drift('DRIFT', 0.132, 'DriftPass'); % +0.132= sb(400.048)
cl1g2c15a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 400.048 + 0.2
D_601_sl2g2c15a = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(400.379)
sl2g2c15a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 400.379 + 0.2
D_602_ql2g2c15a = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(400.829)
ql2g2c15a = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 400.829 + 0.448
D_603_cl2g2c15a = drift('DRIFT', 0.208, 'DriftPass'); % +0.208= sb(401.485)
cl2g2c15a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 401.485 + 0.2
D_604_sl3g2c15a = drift('DRIFT', 0.158, 'DriftPass'); % +0.158= sb(401.843)
sl3g2c15a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 401.843 + 0.2
D_605_pl2g2c15a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(402.133)
pl2g2c15a = drift('BPM', 0.0, 'DriftPass'); %s= 402.133 + 0.0
D_606_ql3g2c15a = drift('DRIFT', 0.0720000000001, 'DriftPass'); % +0.0720000000001= sb(402.205)
ql3g2c15a = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 402.205 + 0.275
D_607_b1g3c15a = drift('DRIFT', 0.588, 'DriftPass'); % +0.588= sb(403.068)
b1g3c15a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 403.068 + 2.62
D_608_cm1g4c15a = drift('DRIFT', 0.601, 'DriftPass'); % +0.601= sb(406.289)
cm1g4c15a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 406.289 + 0.0
sqmhg4c15a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 406.289 + 0.1
D_610_qm1g4c15a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(406.663)
qm1g4c15a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 406.663 + 0.25
D_611_sm1g4c15a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(407.113)
sm1g4c15a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 407.113 + 0.2
D_612_fm1g4c15a = drift('DRIFT', 0.233, 'DriftPass'); % +0.233= sb(407.546)
fm1g4c15a = drift('FCOR', 0.044, 'DriftPass'); %s= 407.546 + 0.044
D_613_pm1g4c15a = drift('DRIFT', 0.292, 'DriftPass'); % +0.292= sb(407.882)
pm1g4c15a = drift('BPM', 0.0, 'DriftPass'); %s= 407.882 + 0.0
D_614_qm2g4c15a = drift('DRIFT', 0.084, 'DriftPass'); % +0.084= sb(407.966)
qm2g4c15a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 407.966 + 0.283
D_615_sm2g4c15b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(408.433)
sm2g4c15b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 408.433 + 0.25
D_616_qm2g4c15b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(408.866)
qm2g4c15b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 408.866 + 0.283
D_617_sm1g4c15b = drift('DRIFT', 0.504, 'DriftPass'); % +0.504= sb(409.653)
sm1g4c15b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 409.653 + 0.2
D_618_pm1g4c15b = drift('DRIFT', 0.262, 'DriftPass'); % +0.262= sb(410.115)
pm1g4c15b = drift('BPM', 0.0, 'DriftPass'); %s= 410.115 + 0.0
D_619_qm1g4c15b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(410.203)
qm1g4c15b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 410.203 + 0.25
D_620_cm1g4c15b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(410.562)
cm1g4c15b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 410.562 + 0.3
D_621_b1g5c15b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(411.428)
b1g5c15b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 411.428 + 2.62
D_622_ch2g6c15b = drift('DRIFT', 0.216, 'DriftPass'); % +0.216= sb(414.264)
ch2g6c15b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 414.264 + 0.3
D_623_sh4g6c15b = drift('DRIFT', 0.064, 'DriftPass'); % +0.064= sb(414.628)
sh4g6c15b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 414.628 + 0.2
D_624_ph2g6c15b = drift('DRIFT', 0.089, 'DriftPass'); % +0.089= sb(414.917)
ph2g6c15b = drift('BPM', 0.0, 'DriftPass'); %s= 414.917 + 0.0
D_625_qh3g6c15b = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(414.99)
qh3g6c15b = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 414.99 + 0.275
D_626_sh3g6c15b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(415.448)
sh3g6c15b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 415.448 + 0.2
D_627_qh2g6c15b = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(415.838)
qh2g6c15b = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 415.838 + 0.448
D_628_ch1g6c15b = drift('DRIFT', 0.484, 'DriftPass'); % +0.484= sb(416.77)
ch1g6c15b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 416.77 + 0.2
D_629_qh1g6c15b = drift('DRIFT', 0.12, 'DriftPass'); % +0.12= sb(417.09)
qh1g6c15b = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 417.09 + 0.275
D_630_ph1g6c15b = drift('DRIFT', 0.077, 'DriftPass'); % +0.077= sb(417.442)
ph1g6c15b = drift('BPM', 0.0, 'DriftPass'); %s= 417.442 + 0.0
D_631_sh1g6c15b = drift('DRIFT', 0.086, 'DriftPass'); % +0.086= sb(417.528)
sh1g6c15b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 417.528 + 0.2
D_632_fh1g1c16a = drift('DRIFT', 0.44, 'DriftPass'); % +0.44= sb(418.168)
fh1g1c16a = drift('FCOR', 0.044, 'DriftPass'); %s= 418.168 + 0.044
D_633_fh2g1c16a = drift('DRIFT', 8.459, 'DriftPass'); % +8.459= sb(426.671)
fh2g1c16a = drift('FCOR', 0.044, 'DriftPass'); %s= 426.671 + 0.044
D_634_sh1g2c16a = drift('DRIFT', 0.313, 'DriftPass'); % +0.313= sb(427.028)
sh1g2c16a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 427.028 + 0.2
D_635_ph1g2c16a = drift('DRIFT', 0.085, 'DriftPass'); % +0.085= sb(427.313)
ph1g2c16a = drift('BPM', 0.0, 'DriftPass'); %s= 427.313 + 0.0
D_636_qh1g2c16a = drift('DRIFT', 0.0770000000001, 'DriftPass'); % +0.0770000000001= sb(427.39)
qh1g2c16a = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 427.39 + 0.275
D_637_ch1g2c16a = drift('DRIFT', 0.245, 'DriftPass'); % +0.245= sb(427.91)
ch1g2c16a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 427.91 + 0.0
sqhhg2c16a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 427.91 + 0.1
D_639_qh2g2c16a = drift('DRIFT', 0.46, 'DriftPass'); % +0.46= sb(428.47)
qh2g2c16a = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 428.47 + 0.448
D_640_sh3g2c16a = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(429.108)
sh3g2c16a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 429.108 + 0.2
D_641_qh3g2c16a = drift('DRIFT', 0.182, 'DriftPass'); % +0.182= sb(429.49)
qh3g2c16a = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 429.49 + 0.275
D_642_ph2g2c16a = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(429.838)
ph2g2c16a = drift('BPM', 0.0, 'DriftPass'); %s= 429.838 + 0.0
D_643_sh4g2c16a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(429.928)
sh4g2c16a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 429.928 + 0.2
D_644_ch2g2c16a = drift('DRIFT', 0.248, 'DriftPass'); % +0.248= sb(430.376)
ch2g2c16a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 430.376 + 0.3
D_645_b1g3c16a = drift('DRIFT', 0.032, 'DriftPass'); % +0.032= sb(430.708)
b1g3c16a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 430.708 + 2.62
D_646_cm1g4c16a = drift('DRIFT', 0.501, 'DriftPass'); % +0.501= sb(433.829)
cm1g4c16a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 433.829 + 0.2
D_647_qm1g4c16a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(434.303)
qm1g4c16a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 434.303 + 0.25
D_648_sm1g4c16a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(434.753)
sm1g4c16a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 434.753 + 0.2
D_649_fm1g4c16a = drift('DRIFT', 0.233, 'DriftPass'); % +0.233= sb(435.186)
fm1g4c16a = drift('FCOR', 0.044, 'DriftPass'); %s= 435.186 + 0.044
D_650_pm1g4c16a = drift('DRIFT', 0.292, 'DriftPass'); % +0.292= sb(435.522)
pm1g4c16a = drift('BPM', 0.0, 'DriftPass'); %s= 435.522 + 0.0
D_651_qm2g4c16a = drift('DRIFT', 0.084, 'DriftPass'); % +0.084= sb(435.606)
qm2g4c16a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 435.606 + 0.283
D_652_sm2g4c16b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(436.073)
sm2g4c16b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 436.073 + 0.25
D_653_qm2g4c16b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(436.506)
qm2g4c16b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 436.506 + 0.283
D_654_sm1g4c16b = drift('DRIFT', 0.504, 'DriftPass'); % +0.504= sb(437.293)
sm1g4c16b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 437.293 + 0.2
D_655_pm1g4c16b = drift('DRIFT', 0.262, 'DriftPass'); % +0.262= sb(437.755)
pm1g4c16b = drift('BPM', 0.0, 'DriftPass'); %s= 437.755 + 0.0
D_656_qm1g4c16b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(437.843)
qm1g4c16b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 437.843 + 0.25
D_657_cm1g4c16b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(438.202)
cm1g4c16b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 438.202 + 0.3
D_658_b1g5c16b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(439.068)
b1g5c16b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 439.068 + 2.62
D_659_ql3g6c16b = drift('DRIFT', 0.587, 'DriftPass'); % +0.587= sb(442.275)
ql3g6c16b = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 442.275 + 0.275
D_660_pl2g6c16b = drift('DRIFT', 0.075, 'DriftPass'); % +0.075= sb(442.625)
pl2g6c16b = drift('BPM', 0.0, 'DriftPass'); %s= 442.625 + 0.0
D_661_sl3g6c16b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(442.713)
sl3g6c16b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 442.713 + 0.2
D_662_cl2g6c16b = drift('DRIFT', 0.157, 'DriftPass'); % +0.157= sb(443.07)
cl2g6c16b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 443.07 + 0.2
D_663_ql2g6c16b = drift('DRIFT', 0.208, 'DriftPass'); % +0.208= sb(443.478)
ql2g6c16b = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 443.478 + 0.448
D_664_sl2g6c16b = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(444.176)
sl2g6c16b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 444.176 + 0.2
D_665_cl1g6c16b = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(444.507)
cl1g6c16b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 444.507 + 0.2
D_666_ql1g6c16b = drift('DRIFT', 0.132, 'DriftPass'); % +0.132= sb(444.839)
ql1g6c16b = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 444.839 + 0.275
D_667_pl1g6c16b = drift('DRIFT', 0.074, 'DriftPass'); % +0.074= sb(445.188)
pl1g6c16b = drift('BPM', 0.0, 'DriftPass'); %s= 445.188 + 0.0
D_668_sl1g6c16b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(445.276)
sl1g6c16b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 445.276 + 0.2
D_669_fl1g1c17a = drift('DRIFT', 0.447, 'DriftPass'); % +0.447= sb(445.923)
fl1g1c17a = drift('FCOR', 0.044, 'DriftPass'); %s= 445.923 + 0.044
D_670_fl2g1c17a = drift('DRIFT', 5.753, 'DriftPass'); % +5.753= sb(451.72)
fl2g1c17a = drift('FCOR', 0.044, 'DriftPass'); %s= 451.72 + 0.044
D_671_sl1g2c17a = drift('DRIFT', 0.312, 'DriftPass'); % +0.312= sb(452.076)
sl1g2c17a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 452.076 + 0.2
D_672_pl1g2c17a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(452.366)
pl1g2c17a = drift('BPM', 0.0, 'DriftPass'); %s= 452.366 + 0.0
D_673_ql1g2c17a = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(452.439)
ql1g2c17a = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 452.439 + 0.275
D_674_cl1g2c17a = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(452.845)
cl1g2c17a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 452.845 + 0.2
D_675_sl2g2c17a = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(453.176)
sl2g2c17a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 453.176 + 0.2
D_676_ql2g2c17a = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(453.626)
ql2g2c17a = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 453.626 + 0.448
D_677_cl2g2c17a = drift('DRIFT', 0.208, 'DriftPass'); % +0.208= sb(454.282)
cl2g2c17a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 454.282 + 0.2
D_678_sl3g2c17a = drift('DRIFT', 0.158, 'DriftPass'); % +0.158= sb(454.64)
sl3g2c17a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 454.64 + 0.2
D_679_pl2g2c17a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(454.93)
pl2g2c17a = drift('BPM', 0.0, 'DriftPass'); %s= 454.93 + 0.0
D_680_ql3g2c17a = drift('DRIFT', 0.072, 'DriftPass'); % +0.072= sb(455.002)
ql3g2c17a = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 455.002 + 0.275
D_681_b1g3c17a = drift('DRIFT', 0.588, 'DriftPass'); % +0.588= sb(455.865)
b1g3c17a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 455.865 + 2.62
D_682_cm1g4c17a = drift('DRIFT', 0.601, 'DriftPass'); % +0.601= sb(459.086)
cm1g4c17a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 459.086 + 0.0
sqmhg4c17a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 459.086 + 0.1
D_684_qm1g4c17a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(459.46)
qm1g4c17a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 459.46 + 0.25
D_685_sm1g4c17a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(459.91)
sm1g4c17a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 459.91 + 0.2
D_686_fm1g4c17a = drift('DRIFT', 0.233, 'DriftPass'); % +0.233= sb(460.343)
fm1g4c17a = drift('FCOR', 0.044, 'DriftPass'); %s= 460.343 + 0.044
D_687_pm1g4c17a = drift('DRIFT', 0.292, 'DriftPass'); % +0.292= sb(460.679)
pm1g4c17a = drift('BPM', 0.0, 'DriftPass'); %s= 460.679 + 0.0
D_688_qm2g4c17a = drift('DRIFT', 0.084, 'DriftPass'); % +0.084= sb(460.763)
qm2g4c17a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 460.763 + 0.283
D_689_sm2g4c17b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(461.23)
sm2g4c17b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 461.23 + 0.25
D_690_qm2g4c17b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(461.663)
qm2g4c17b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 461.663 + 0.283
D_691_sm1g4c17b = drift('DRIFT', 0.504, 'DriftPass'); % +0.504= sb(462.45)
sm1g4c17b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 462.45 + 0.2
D_692_pm1g4c17b = drift('DRIFT', 0.262, 'DriftPass'); % +0.262= sb(462.912)
pm1g4c17b = drift('BPM', 0.0, 'DriftPass'); %s= 462.912 + 0.0
D_693_qm1g4c17b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(463.0)
qm1g4c17b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 463.0 + 0.25
D_694_cm1g4c17b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(463.359)
cm1g4c17b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 463.359 + 0.3
D_695_b1g5c17b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(464.225)
b1g5c17b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 464.225 + 2.62
D_696_ch2g6c17b = drift('DRIFT', 0.216, 'DriftPass'); % +0.216= sb(467.061)
ch2g6c17b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 467.061 + 0.3
D_697_sh4g6c17b = drift('DRIFT', 0.064, 'DriftPass'); % +0.064= sb(467.425)
sh4g6c17b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 467.425 + 0.2
D_698_ph2g6c17b = drift('DRIFT', 0.089, 'DriftPass'); % +0.089= sb(467.714)
ph2g6c17b = drift('BPM', 0.0, 'DriftPass'); %s= 467.714 + 0.0
D_699_qh3g6c17b = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(467.787)
qh3g6c17b = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 467.787 + 0.275
D_700_sh3g6c17b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(468.245)
sh3g6c17b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 468.245 + 0.2
D_701_qh2g6c17b = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(468.635)
qh2g6c17b = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 468.635 + 0.448
D_702_ch1g6c17b = drift('DRIFT', 0.484, 'DriftPass'); % +0.484= sb(469.567)
ch1g6c17b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 469.567 + 0.2
D_703_qh1g6c17b = drift('DRIFT', 0.12, 'DriftPass'); % +0.12= sb(469.887)
qh1g6c17b = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 469.887 + 0.275
D_704_ph1g6c17b = drift('DRIFT', 0.077, 'DriftPass'); % +0.077= sb(470.239)
ph1g6c17b = drift('BPM', 0.0, 'DriftPass'); %s= 470.239 + 0.0
D_705_sh1g6c17b = drift('DRIFT', 0.086, 'DriftPass'); % +0.086= sb(470.325)
sh1g6c17b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 470.325 + 0.2
D_706_fh1g1c18a = drift('DRIFT', 0.441, 'DriftPass'); % +0.441= sb(470.966)
fh1g1c18a = drift('FCOR', 0.044, 'DriftPass'); %s= 470.966 + 0.044
D_707_pu1g1c18a = drift('DRIFT', 0.503, 'DriftPass'); % +0.503= sb(471.513)
pu1g1c18a = drift('UBPM', 0.0, 'DriftPass'); %s= 471.513 + 0.0
D_708_cu1g1c18id1 = drift('DRIFT', 0.071, 'DriftPass'); % +0.071= sb(471.584)
cu1g1c18id1 = drift('IDCOR', 0.0, 'DriftPass'); %s= 471.584 + 0.0
cs1g1c18id1 = drift('IDSIMCOR', 0.0, 'DriftPass'); %s= 471.584 + 0.0
dw100g1c18u = drift('INSERTION', 3.4, 'DriftPass'); %s= 471.584 + 3.4
cu2g1c18id1 = drift('IDCOR', 0.0, 'DriftPass'); %s= 474.984 + 0.0
cs2g1c18id1 = drift('IDSIMCOR', 0.0, 'DriftPass'); %s= 474.984 + 0.0
D_713_cu1g1c18id2 = drift('DRIFT', 0.381, 'DriftPass'); % +0.381= sb(475.365)
cu1g1c18id2 = drift('IDCOR', 0.0, 'DriftPass'); %s= 475.365 + 0.0
cs1g1c18id2 = drift('IDSIMCOR', 0.0, 'DriftPass'); %s= 475.365 + 0.0
dw100g1c18d = drift('INSERTION', 3.4, 'DriftPass'); %s= 475.365 + 3.4
cu2g1c18id2 = drift('IDCOR', 0.0, 'DriftPass'); %s= 478.765 + 0.0
cs2g1c18id2 = drift('IDSIMCOR', 0.0, 'DriftPass'); %s= 478.765 + 0.0
D_718_pu4g1c18a = drift('DRIFT', 0.087, 'DriftPass'); % +0.087= sb(478.852)
pu4g1c18a = drift('UBPM', 0.0, 'DriftPass'); %s= 478.852 + 0.0
D_719_fh2g1c18a = drift('DRIFT', 0.617, 'DriftPass'); % +0.617= sb(479.469)
fh2g1c18a = drift('FCOR', 0.044, 'DriftPass'); %s= 479.469 + 0.044
D_720_sh1g2c18a = drift('DRIFT', 0.312, 'DriftPass'); % +0.312= sb(479.825)
sh1g2c18a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 479.825 + 0.2
D_721_ph1g2c18a = drift('DRIFT', 0.085, 'DriftPass'); % +0.085= sb(480.11)
ph1g2c18a = drift('BPM', 0.0, 'DriftPass'); %s= 480.11 + 0.0
D_722_qh1g2c18a = drift('DRIFT', 0.077, 'DriftPass'); % +0.077= sb(480.187)
qh1g2c18a = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 480.187 + 0.275
D_723_ch1g2c18a = drift('DRIFT', 0.245, 'DriftPass'); % +0.245= sb(480.707)
ch1g2c18a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 480.707 + 0.0
sqhhg2c18a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 480.707 + 0.1
D_725_qh2g2c18a = drift('DRIFT', 0.46, 'DriftPass'); % +0.46= sb(481.267)
qh2g2c18a = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 481.267 + 0.448
D_726_sh3g2c18a = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(481.905)
sh3g2c18a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 481.905 + 0.2
D_727_qh3g2c18a = drift('DRIFT', 0.182, 'DriftPass'); % +0.182= sb(482.287)
qh3g2c18a = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 482.287 + 0.275
D_728_ph2g2c18a = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(482.635)
ph2g2c18a = drift('BPM', 0.0, 'DriftPass'); %s= 482.635 + 0.0
D_729_sh4g2c18a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(482.725)
sh4g2c18a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 482.725 + 0.2
D_730_ch2g2c18a = drift('DRIFT', 0.248, 'DriftPass'); % +0.248= sb(483.173)
ch2g2c18a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 483.173 + 0.3
D_731_b1g3c18a = drift('DRIFT', 0.032, 'DriftPass'); % +0.032= sb(483.505)
b1g3c18a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 483.505 + 2.62
D_732_cm1g4c18a = drift('DRIFT', 0.501, 'DriftPass'); % +0.501= sb(486.626)
cm1g4c18a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 486.626 + 0.2
D_733_qm1g4c18a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(487.1)
qm1g4c18a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 487.1 + 0.25
D_734_sm1g4c18a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(487.55)
sm1g4c18a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 487.55 + 0.2
D_735_fm1g4c18a = drift('DRIFT', 0.233, 'DriftPass'); % +0.233= sb(487.983)
fm1g4c18a = drift('FCOR', 0.044, 'DriftPass'); %s= 487.983 + 0.044
D_736_pm1g4c18a = drift('DRIFT', 0.292, 'DriftPass'); % +0.292= sb(488.319)
pm1g4c18a = drift('BPM', 0.0, 'DriftPass'); %s= 488.319 + 0.0
D_737_qm2g4c18a = drift('DRIFT', 0.0839999999999, 'DriftPass'); % +0.0839999999999= sb(488.403)
qm2g4c18a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 488.403 + 0.283
D_738_sm2g4c18b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(488.87)
sm2g4c18b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 488.87 + 0.25
D_739_qm2g4c18b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(489.303)
qm2g4c18b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 489.303 + 0.283
D_740_sm1g4c18b = drift('DRIFT', 0.504, 'DriftPass'); % +0.504= sb(490.09)
sm1g4c18b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 490.09 + 0.2
D_741_pm1g4c18b = drift('DRIFT', 0.262, 'DriftPass'); % +0.262= sb(490.552)
pm1g4c18b = drift('BPM', 0.0, 'DriftPass'); %s= 490.552 + 0.0
D_742_qm1g4c18b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(490.64)
qm1g4c18b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 490.64 + 0.25
D_743_cm1g4c18b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(490.999)
cm1g4c18b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 490.999 + 0.3
D_744_b1g5c18b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(491.865)
b1g5c18b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 491.865 + 2.62
D_745_ql3g6c18b = drift('DRIFT', 0.587, 'DriftPass'); % +0.587= sb(495.072)
ql3g6c18b = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 495.072 + 0.275
D_746_pl2g6c18b = drift('DRIFT', 0.075, 'DriftPass'); % +0.075= sb(495.422)
pl2g6c18b = drift('BPM', 0.0, 'DriftPass'); %s= 495.422 + 0.0
D_747_sl3g6c18b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(495.51)
sl3g6c18b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 495.51 + 0.2
D_748_cl2g6c18b = drift('DRIFT', 0.157, 'DriftPass'); % +0.157= sb(495.867)
cl2g6c18b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 495.867 + 0.2
D_749_ql2g6c18b = drift('DRIFT', 0.208, 'DriftPass'); % +0.208= sb(496.275)
ql2g6c18b = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 496.275 + 0.448
D_750_sl2g6c18b = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(496.973)
sl2g6c18b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 496.973 + 0.2
D_751_cl1g6c18b = drift('DRIFT', 0.132, 'DriftPass'); % +0.132= sb(497.305)
cl1g6c18b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 497.305 + 0.2
D_752_ql1g6c18b = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(497.636)
ql1g6c18b = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 497.636 + 0.275
D_753_pl1g6c18b = drift('DRIFT', 0.075, 'DriftPass'); % +0.075= sb(497.986)
pl1g6c18b = drift('BPM', 0.0, 'DriftPass'); %s= 497.986 + 0.0
D_754_sl1g6c18b = drift('DRIFT', 0.087, 'DriftPass'); % +0.087= sb(498.073)
sl1g6c18b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 498.073 + 0.2
D_755_fl1g1c19a = drift('DRIFT', 0.447, 'DriftPass'); % +0.447= sb(498.72)
fl1g1c19a = drift('FCOR', 0.044, 'DriftPass'); %s= 498.72 + 0.044
D_756_fl2g1c19a = drift('DRIFT', 5.753, 'DriftPass'); % +5.753= sb(504.517)
fl2g1c19a = drift('FCOR', 0.044, 'DriftPass'); %s= 504.517 + 0.044
D_757_sl1g2c19a = drift('DRIFT', 0.312, 'DriftPass'); % +0.312= sb(504.873)
sl1g2c19a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 504.873 + 0.2
D_758_pl1g2c19a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(505.163)
pl1g2c19a = drift('BPM', 0.0, 'DriftPass'); %s= 505.163 + 0.0
D_759_ql1g2c19a = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(505.236)
ql1g2c19a = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 505.236 + 0.275
D_760_cl1g2c19a = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(505.642)
cl1g2c19a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 505.642 + 0.2
D_761_sl2g2c19a = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(505.973)
sl2g2c19a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 505.973 + 0.2
D_762_ql2g2c19a = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(506.423)
ql2g2c19a = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 506.423 + 0.448
D_763_cl2g2c19a = drift('DRIFT', 0.208, 'DriftPass'); % +0.208= sb(507.079)
cl2g2c19a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 507.079 + 0.2
D_764_sl3g2c19a = drift('DRIFT', 0.158, 'DriftPass'); % +0.158= sb(507.437)
sl3g2c19a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 507.437 + 0.2
D_765_pl2g2c19a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(507.727)
pl2g2c19a = drift('BPM', 0.0, 'DriftPass'); %s= 507.727 + 0.0
D_766_ql3g2c19a = drift('DRIFT', 0.0720000000001, 'DriftPass'); % +0.0720000000001= sb(507.799)
ql3g2c19a = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 507.799 + 0.275
D_767_b1g3c19a = drift('DRIFT', 0.588, 'DriftPass'); % +0.588= sb(508.662)
b1g3c19a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 508.662 + 2.62
D_768_cm1g4c19a = drift('DRIFT', 0.601, 'DriftPass'); % +0.601= sb(511.883)
cm1g4c19a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 511.883 + 0.0
sqmhg4c19a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 511.883 + 0.1
D_770_qm1g4c19a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(512.257)
qm1g4c19a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 512.257 + 0.25
D_771_sm1g4c19a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(512.707)
sm1g4c19a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 512.707 + 0.2
D_772_fm1g4c19a = drift('DRIFT', 0.233, 'DriftPass'); % +0.233= sb(513.14)
fm1g4c19a = drift('FCOR', 0.044, 'DriftPass'); %s= 513.14 + 0.044
D_773_pm1g4c19a = drift('DRIFT', 0.293, 'DriftPass'); % +0.293= sb(513.477)
pm1g4c19a = drift('BPM', 0.0, 'DriftPass'); %s= 513.477 + 0.0
D_774_qm2g4c19a = drift('DRIFT', 0.083, 'DriftPass'); % +0.083= sb(513.56)
qm2g4c19a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 513.56 + 0.283
D_775_sm2g4c19b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(514.027)
sm2g4c19b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 514.027 + 0.25
D_776_qm2g4c19b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(514.46)
qm2g4c19b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 514.46 + 0.283
D_777_sm1g4c19b = drift('DRIFT', 0.504, 'DriftPass'); % +0.504= sb(515.247)
sm1g4c19b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 515.247 + 0.2
D_778_pm1g4c19b = drift('DRIFT', 0.262, 'DriftPass'); % +0.262= sb(515.709)
pm1g4c19b = drift('BPM', 0.0, 'DriftPass'); %s= 515.709 + 0.0
D_779_qm1g4c19b = drift('DRIFT', 0.0880000000001, 'DriftPass'); % +0.0880000000001= sb(515.797)
qm1g4c19b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 515.797 + 0.25
D_780_cm1g4c19b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(516.156)
cm1g4c19b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 516.156 + 0.3
D_781_b1g5c19b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(517.022)
b1g5c19b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 517.022 + 2.62
D_782_ch2g6c19b = drift('DRIFT', 0.216, 'DriftPass'); % +0.216= sb(519.858)
ch2g6c19b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 519.858 + 0.3
D_783_sh4g6c19b = drift('DRIFT', 0.064, 'DriftPass'); % +0.064= sb(520.222)
sh4g6c19b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 520.222 + 0.2
D_784_ph2g6c19b = drift('DRIFT', 0.0899999999999, 'DriftPass'); % +0.0899999999999= sb(520.512)
ph2g6c19b = drift('BPM', 0.0, 'DriftPass'); %s= 520.512 + 0.0
D_785_qh3g6c19b = drift('DRIFT', 0.0720000000001, 'DriftPass'); % +0.0720000000001= sb(520.584)
qh3g6c19b = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 520.584 + 0.275
D_786_sh3g6c19b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(521.042)
sh3g6c19b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 521.042 + 0.2
D_787_qh2g6c19b = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(521.432)
qh2g6c19b = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 521.432 + 0.448
D_788_ch1g6c19b = drift('DRIFT', 0.484, 'DriftPass'); % +0.484= sb(522.364)
ch1g6c19b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 522.364 + 0.2
D_789_qh1g6c19b = drift('DRIFT', 0.12, 'DriftPass'); % +0.12= sb(522.684)
qh1g6c19b = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 522.684 + 0.275
D_790_ph1g6c19b = drift('DRIFT', 0.0780000000001, 'DriftPass'); % +0.0780000000001= sb(523.037)
ph1g6c19b = drift('BPM', 0.0, 'DriftPass'); %s= 523.037 + 0.0
D_791_sh1g6c19b = drift('DRIFT', 0.0849999999999, 'DriftPass'); % +0.0849999999999= sb(523.122)
sh1g6c19b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 523.122 + 0.2
D_792_fh1g1c20a = drift('DRIFT', 0.441, 'DriftPass'); % +0.441= sb(523.763)
fh1g1c20a = drift('FCOR', 0.044, 'DriftPass'); %s= 523.763 + 0.044
D_793_fh2g1c20a = drift('DRIFT', 8.459, 'DriftPass'); % +8.459= sb(532.266)
fh2g1c20a = drift('FCOR', 0.044, 'DriftPass'); %s= 532.266 + 0.044
D_794_sh1g2c20a = drift('DRIFT', 0.312, 'DriftPass'); % +0.312= sb(532.622)
sh1g2c20a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 532.622 + 0.2
D_795_ph1g2c20a = drift('DRIFT', 0.085, 'DriftPass'); % +0.085= sb(532.907)
ph1g2c20a = drift('BPM', 0.0, 'DriftPass'); %s= 532.907 + 0.0
D_796_qh1g2c20a = drift('DRIFT', 0.077, 'DriftPass'); % +0.077= sb(532.984)
qh1g2c20a = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 532.984 + 0.275
D_797_ch1g2c20a = drift('DRIFT', 0.245, 'DriftPass'); % +0.245= sb(533.504)
ch1g2c20a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 533.504 + 0.0
sqhhg2c20a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 533.504 + 0.1
D_799_qh2g2c20a = drift('DRIFT', 0.46, 'DriftPass'); % +0.46= sb(534.064)
qh2g2c20a = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 534.064 + 0.448
D_800_sh3g2c20a = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(534.702)
sh3g2c20a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 534.702 + 0.2
D_801_qh3g2c20a = drift('DRIFT', 0.182, 'DriftPass'); % +0.182= sb(535.084)
qh3g2c20a = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 535.084 + 0.275
D_802_ph2g2c20a = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(535.432)
ph2g2c20a = drift('BPM', 0.0, 'DriftPass'); %s= 535.432 + 0.0
D_803_sh4g2c20a = drift('DRIFT', 0.0899999999999, 'DriftPass'); % +0.0899999999999= sb(535.522)
sh4g2c20a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 535.522 + 0.2
D_804_ch2g2c20a = drift('DRIFT', 0.248, 'DriftPass'); % +0.248= sb(535.97)
ch2g2c20a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 535.97 + 0.3
D_805_b1g3c20a = drift('DRIFT', 0.032, 'DriftPass'); % +0.032= sb(536.302)
b1g3c20a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 536.302 + 2.62
D_806_cm1g4c20a = drift('DRIFT', 0.501, 'DriftPass'); % +0.501= sb(539.423)
cm1g4c20a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 539.423 + 0.2
D_807_qm1g4c20a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(539.897)
qm1g4c20a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 539.897 + 0.25
D_808_sm1g4c20a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(540.347)
sm1g4c20a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 540.347 + 0.2
D_809_fm1g4c20a = drift('DRIFT', 0.233, 'DriftPass'); % +0.233= sb(540.78)
fm1g4c20a = drift('FCOR', 0.044, 'DriftPass'); %s= 540.78 + 0.044
D_810_pm1g4c20a = drift('DRIFT', 0.293, 'DriftPass'); % +0.293= sb(541.117)
pm1g4c20a = drift('BPM', 0.0, 'DriftPass'); %s= 541.117 + 0.0
D_811_qm2g4c20a = drift('DRIFT', 0.0840000000001, 'DriftPass'); % +0.0840000000001= sb(541.201)
qm2g4c20a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 541.201 + 0.283
D_812_sm2g4c20b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(541.667)
sm2g4c20b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 541.667 + 0.25
D_813_qm2g4c20b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(542.101)
qm2g4c20b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 542.101 + 0.283
D_814_sm1g4c20b = drift('DRIFT', 0.503, 'DriftPass'); % +0.503= sb(542.887)
sm1g4c20b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 542.887 + 0.2
D_815_pm1g4c20b = drift('DRIFT', 0.262, 'DriftPass'); % +0.262= sb(543.349)
pm1g4c20b = drift('BPM', 0.0, 'DriftPass'); %s= 543.349 + 0.0
D_816_qm1g4c20b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(543.437)
qm1g4c20b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 543.437 + 0.25
D_817_cm1g4c20b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(543.796)
cm1g4c20b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 543.796 + 0.3
D_818_b1g5c20b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(544.662)
b1g5c20b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 544.662 + 2.62
D_819_ql3g6c20b = drift('DRIFT', 0.588, 'DriftPass'); % +0.588= sb(547.87)
ql3g6c20b = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 547.87 + 0.275
D_820_pl2g6c20b = drift('DRIFT', 0.0740000000001, 'DriftPass'); % +0.0740000000001= sb(548.219)
pl2g6c20b = drift('BPM', 0.0, 'DriftPass'); %s= 548.219 + 0.0
D_821_sl3g6c20b = drift('DRIFT', 0.0879999999999, 'DriftPass'); % +0.0879999999999= sb(548.307)
sl3g6c20b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 548.307 + 0.2
D_822_cl2g6c20b = drift('DRIFT', 0.158, 'DriftPass'); % +0.158= sb(548.665)
cl2g6c20b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 548.665 + 0.2
D_823_ql2g6c20b = drift('DRIFT', 0.208, 'DriftPass'); % +0.208= sb(549.073)
ql2g6c20b = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 549.073 + 0.448
D_824_sl2g6c20b = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(549.771)
sl2g6c20b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 549.771 + 0.2
D_825_cl1g6c20b = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(550.102)
cl1g6c20b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 550.102 + 0.2
D_826_ql1g6c20b = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(550.433)
ql1g6c20b = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 550.433 + 0.275
D_827_pl1g6c20b = drift('DRIFT', 0.075, 'DriftPass'); % +0.075= sb(550.783)
pl1g6c20b = drift('BPM', 0.0, 'DriftPass'); %s= 550.783 + 0.0
D_828_sl1g6c20b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(550.871)
sl1g6c20b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 550.871 + 0.2
D_829_fl1g1c21a = drift('DRIFT', 0.446, 'DriftPass'); % +0.446= sb(551.517)
fl1g1c21a = drift('FCOR', 0.044, 'DriftPass'); %s= 551.517 + 0.044
D_830_fl2g1c21a = drift('DRIFT', 5.753, 'DriftPass'); % +5.753= sb(557.314)
fl2g1c21a = drift('FCOR', 0.044, 'DriftPass'); %s= 557.314 + 0.044
D_831_sl1g2c21a = drift('DRIFT', 0.313, 'DriftPass'); % +0.313= sb(557.671)
sl1g2c21a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 557.671 + 0.2
D_832_pl1g2c21a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(557.961)
pl1g2c21a = drift('BPM', 0.0, 'DriftPass'); %s= 557.961 + 0.0
D_833_ql1g2c21a = drift('DRIFT', 0.072, 'DriftPass'); % +0.072= sb(558.033)
ql1g2c21a = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 558.033 + 0.275
D_834_cl1g2c21a = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(558.439)
cl1g2c21a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 558.439 + 0.2
D_835_sl2g2c21a = drift('DRIFT', 0.132, 'DriftPass'); % +0.132= sb(558.771)
sl2g2c21a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 558.771 + 0.2
D_836_ql2g2c21a = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(559.221)
ql2g2c21a = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 559.221 + 0.448
D_837_cl2g2c21a = drift('DRIFT', 0.208, 'DriftPass'); % +0.208= sb(559.877)
cl2g2c21a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 559.877 + 0.2
D_838_sl3g2c21a = drift('DRIFT', 0.157, 'DriftPass'); % +0.157= sb(560.234)
sl3g2c21a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 560.234 + 0.2
D_839_pl2g2c21a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(560.524)
pl2g2c21a = drift('BPM', 0.0, 'DriftPass'); %s= 560.524 + 0.0
D_840_ql3g2c21a = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(560.597)
ql3g2c21a = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 560.597 + 0.275
D_841_b1g3c21a = drift('DRIFT', 0.587, 'DriftPass'); % +0.587= sb(561.459)
b1g3c21a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 561.459 + 2.62
D_842_cm1g4c21a = drift('DRIFT', 0.601, 'DriftPass'); % +0.601= sb(564.68)
cm1g4c21a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 564.68 + 0.0
sqmhg4c21a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 564.68 + 0.1
D_844_qm1g4c21a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(565.054)
qm1g4c21a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 565.054 + 0.25
D_845_sm1g4c21a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(565.504)
sm1g4c21a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 565.504 + 0.2
D_846_fm1g4c21a = drift('DRIFT', 0.233, 'DriftPass'); % +0.233= sb(565.937)
fm1g4c21a = drift('FCOR', 0.044, 'DriftPass'); %s= 565.937 + 0.044
D_847_pm1g4c21a = drift('DRIFT', 0.293, 'DriftPass'); % +0.293= sb(566.274)
pm1g4c21a = drift('BPM', 0.0, 'DriftPass'); %s= 566.274 + 0.0
D_848_qm2g4c21a = drift('DRIFT', 0.0839999999999, 'DriftPass'); % +0.0839999999999= sb(566.358)
qm2g4c21a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 566.358 + 0.283
D_849_sm2g4c21b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(566.824)
sm2g4c21b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 566.824 + 0.25
D_850_qm2g4c21b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(567.258)
qm2g4c21b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 567.258 + 0.283
D_851_sm1g4c21b = drift('DRIFT', 0.503, 'DriftPass'); % +0.503= sb(568.044)
sm1g4c21b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 568.044 + 0.2
D_852_pm1g4c21b = drift('DRIFT', 0.262, 'DriftPass'); % +0.262= sb(568.506)
pm1g4c21b = drift('BPM', 0.0, 'DriftPass'); %s= 568.506 + 0.0
D_853_qm1g4c21b = drift('DRIFT', 0.0880000000001, 'DriftPass'); % +0.0880000000001= sb(568.594)
qm1g4c21b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 568.594 + 0.25
D_854_cm1g4c21b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(568.953)
cm1g4c21b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 568.953 + 0.3
D_855_b1g5c21b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(569.819)
b1g5c21b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 569.819 + 2.62
D_856_ch2g6c21b = drift('DRIFT', 0.217, 'DriftPass'); % +0.217= sb(572.656)
ch2g6c21b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 572.656 + 0.3
D_857_sh4g6c21b = drift('DRIFT', 0.063, 'DriftPass'); % +0.063= sb(573.019)
sh4g6c21b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 573.019 + 0.2
D_858_ph2g6c21b = drift('DRIFT', 0.0899999999999, 'DriftPass'); % +0.0899999999999= sb(573.309)
ph2g6c21b = drift('BPM', 0.0, 'DriftPass'); %s= 573.309 + 0.0
D_859_qh3g6c21b = drift('DRIFT', 0.0730000000001, 'DriftPass'); % +0.0730000000001= sb(573.382)
qh3g6c21b = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 573.382 + 0.275
D_860_sh3g6c21b = drift('DRIFT', 0.182, 'DriftPass'); % +0.182= sb(573.839)
sh3g6c21b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 573.839 + 0.2
D_861_qh2g6c21b = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(574.229)
qh2g6c21b = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 574.229 + 0.448
D_862_ch1g6c21b = drift('DRIFT', 0.485, 'DriftPass'); % +0.485= sb(575.162)
ch1g6c21b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 575.162 + 0.2
D_863_qh1g6c21b = drift('DRIFT', 0.12, 'DriftPass'); % +0.12= sb(575.482)
qh1g6c21b = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 575.482 + 0.275
D_864_ph1g6c21b = drift('DRIFT', 0.077, 'DriftPass'); % +0.077= sb(575.834)
ph1g6c21b = drift('BPM', 0.0, 'DriftPass'); %s= 575.834 + 0.0
D_865_sh1g6c21b = drift('DRIFT', 0.085, 'DriftPass'); % +0.085= sb(575.919)
sh1g6c21b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 575.919 + 0.2
D_866_fh1g1c22a = drift('DRIFT', 0.441, 'DriftPass'); % +0.441= sb(576.56)
fh1g1c22a = drift('FCOR', 0.044, 'DriftPass'); %s= 576.56 + 0.044
D_867_fh2g1c22a = drift('DRIFT', 8.459, 'DriftPass'); % +8.459= sb(585.063)
fh2g1c22a = drift('FCOR', 0.044, 'DriftPass'); %s= 585.063 + 0.044
D_868_sh1g2c22a = drift('DRIFT', 0.312, 'DriftPass'); % +0.312= sb(585.419)
sh1g2c22a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 585.419 + 0.2
D_869_ph1g2c22a = drift('DRIFT', 0.0849999999999, 'DriftPass'); % +0.0849999999999= sb(585.704)
ph1g2c22a = drift('BPM', 0.0, 'DriftPass'); %s= 585.704 + 0.0
D_870_qh1g2c22a = drift('DRIFT', 0.0780000000001, 'DriftPass'); % +0.0780000000001= sb(585.782)
qh1g2c22a = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 585.782 + 0.275
D_871_ch1g2c22a = drift('DRIFT', 0.245, 'DriftPass'); % +0.245= sb(586.302)
ch1g2c22a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 586.302 + 0.0
sqhhg2c22a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 586.302 + 0.1
D_873_qh2g2c22a = drift('DRIFT', 0.459, 'DriftPass'); % +0.459= sb(586.861)
qh2g2c22a = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 586.861 + 0.448
D_874_sh3g2c22a = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(587.499)
sh3g2c22a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 587.499 + 0.2
D_875_qh3g2c22a = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(587.882)
qh3g2c22a = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 587.882 + 0.275
D_876_ph2g2c22a = drift('DRIFT', 0.072, 'DriftPass'); % +0.072= sb(588.229)
ph2g2c22a = drift('BPM', 0.0, 'DriftPass'); %s= 588.229 + 0.0
D_877_sh4g2c22a = drift('DRIFT', 0.0899999999999, 'DriftPass'); % +0.0899999999999= sb(588.319)
sh4g2c22a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 588.319 + 0.2
D_878_ch2g2c22a = drift('DRIFT', 0.249, 'DriftPass'); % +0.249= sb(588.768)
ch2g2c22a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 588.768 + 0.3
D_879_b1g3c22a = drift('DRIFT', 0.0310000000001, 'DriftPass'); % +0.0310000000001= sb(589.099)
b1g3c22a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 589.099 + 2.62
D_880_cm1g4c22a = drift('DRIFT', 0.501, 'DriftPass'); % +0.501= sb(592.22)
cm1g4c22a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 592.22 + 0.2
D_881_qm1g4c22a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(592.694)
qm1g4c22a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 592.694 + 0.25
D_882_sm1g4c22a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(593.144)
sm1g4c22a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 593.144 + 0.2
D_883_fm1g4c22a = drift('DRIFT', 0.233, 'DriftPass'); % +0.233= sb(593.577)
fm1g4c22a = drift('FCOR', 0.044, 'DriftPass'); %s= 593.577 + 0.044
D_884_pm1g4c22a = drift('DRIFT', 0.293, 'DriftPass'); % +0.293= sb(593.914)
pm1g4c22a = drift('BPM', 0.0, 'DriftPass'); %s= 593.914 + 0.0
D_885_qm2g4c22a = drift('DRIFT', 0.0839999999999, 'DriftPass'); % +0.0839999999999= sb(593.998)
qm2g4c22a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 593.998 + 0.283
D_886_sm2g4c22b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(594.464)
sm2g4c22b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 594.464 + 0.25
D_887_qm2g4c22b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(594.898)
qm2g4c22b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 594.898 + 0.283
D_888_sm1g4c22b = drift('DRIFT', 0.503, 'DriftPass'); % +0.503= sb(595.684)
sm1g4c22b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 595.684 + 0.2
D_889_pm1g4c22b = drift('DRIFT', 0.262, 'DriftPass'); % +0.262= sb(596.146)
pm1g4c22b = drift('BPM', 0.0, 'DriftPass'); %s= 596.146 + 0.0
D_890_qm1g4c22b = drift('DRIFT', 0.0880000000001, 'DriftPass'); % +0.0880000000001= sb(596.234)
qm1g4c22b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 596.234 + 0.25
D_891_cm1g4c22b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(596.593)
cm1g4c22b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 596.593 + 0.3
D_892_b1g5c22b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(597.459)
b1g5c22b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 597.459 + 2.62
D_893_ql3g6c22b = drift('DRIFT', 0.588, 'DriftPass'); % +0.588= sb(600.667)
ql3g6c22b = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 600.667 + 0.275
D_894_pl2g6c22b = drift('DRIFT', 0.074, 'DriftPass'); % +0.074= sb(601.016)
pl2g6c22b = drift('BPM', 0.0, 'DriftPass'); %s= 601.016 + 0.0
D_895_sl3g6c22b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(601.104)
sl3g6c22b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 601.104 + 0.2
D_896_cl2g6c22b = drift('DRIFT', 0.158, 'DriftPass'); % +0.158= sb(601.462)
cl2g6c22b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 601.462 + 0.2
D_897_ql2g6c22b = drift('DRIFT', 0.208, 'DriftPass'); % +0.208= sb(601.87)
ql2g6c22b = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 601.87 + 0.448
D_898_sl2g6c22b = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(602.568)
sl2g6c22b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 602.568 + 0.2
D_899_cl1g6c22b = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(602.899)
cl1g6c22b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 602.899 + 0.2
D_900_ql1g6c22b = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(603.23)
ql1g6c22b = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 603.23 + 0.275
D_901_pl1g6c22b = drift('DRIFT', 0.075, 'DriftPass'); % +0.075= sb(603.58)
pl1g6c22b = drift('BPM', 0.0, 'DriftPass'); %s= 603.58 + 0.0
D_902_sl1g6c22b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(603.668)
sl1g6c22b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 603.668 + 0.2
D_903_fl1g1c23a = drift('DRIFT', 0.446, 'DriftPass'); % +0.446= sb(604.314)
fl1g1c23a = drift('FCOR', 0.044, 'DriftPass'); %s= 604.314 + 0.044
D_904_cu1g1c23id1 = drift('DRIFT', 0.605, 'DriftPass'); % +0.605= sb(604.963)
cu1g1c23id1 = drift('IDCOR', 0.0, 'DriftPass'); %s= 604.963 + 0.0
cs1g1c23id1 = drift('IDSIMCOR', 0.0, 'DriftPass'); %s= 604.963 + 0.0
epu49g1c23u = drift('INSERTION', 2.0, 'DriftPass'); %s= 604.963 + 2.0
cu2g1c23id1 = drift('IDCOR', 0.0, 'DriftPass'); %s= 606.963 + 0.0
cs2g1c23id1 = drift('IDSIMCOR', 0.0, 'DriftPass'); %s= 606.963 + 0.0
D_909_cu1g1c23id2 = drift('DRIFT', 0.485, 'DriftPass'); % +0.485= sb(607.448)
cu1g1c23id2 = drift('IDCOR', 0.0, 'DriftPass'); %s= 607.448 + 0.0
cs1g1c23id2 = drift('IDSIMCOR', 0.0, 'DriftPass'); %s= 607.448 + 0.0
epu49g1c23d = drift('INSERTION', 2.0, 'DriftPass'); %s= 607.448 + 2.0
cu2g1c23id2 = drift('IDCOR', 0.0, 'DriftPass'); %s= 609.448 + 0.0
cs2g1c23id2 = drift('IDSIMCOR', 0.0, 'DriftPass'); %s= 609.448 + 0.0
D_914_fl2g1c23a = drift('DRIFT', 0.663, 'DriftPass'); % +0.663= sb(610.111)
fl2g1c23a = drift('FCOR', 0.044, 'DriftPass'); %s= 610.111 + 0.044
D_915_sl1g2c23a = drift('DRIFT', 0.313, 'DriftPass'); % +0.313= sb(610.468)
sl1g2c23a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 610.468 + 0.2
D_916_pl1g2c23a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(610.758)
pl1g2c23a = drift('BPM', 0.0, 'DriftPass'); %s= 610.758 + 0.0
D_917_ql1g2c23a = drift('DRIFT', 0.072, 'DriftPass'); % +0.072= sb(610.83)
ql1g2c23a = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 610.83 + 0.275
D_918_cl1g2c23a = drift('DRIFT', 0.132, 'DriftPass'); % +0.132= sb(611.237)
cl1g2c23a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 611.237 + 0.2
D_919_sl2g2c23a = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(611.568)
sl2g2c23a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 611.568 + 0.2
D_920_ql2g2c23a = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(612.018)
ql2g2c23a = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 612.018 + 0.448
D_921_cl2g2c23a = drift('DRIFT', 0.208, 'DriftPass'); % +0.208= sb(612.674)
cl2g2c23a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 612.674 + 0.2
D_922_sl3g2c23a = drift('DRIFT', 0.157, 'DriftPass'); % +0.157= sb(613.031)
sl3g2c23a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 613.031 + 0.2
D_923_pl2g2c23a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(613.321)
pl2g2c23a = drift('BPM', 0.0, 'DriftPass'); %s= 613.321 + 0.0
D_924_ql3g2c23a = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(613.394)
ql3g2c23a = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 613.394 + 0.275
D_925_b2g3c23a = drift('DRIFT', 0.587, 'DriftPass'); % +0.587= sb(614.256)
b2g3c23a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 614.256 + 2.62
D_926_cm1g4c23a = drift('DRIFT', 0.601, 'DriftPass'); % +0.601= sb(617.477)
cm1g4c23a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 617.477 + 0.0
sqmhg4c23a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 617.477 + 0.1
D_928_qm1g4c23a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(617.851)
qm1g4c23a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 617.851 + 0.25
D_929_sm1g4c23a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(618.301)
sm1g4c23a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 618.301 + 0.2
D_930_fm1g4c23a = drift('DRIFT', 0.234, 'DriftPass'); % +0.234= sb(618.735)
fm1g4c23a = drift('FCOR', 0.044, 'DriftPass'); %s= 618.735 + 0.044
D_931_pm1g4c23a = drift('DRIFT', 0.292, 'DriftPass'); % +0.292= sb(619.071)
pm1g4c23a = drift('BPM', 0.0, 'DriftPass'); %s= 619.071 + 0.0
D_932_qm2g4c23a = drift('DRIFT', 0.0839999999999, 'DriftPass'); % +0.0839999999999= sb(619.155)
qm2g4c23a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 619.155 + 0.283
D_933_sm2g4c23b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(619.621)
sm2g4c23b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 619.621 + 0.25
D_934_qm2g4c23b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(620.055)
qm2g4c23b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 620.055 + 0.283
D_935_sm1g4c23b = drift('DRIFT', 0.503, 'DriftPass'); % +0.503= sb(620.841)
sm1g4c23b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 620.841 + 0.2
D_936_pm1g4c23b = drift('DRIFT', 0.263, 'DriftPass'); % +0.263= sb(621.304)
pm1g4c23b = drift('BPM', 0.0, 'DriftPass'); %s= 621.304 + 0.0
D_937_qm1g4c23b = drift('DRIFT', 0.087, 'DriftPass'); % +0.087= sb(621.391)
qm1g4c23b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 621.391 + 0.25
D_938_cm1g4c23b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(621.75)
cm1g4c23b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 621.75 + 0.3
D_939_b2g5c23b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(622.616)
b2g5c23b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 622.616 + 2.62
D_940_ch2g6c23b = drift('DRIFT', 0.217, 'DriftPass'); % +0.217= sb(625.453)
ch2g6c23b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 625.453 + 0.3
D_941_sh4g6c23b = drift('DRIFT', 0.0629999999999, 'DriftPass'); % +0.0629999999999= sb(625.816)
sh4g6c23b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 625.816 + 0.2
D_942_ph2g6c23b = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(626.106)
ph2g6c23b = drift('BPM', 0.0, 'DriftPass'); %s= 626.106 + 0.0
D_943_qh3g6c23b = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(626.179)
qh3g6c23b = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 626.179 + 0.275
D_944_sh3g6c23b = drift('DRIFT', 0.182, 'DriftPass'); % +0.182= sb(626.636)
sh3g6c23b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 626.636 + 0.2
D_945_qh2g6c23b = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(627.026)
qh2g6c23b = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 627.026 + 0.448
D_946_ch1g6c23b = drift('DRIFT', 0.485, 'DriftPass'); % +0.485= sb(627.959)
ch1g6c23b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 627.959 + 0.2
D_947_qh1g6c23b = drift('DRIFT', 0.12, 'DriftPass'); % +0.12= sb(628.279)
qh1g6c23b = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 628.279 + 0.275
D_948_ph1g6c23b = drift('DRIFT', 0.077, 'DriftPass'); % +0.077= sb(628.631)
ph1g6c23b = drift('BPM', 0.0, 'DriftPass'); %s= 628.631 + 0.0
D_949_sh1g6c23b = drift('DRIFT', 0.085, 'DriftPass'); % +0.085= sb(628.716)
sh1g6c23b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 628.716 + 0.2
D_950_fh1g1c24a = drift('DRIFT', 0.441, 'DriftPass'); % +0.441= sb(629.357)
fh1g1c24a = drift('FCOR', 0.044, 'DriftPass'); %s= 629.357 + 0.044
D_951_cav = drift('DRIFT', 4.165, 'DriftPass'); % +4.165= sb(633.566)
cav = rfcavity('RFCAVITY', 0.0, 5000000.0, 499681000.0, 1320, 'CavityPass'); %s= 633.566 + 0.0
D_952_fh2g1c24a = drift('DRIFT', 4.294, 'DriftPass'); % +4.294= sb(637.86)
fh2g1c24a = drift('FCOR', 0.044, 'DriftPass'); %s= 637.86 + 0.044
D_953_sh1g2c24a = drift('DRIFT', 0.312, 'DriftPass'); % +0.312= sb(638.216)
sh1g2c24a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 638.216 + 0.2
D_954_ph1g2c24a = drift('DRIFT', 0.0849999999999, 'DriftPass'); % +0.0849999999999= sb(638.501)
ph1g2c24a = drift('BPM', 0.0, 'DriftPass'); %s= 638.501 + 0.0
D_955_qh1g2c24a = drift('DRIFT', 0.0780000000001, 'DriftPass'); % +0.0780000000001= sb(638.579)
qh1g2c24a = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 638.579 + 0.275
D_956_ch1g2c24a = drift('DRIFT', 0.245, 'DriftPass'); % +0.245= sb(639.099)
ch1g2c24a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 639.099 + 0.0
sqhhg2c24a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 639.099 + 0.1
D_958_qh2g2c24a = drift('DRIFT', 0.459, 'DriftPass'); % +0.459= sb(639.658)
qh2g2c24a = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 639.658 + 0.448
D_959_sh3g2c24a = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(640.296)
sh3g2c24a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 640.296 + 0.2
D_960_qh3g2c24a = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(640.679)
qh3g2c24a = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 640.679 + 0.275
D_961_ph2g2c24a = drift('DRIFT', 0.072, 'DriftPass'); % +0.072= sb(641.026)
ph2g2c24a = drift('BPM', 0.0, 'DriftPass'); %s= 641.026 + 0.0
D_962_sh4g2c24a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(641.116)
sh4g2c24a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 641.116 + 0.2
D_963_ch2g2c24a = drift('DRIFT', 0.249, 'DriftPass'); % +0.249= sb(641.565)
ch2g2c24a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 641.565 + 0.3
D_964_b1g3c24a = drift('DRIFT', 0.0309999999999, 'DriftPass'); % +0.0309999999999= sb(641.896)
b1g3c24a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 641.896 + 2.62
D_965_cm1g4c24a = drift('DRIFT', 0.501, 'DriftPass'); % +0.501= sb(645.017)
cm1g4c24a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 645.017 + 0.2
D_966_qm1g4c24a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(645.491)
qm1g4c24a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 645.491 + 0.25
D_967_sm1g4c24a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(645.941)
sm1g4c24a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 645.941 + 0.2
D_968_fm1g4c24a = drift('DRIFT', 0.234, 'DriftPass'); % +0.234= sb(646.375)
fm1g4c24a = drift('FCOR', 0.044, 'DriftPass'); %s= 646.375 + 0.044
D_969_pm1g4c24a = drift('DRIFT', 0.292, 'DriftPass'); % +0.292= sb(646.711)
pm1g4c24a = drift('BPM', 0.0, 'DriftPass'); %s= 646.711 + 0.0
D_970_qm2g4c24a = drift('DRIFT', 0.0839999999999, 'DriftPass'); % +0.0839999999999= sb(646.795)
qm2g4c24a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 646.795 + 0.283
D_971_sm2g4c24b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(647.261)
sm2g4c24b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 647.261 + 0.25
D_972_qm2g4c24b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(647.695)
qm2g4c24b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 647.695 + 0.283
D_973_sm1g4c24b = drift('DRIFT', 0.503, 'DriftPass'); % +0.503= sb(648.481)
sm1g4c24b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 648.481 + 0.2
D_974_pm1g4c24b = drift('DRIFT', 0.263, 'DriftPass'); % +0.263= sb(648.944)
pm1g4c24b = drift('BPM', 0.0, 'DriftPass'); %s= 648.944 + 0.0
D_975_qm1g4c24b = drift('DRIFT', 0.087, 'DriftPass'); % +0.087= sb(649.031)
qm1g4c24b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 649.031 + 0.25
D_976_cm1g4c24b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(649.39)
cm1g4c24b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 649.39 + 0.3
D_977_b1g5c24b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(650.256)
b1g5c24b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 650.256 + 2.62
D_978_ql3g6c24b = drift('DRIFT', 0.588, 'DriftPass'); % +0.588= sb(653.464)
ql3g6c24b = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 653.464 + 0.275
D_979_pl2g6c24b = drift('DRIFT', 0.0749999999999, 'DriftPass'); % +0.0749999999999= sb(653.814)
pl2g6c24b = drift('BPM', 0.0, 'DriftPass'); %s= 653.814 + 0.0
D_980_sl3g6c24b = drift('DRIFT', 0.087, 'DriftPass'); % +0.087= sb(653.901)
sl3g6c24b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 653.901 + 0.2
D_981_cl2g6c24b = drift('DRIFT', 0.158, 'DriftPass'); % +0.158= sb(654.259)
cl2g6c24b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 654.259 + 0.2
D_982_ql2g6c24b = drift('DRIFT', 0.208, 'DriftPass'); % +0.208= sb(654.667)
ql2g6c24b = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 654.667 + 0.448
D_983_sl2g6c24b = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(655.365)
sl2g6c24b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 655.365 + 0.2
D_984_cl1g6c24b = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(655.696)
cl1g6c24b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 655.696 + 0.2
D_985_ql1g6c24b = drift('DRIFT', 0.132, 'DriftPass'); % +0.132= sb(656.028)
ql1g6c24b = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 656.028 + 0.275
D_986_pl1g6c24b = drift('DRIFT', 0.074, 'DriftPass'); % +0.074= sb(656.377)
pl1g6c24b = drift('BPM', 0.0, 'DriftPass'); %s= 656.377 + 0.0
D_987_sl1g6c24b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(656.465)
sl1g6c24b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 656.465 + 0.2
D_988_fl1g1c25a = drift('DRIFT', 0.447, 'DriftPass'); % +0.447= sb(657.112)
fl1g1c25a = drift('FCOR', 0.044, 'DriftPass'); %s= 657.112 + 0.044
D_989_fl2g1c25a = drift('DRIFT', 5.753, 'DriftPass'); % +5.753= sb(662.909)
fl2g1c25a = drift('FCOR', 0.044, 'DriftPass'); %s= 662.909 + 0.044
D_990_sl1g2c25a = drift('DRIFT', 0.312, 'DriftPass'); % +0.312= sb(663.265)
sl1g2c25a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 663.265 + 0.2
D_991_pl1g2c25a = drift('DRIFT', 0.0899999999999, 'DriftPass'); % +0.0899999999999= sb(663.555)
pl1g2c25a = drift('BPM', 0.0, 'DriftPass'); %s= 663.555 + 0.0
D_992_ql1g2c25a = drift('DRIFT', 0.0730000000001, 'DriftPass'); % +0.0730000000001= sb(663.628)
ql1g2c25a = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 663.628 + 0.275
D_993_cl1g2c25a = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(664.034)
cl1g2c25a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 664.034 + 0.2
D_994_sl2g2c25a = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(664.365)
sl2g2c25a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 664.365 + 0.2
D_995_ql2g2c25a = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(664.815)
ql2g2c25a = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 664.815 + 0.448
D_996_cl2g2c25a = drift('DRIFT', 0.208, 'DriftPass'); % +0.208= sb(665.471)
cl2g2c25a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 665.471 + 0.2
D_997_sl3g2c25a = drift('DRIFT', 0.158, 'DriftPass'); % +0.158= sb(665.829)
sl3g2c25a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 665.829 + 0.2
D_998_pl2g2c25a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(666.119)
pl2g2c25a = drift('BPM', 0.0, 'DriftPass'); %s= 666.119 + 0.0
D_999_ql3g2c25a = drift('DRIFT', 0.072, 'DriftPass'); % +0.072= sb(666.191)
ql3g2c25a = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 666.191 + 0.275
D_1000_b1g3c25a = drift('DRIFT', 0.588, 'DriftPass'); % +0.588= sb(667.054)
b1g3c25a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 667.054 + 2.62
D_1001_cm1g4c25a = drift('DRIFT', 0.601, 'DriftPass'); % +0.601= sb(670.275)
cm1g4c25a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 670.275 + 0.0
sqmhg4c25a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 670.275 + 0.1
D_1003_qm1g4c25a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(670.649)
qm1g4c25a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 670.649 + 0.25
D_1004_sm1g4c25a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(671.099)
sm1g4c25a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 671.099 + 0.2
D_1005_fm1g4c25a = drift('DRIFT', 0.233, 'DriftPass'); % +0.233= sb(671.532)
fm1g4c25a = drift('FCOR', 0.044, 'DriftPass'); %s= 671.532 + 0.044
D_1006_pm1g4c25a = drift('DRIFT', 0.292, 'DriftPass'); % +0.292= sb(671.868)
pm1g4c25a = drift('BPM', 0.0, 'DriftPass'); %s= 671.868 + 0.0
D_1007_qm2g4c25a = drift('DRIFT', 0.0839999999999, 'DriftPass'); % +0.0839999999999= sb(671.952)
qm2g4c25a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 671.952 + 0.283
D_1008_sm2g4c25b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(672.419)
sm2g4c25b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 672.419 + 0.25
D_1009_qm2g4c25b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(672.852)
qm2g4c25b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 672.852 + 0.283
D_1010_sm1g4c25b = drift('DRIFT', 0.504, 'DriftPass'); % +0.504= sb(673.639)
sm1g4c25b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 673.639 + 0.2
D_1011_pm1g4c25b = drift('DRIFT', 0.262, 'DriftPass'); % +0.262= sb(674.101)
pm1g4c25b = drift('BPM', 0.0, 'DriftPass'); %s= 674.101 + 0.0
D_1012_qm1g4c25b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(674.189)
qm1g4c25b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 674.189 + 0.25
D_1013_cm1g4c25b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(674.548)
cm1g4c25b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 674.548 + 0.3
D_1014_b1g5c25b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(675.414)
b1g5c25b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 675.414 + 2.62
D_1015_ch2g6c25b = drift('DRIFT', 0.216, 'DriftPass'); % +0.216= sb(678.25)
ch2g6c25b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 678.25 + 0.3
D_1016_sh4g6c25b = drift('DRIFT', 0.064, 'DriftPass'); % +0.064= sb(678.614)
sh4g6c25b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 678.614 + 0.2
D_1017_ph2g6c25b = drift('DRIFT', 0.0890000000001, 'DriftPass'); % +0.0890000000001= sb(678.903)
ph2g6c25b = drift('BPM', 0.0, 'DriftPass'); %s= 678.903 + 0.0
D_1018_qh3g6c25b = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(678.976)
qh3g6c25b = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 678.976 + 0.275
D_1019_sh3g6c25b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(679.434)
sh3g6c25b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 679.434 + 0.2
D_1020_qh2g6c25b = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(679.824)
qh2g6c25b = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 679.824 + 0.448
D_1021_ch1g6c25b = drift('DRIFT', 0.484, 'DriftPass'); % +0.484= sb(680.756)
ch1g6c25b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 680.756 + 0.2
D_1022_qh1g6c25b = drift('DRIFT', 0.12, 'DriftPass'); % +0.12= sb(681.076)
qh1g6c25b = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 681.076 + 0.275
D_1023_ph1g6c25b = drift('DRIFT', 0.077, 'DriftPass'); % +0.077= sb(681.428)
ph1g6c25b = drift('BPM', 0.0, 'DriftPass'); %s= 681.428 + 0.0
D_1024_sh1g6c25b = drift('DRIFT', 0.086, 'DriftPass'); % +0.086= sb(681.514)
sh1g6c25b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 681.514 + 0.2
D_1025_fh1g1c26a = drift('DRIFT', 0.441, 'DriftPass'); % +0.441= sb(682.155)
fh1g1c26a = drift('FCOR', 0.044, 'DriftPass'); %s= 682.155 + 0.044
D_1026_fh2g1c26a = drift('DRIFT', 8.458, 'DriftPass'); % +8.458= sb(690.657)
fh2g1c26a = drift('FCOR', 0.044, 'DriftPass'); %s= 690.657 + 0.044
D_1027_sh1g2c26a = drift('DRIFT', 0.313, 'DriftPass'); % +0.313= sb(691.014)
sh1g2c26a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 691.014 + 0.2
D_1028_ph1g2c26a = drift('DRIFT', 0.0849999999999, 'DriftPass'); % +0.0849999999999= sb(691.299)
ph1g2c26a = drift('BPM', 0.0, 'DriftPass'); %s= 691.299 + 0.0
D_1029_qh1g2c26a = drift('DRIFT', 0.077, 'DriftPass'); % +0.077= sb(691.376)
qh1g2c26a = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 691.376 + 0.275
D_1030_ch1g2c26a = drift('DRIFT', 0.245, 'DriftPass'); % +0.245= sb(691.896)
ch1g2c26a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 691.896 + 0.0
sqhhg2c26a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 691.896 + 0.1
D_1032_qh2g2c26a = drift('DRIFT', 0.46, 'DriftPass'); % +0.46= sb(692.456)
qh2g2c26a = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 692.456 + 0.448
D_1033_sh3g2c26a = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(693.094)
sh3g2c26a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 693.094 + 0.2
D_1034_qh3g2c26a = drift('DRIFT', 0.182, 'DriftPass'); % +0.182= sb(693.476)
qh3g2c26a = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 693.476 + 0.275
D_1035_ph2g2c26a = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(693.824)
ph2g2c26a = drift('BPM', 0.0, 'DriftPass'); %s= 693.824 + 0.0
D_1036_sh4g2c26a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(693.914)
sh4g2c26a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 693.914 + 0.2
D_1037_ch2g2c26a = drift('DRIFT', 0.248, 'DriftPass'); % +0.248= sb(694.362)
ch2g2c26a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 694.362 + 0.3
D_1038_b1g3c26a = drift('DRIFT', 0.0319999999999, 'DriftPass'); % +0.0319999999999= sb(694.694)
b1g3c26a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 694.694 + 2.62
D_1039_cm1g4c26a = drift('DRIFT', 0.501, 'DriftPass'); % +0.501= sb(697.815)
cm1g4c26a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 697.815 + 0.2
D_1040_qm1g4c26a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(698.289)
qm1g4c26a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 698.289 + 0.25
D_1041_sm1g4c26a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(698.739)
sm1g4c26a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 698.739 + 0.2
D_1042_fm1g4c26a = drift('DRIFT', 0.233, 'DriftPass'); % +0.233= sb(699.172)
fm1g4c26a = drift('FCOR', 0.044, 'DriftPass'); %s= 699.172 + 0.044
D_1043_pm1g4c26a = drift('DRIFT', 0.292, 'DriftPass'); % +0.292= sb(699.508)
pm1g4c26a = drift('BPM', 0.0, 'DriftPass'); %s= 699.508 + 0.0
D_1044_qm2g4c26a = drift('DRIFT', 0.0839999999999, 'DriftPass'); % +0.0839999999999= sb(699.592)
qm2g4c26a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 699.592 + 0.283
D_1045_sm2g4c26b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(700.059)
sm2g4c26b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 700.059 + 0.25
D_1046_qm2g4c26b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(700.492)
qm2g4c26b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 700.492 + 0.283
D_1047_sm1g4c26b = drift('DRIFT', 0.504, 'DriftPass'); % +0.504= sb(701.279)
sm1g4c26b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 701.279 + 0.2
D_1048_pm1g4c26b = drift('DRIFT', 0.262, 'DriftPass'); % +0.262= sb(701.741)
pm1g4c26b = drift('BPM', 0.0, 'DriftPass'); %s= 701.741 + 0.0
D_1049_qm1g4c26b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(701.829)
qm1g4c26b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 701.829 + 0.25
D_1050_cm1g4c26b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(702.188)
cm1g4c26b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 702.188 + 0.3
D_1051_b1g5c26b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(703.054)
b1g5c26b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 703.054 + 2.62
D_1052_ql3g6c26b = drift('DRIFT', 0.587, 'DriftPass'); % +0.587= sb(706.261)
ql3g6c26b = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 706.261 + 0.275
D_1053_pl2g6c26b = drift('DRIFT', 0.075, 'DriftPass'); % +0.075= sb(706.611)
pl2g6c26b = drift('BPM', 0.0, 'DriftPass'); %s= 706.611 + 0.0
D_1054_sl3g6c26b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(706.699)
sl3g6c26b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 706.699 + 0.2
D_1055_cl2g6c26b = drift('DRIFT', 0.157, 'DriftPass'); % +0.157= sb(707.056)
cl2g6c26b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 707.056 + 0.2
D_1056_ql2g6c26b = drift('DRIFT', 0.208, 'DriftPass'); % +0.208= sb(707.464)
ql2g6c26b = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 707.464 + 0.448
D_1057_sl2g6c26b = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(708.162)
sl2g6c26b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 708.162 + 0.2
D_1058_cl1g6c26b = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(708.493)
cl1g6c26b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 708.493 + 0.2
D_1059_ql1g6c26b = drift('DRIFT', 0.132, 'DriftPass'); % +0.132= sb(708.825)
ql1g6c26b = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 708.825 + 0.275
D_1060_pl1g6c26b = drift('DRIFT', 0.0749999999999, 'DriftPass'); % +0.0749999999999= sb(709.175)
pl1g6c26b = drift('BPM', 0.0, 'DriftPass'); %s= 709.175 + 0.0
D_1061_sl1g6c26b = drift('DRIFT', 0.087, 'DriftPass'); % +0.087= sb(709.262)
sl1g6c26b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 709.262 + 0.2
D_1062_fl1g1c27a = drift('DRIFT', 0.447, 'DriftPass'); % +0.447= sb(709.909)
fl1g1c27a = drift('FCOR', 0.044, 'DriftPass'); %s= 709.909 + 0.044
D_1063_fl2g1c27a = drift('DRIFT', 5.753, 'DriftPass'); % +5.753= sb(715.706)
fl2g1c27a = drift('FCOR', 0.044, 'DriftPass'); %s= 715.706 + 0.044
D_1064_sl1g2c27a = drift('DRIFT', 0.312, 'DriftPass'); % +0.312= sb(716.062)
sl1g2c27a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 716.062 + 0.2
D_1065_pl1g2c27a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(716.352)
pl1g2c27a = drift('BPM', 0.0, 'DriftPass'); %s= 716.352 + 0.0
D_1066_ql1g2c27a = drift('DRIFT', 0.0730000000001, 'DriftPass'); % +0.0730000000001= sb(716.425)
ql1g2c27a = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 716.425 + 0.275
D_1067_cl1g2c27a = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(716.831)
cl1g2c27a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 716.831 + 0.2
D_1068_sl2g2c27a = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(717.162)
sl2g2c27a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 717.162 + 0.2
D_1069_ql2g2c27a = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(717.612)
ql2g2c27a = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 717.612 + 0.448
D_1070_cl2g2c27a = drift('DRIFT', 0.208, 'DriftPass'); % +0.208= sb(718.268)
cl2g2c27a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 718.268 + 0.2
D_1071_sl3g2c27a = drift('DRIFT', 0.158, 'DriftPass'); % +0.158= sb(718.626)
sl3g2c27a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 718.626 + 0.2
D_1072_pl2g2c27a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(718.916)
pl2g2c27a = drift('BPM', 0.0, 'DriftPass'); %s= 718.916 + 0.0
D_1073_ql3g2c27a = drift('DRIFT', 0.072, 'DriftPass'); % +0.072= sb(718.988)
ql3g2c27a = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 718.988 + 0.275
D_1074_b1g3c27a = drift('DRIFT', 0.588, 'DriftPass'); % +0.588= sb(719.851)
b1g3c27a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 719.851 + 2.62
D_1075_cm1g4c27a = drift('DRIFT', 0.601, 'DriftPass'); % +0.601= sb(723.072)
cm1g4c27a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 723.072 + 0.0
sqmhg4c27a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 723.072 + 0.1
D_1077_qm1g4c27a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(723.446)
qm1g4c27a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 723.446 + 0.25
D_1078_sm1g4c27a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(723.896)
sm1g4c27a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 723.896 + 0.2
D_1079_fm1g4c27a = drift('DRIFT', 0.233, 'DriftPass'); % +0.233= sb(724.329)
fm1g4c27a = drift('FCOR', 0.044, 'DriftPass'); %s= 724.329 + 0.044
D_1080_pm1g4c27a = drift('DRIFT', 0.292, 'DriftPass'); % +0.292= sb(724.665)
pm1g4c27a = drift('BPM', 0.0, 'DriftPass'); %s= 724.665 + 0.0
D_1081_qm2g4c27a = drift('DRIFT', 0.0840000000001, 'DriftPass'); % +0.0840000000001= sb(724.749)
qm2g4c27a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 724.749 + 0.283
D_1082_sm2g4c27b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(725.216)
sm2g4c27b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 725.216 + 0.25
D_1083_qm2g4c27b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(725.649)
qm2g4c27b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 725.649 + 0.283
D_1084_sm1g4c27b = drift('DRIFT', 0.504, 'DriftPass'); % +0.504= sb(726.436)
sm1g4c27b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 726.436 + 0.2
D_1085_pm1g4c27b = drift('DRIFT', 0.262, 'DriftPass'); % +0.262= sb(726.898)
pm1g4c27b = drift('BPM', 0.0, 'DriftPass'); %s= 726.898 + 0.0
D_1086_qm1g4c27b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(726.986)
qm1g4c27b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 726.986 + 0.25
D_1087_cm1g4c27b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(727.345)
cm1g4c27b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 727.345 + 0.3
D_1088_b1g5c27b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(728.211)
b1g5c27b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 728.211 + 2.62
D_1089_ch2g6c27b = drift('DRIFT', 0.216, 'DriftPass'); % +0.216= sb(731.047)
ch2g6c27b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 731.047 + 0.3
D_1090_sh4g6c27b = drift('DRIFT', 0.064, 'DriftPass'); % +0.064= sb(731.411)
sh4g6c27b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 731.411 + 0.2
D_1091_ph2g6c27b = drift('DRIFT', 0.0890000000001, 'DriftPass'); % +0.0890000000001= sb(731.7)
ph2g6c27b = drift('BPM', 0.0, 'DriftPass'); %s= 731.7 + 0.0
D_1092_qh3g6c27b = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(731.773)
qh3g6c27b = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 731.773 + 0.275
D_1093_sh3g6c27b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(732.231)
sh3g6c27b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 732.231 + 0.2
D_1094_qh2g6c27b = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(732.621)
qh2g6c27b = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 732.621 + 0.448
D_1095_ch1g6c27b = drift('DRIFT', 0.484, 'DriftPass'); % +0.484= sb(733.553)
ch1g6c27b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 733.553 + 0.2
D_1096_qh1g6c27b = drift('DRIFT', 0.12, 'DriftPass'); % +0.12= sb(733.873)
qh1g6c27b = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 733.873 + 0.275
D_1097_ph1g6c27b = drift('DRIFT', 0.077, 'DriftPass'); % +0.077= sb(734.225)
ph1g6c27b = drift('BPM', 0.0, 'DriftPass'); %s= 734.225 + 0.0
D_1098_sh1g6c27b = drift('DRIFT', 0.0859999999999, 'DriftPass'); % +0.0859999999999= sb(734.311)
sh1g6c27b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 734.311 + 0.2
D_1099_fh1g1c28a = drift('DRIFT', 0.441, 'DriftPass'); % +0.441= sb(734.952)
fh1g1c28a = drift('FCOR', 0.044, 'DriftPass'); %s= 734.952 + 0.044
D_1100_pu1g1c28a = drift('DRIFT', 0.503, 'DriftPass'); % +0.503= sb(735.499)
pu1g1c28a = drift('UBPM', 0.0, 'DriftPass'); %s= 735.499 + 0.0
D_1101_cu1g1c28id1 = drift('DRIFT', 0.071, 'DriftPass'); % +0.071= sb(735.57)
cu1g1c28id1 = drift('IDCOR', 0.0, 'DriftPass'); %s= 735.57 + 0.0
cs1g1c28id1 = drift('IDSIMCOR', 0.0, 'DriftPass'); %s= 735.57 + 0.0
dw100g1c28u = drift('INSERTION', 3.4, 'DriftPass'); %s= 735.57 + 3.4
cu2g1c28id1 = drift('IDCOR', 0.0, 'DriftPass'); %s= 738.97 + 0.0
cs2g1c28id1 = drift('IDSIMCOR', 0.0, 'DriftPass'); %s= 738.97 + 0.0
D_1106_cu1g1c28id2 = drift('DRIFT', 0.381, 'DriftPass'); % +0.381= sb(739.351)
cu1g1c28id2 = drift('IDCOR', 0.0, 'DriftPass'); %s= 739.351 + 0.0
cs1g1c28id2 = drift('IDSIMCOR', 0.0, 'DriftPass'); %s= 739.351 + 0.0
dw100g1c28d = drift('INSERTION', 3.4, 'DriftPass'); %s= 739.351 + 3.4
cu2g1c28id2 = drift('IDCOR', 0.0, 'DriftPass'); %s= 742.751 + 0.0
cs2g1c28id2 = drift('IDSIMCOR', 0.0, 'DriftPass'); %s= 742.751 + 0.0
D_1111_pu4g1c28a = drift('DRIFT', 0.0880000000001, 'DriftPass'); % +0.0880000000001= sb(742.839)
pu4g1c28a = drift('UBPM', 0.0, 'DriftPass'); %s= 742.839 + 0.0
D_1112_fh2g1c28a = drift('DRIFT', 0.616, 'DriftPass'); % +0.616= sb(743.455)
fh2g1c28a = drift('FCOR', 0.044, 'DriftPass'); %s= 743.455 + 0.044
D_1113_sh1g2c28a = drift('DRIFT', 0.312, 'DriftPass'); % +0.312= sb(743.811)
sh1g2c28a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 743.811 + 0.2
D_1114_ph1g2c28a = drift('DRIFT', 0.085, 'DriftPass'); % +0.085= sb(744.096)
ph1g2c28a = drift('BPM', 0.0, 'DriftPass'); %s= 744.096 + 0.0
D_1115_qh1g2c28a = drift('DRIFT', 0.077, 'DriftPass'); % +0.077= sb(744.173)
qh1g2c28a = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 744.173 + 0.275
D_1116_ch1g2c28a = drift('DRIFT', 0.245, 'DriftPass'); % +0.245= sb(744.693)
ch1g2c28a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 744.693 + 0.0
sqhhg2c28a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 744.693 + 0.1
D_1118_qh2g2c28a = drift('DRIFT', 0.46, 'DriftPass'); % +0.46= sb(745.253)
qh2g2c28a = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 745.253 + 0.448
D_1119_sh3g2c28a = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(745.891)
sh3g2c28a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 745.891 + 0.2
D_1120_qh3g2c28a = drift('DRIFT', 0.182, 'DriftPass'); % +0.182= sb(746.273)
qh3g2c28a = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 746.273 + 0.275
D_1121_ph2g2c28a = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(746.621)
ph2g2c28a = drift('BPM', 0.0, 'DriftPass'); %s= 746.621 + 0.0
D_1122_sh4g2c28a = drift('DRIFT', 0.0899999999999, 'DriftPass'); % +0.0899999999999= sb(746.711)
sh4g2c28a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 746.711 + 0.2
D_1123_ch2g2c28a = drift('DRIFT', 0.248, 'DriftPass'); % +0.248= sb(747.159)
ch2g2c28a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 747.159 + 0.3
D_1124_b1g3c28a = drift('DRIFT', 0.032, 'DriftPass'); % +0.032= sb(747.491)
b1g3c28a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 747.491 + 2.62
D_1125_cm1g4c28a = drift('DRIFT', 0.501, 'DriftPass'); % +0.501= sb(750.612)
cm1g4c28a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 750.612 + 0.2
D_1126_qm1g4c28a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(751.086)
qm1g4c28a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 751.086 + 0.25
D_1127_sm1g4c28a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(751.536)
sm1g4c28a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 751.536 + 0.2
D_1128_fm1g4c28a = drift('DRIFT', 0.233, 'DriftPass'); % +0.233= sb(751.969)
fm1g4c28a = drift('FCOR', 0.044, 'DriftPass'); %s= 751.969 + 0.044
D_1129_pm1g4c28a = drift('DRIFT', 0.292, 'DriftPass'); % +0.292= sb(752.305)
pm1g4c28a = drift('BPM', 0.0, 'DriftPass'); %s= 752.305 + 0.0
D_1130_qm2g4c28a = drift('DRIFT', 0.0840000000001, 'DriftPass'); % +0.0840000000001= sb(752.389)
qm2g4c28a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 752.389 + 0.283
D_1131_sm2g4c28b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(752.856)
sm2g4c28b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 752.856 + 0.25
D_1132_qm2g4c28b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(753.289)
qm2g4c28b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 753.289 + 0.283
D_1133_sm1g4c28b = drift('DRIFT', 0.504, 'DriftPass'); % +0.504= sb(754.076)
sm1g4c28b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 754.076 + 0.2
D_1134_pm1g4c28b = drift('DRIFT', 0.262, 'DriftPass'); % +0.262= sb(754.538)
pm1g4c28b = drift('BPM', 0.0, 'DriftPass'); %s= 754.538 + 0.0
D_1135_qm1g4c28b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(754.626)
qm1g4c28b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 754.626 + 0.25
D_1136_cm1g4c28b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(754.985)
cm1g4c28b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 754.985 + 0.3
D_1137_b1g5c28b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(755.851)
b1g5c28b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 755.851 + 2.62
D_1138_ql3g6c28b = drift('DRIFT', 0.587, 'DriftPass'); % +0.587= sb(759.058)
ql3g6c28b = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 759.058 + 0.275
D_1139_pl2g6c28b = drift('DRIFT', 0.075, 'DriftPass'); % +0.075= sb(759.408)
pl2g6c28b = drift('BPM', 0.0, 'DriftPass'); %s= 759.408 + 0.0
D_1140_sl3g6c28b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(759.496)
sl3g6c28b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 759.496 + 0.2
D_1141_cl2g6c28b = drift('DRIFT', 0.157, 'DriftPass'); % +0.157= sb(759.853)
cl2g6c28b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 759.853 + 0.2
D_1142_ql2g6c28b = drift('DRIFT', 0.208, 'DriftPass'); % +0.208= sb(760.261)
ql2g6c28b = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 760.261 + 0.448
D_1143_sl2g6c28b = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(760.959)
sl2g6c28b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 760.959 + 0.2
D_1144_cl1g6c28b = drift('DRIFT', 0.132, 'DriftPass'); % +0.132= sb(761.291)
cl1g6c28b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 761.291 + 0.2
D_1145_ql1g6c28b = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(761.622)
ql1g6c28b = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 761.622 + 0.275
D_1146_pl1g6c28b = drift('DRIFT', 0.0749999999999, 'DriftPass'); % +0.0749999999999= sb(761.972)
pl1g6c28b = drift('BPM', 0.0, 'DriftPass'); %s= 761.972 + 0.0
D_1147_sl1g6c28b = drift('DRIFT', 0.087, 'DriftPass'); % +0.087= sb(762.059)
sl1g6c28b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 762.059 + 0.2
D_1148_fl1g1c29a = drift('DRIFT', 0.447, 'DriftPass'); % +0.447= sb(762.706)
fl1g1c29a = drift('FCOR', 0.044, 'DriftPass'); %s= 762.706 + 0.044
D_1149_fl2g1c29a = drift('DRIFT', 5.753, 'DriftPass'); % +5.753= sb(768.503)
fl2g1c29a = drift('FCOR', 0.044, 'DriftPass'); %s= 768.503 + 0.044
D_1150_sl1g2c29a = drift('DRIFT', 0.312, 'DriftPass'); % +0.312= sb(768.859)
sl1g2c29a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 768.859 + 0.2
D_1151_pl1g2c29a = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(769.149)
pl1g2c29a = drift('BPM', 0.0, 'DriftPass'); %s= 769.149 + 0.0
D_1152_ql1g2c29a = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(769.222)
ql1g2c29a = quadrupole('QL1', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 769.222 + 0.275
D_1153_cl1g2c29a = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(769.628)
cl1g2c29a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 769.628 + 0.2
D_1154_sl2g2c29a = drift('DRIFT', 0.131, 'DriftPass'); % +0.131= sb(769.959)
sl2g2c29a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 769.959 + 0.2
D_1155_ql2g2c29a = drift('DRIFT', 0.25, 'DriftPass'); % +0.25= sb(770.409)
ql2g2c29a = quadrupole('QL2', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 770.409 + 0.448
D_1156_cl2g2c29a = drift('DRIFT', 0.209, 'DriftPass'); % +0.209= sb(771.066)
cl2g2c29a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 771.066 + 0.2
D_1157_sl3g2c29a = drift('DRIFT', 0.157, 'DriftPass'); % +0.157= sb(771.423)
sl3g2c29a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 771.423 + 0.2
D_1158_pl2g2c29a = drift('DRIFT', 0.0899999999999, 'DriftPass'); % +0.0899999999999= sb(771.713)
pl2g2c29a = drift('BPM', 0.0, 'DriftPass'); %s= 771.713 + 0.0
D_1159_ql3g2c29a = drift('DRIFT', 0.0730000000001, 'DriftPass'); % +0.0730000000001= sb(771.786)
ql3g2c29a = quadrupole('QL3', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 771.786 + 0.275
D_1160_b1g3c29a = drift('DRIFT', 0.587, 'DriftPass'); % +0.587= sb(772.648)
b1g3c29a = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 772.648 + 2.62
D_1161_cm1g4c29a = drift('DRIFT', 0.601, 'DriftPass'); % +0.601= sb(775.869)
cm1g4c29a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 775.869 + 0.0
sqmhg4c29a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 775.869 + 0.1
D_1163_qm1g4c29a = drift('DRIFT', 0.274, 'DriftPass'); % +0.274= sb(776.243)
qm1g4c29a = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 776.243 + 0.25
D_1164_sm1g4c29a = drift('DRIFT', 0.2, 'DriftPass'); % +0.2= sb(776.693)
sm1g4c29a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 776.693 + 0.2
D_1165_fm1g4c29a = drift('DRIFT', 0.233, 'DriftPass'); % +0.233= sb(777.126)
fm1g4c29a = drift('FCOR', 0.044, 'DriftPass'); %s= 777.126 + 0.044
D_1166_pm1g4c29a = drift('DRIFT', 0.293, 'DriftPass'); % +0.293= sb(777.463)
pm1g4c29a = drift('BPM', 0.0, 'DriftPass'); %s= 777.463 + 0.0
D_1167_qm2g4c29a = drift('DRIFT', 0.0840000000001, 'DriftPass'); % +0.0840000000001= sb(777.547)
qm2g4c29a = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 777.547 + 0.283
D_1168_sm2g4c29b = drift('DRIFT', 0.183, 'DriftPass'); % +0.183= sb(778.013)
sm2g4c29b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 778.013 + 0.25
D_1169_qm2g4c29b = drift('DRIFT', 0.184, 'DriftPass'); % +0.184= sb(778.447)
qm2g4c29b = quadrupole('QM2', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 778.447 + 0.283
D_1170_sm1g4c29b = drift('DRIFT', 0.503, 'DriftPass'); % +0.503= sb(779.233)
sm1g4c29b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 779.233 + 0.2
D_1171_pm1g4c29b = drift('DRIFT', 0.262, 'DriftPass'); % +0.262= sb(779.695)
pm1g4c29b = drift('BPM', 0.0, 'DriftPass'); %s= 779.695 + 0.0
D_1172_qm1g4c29b = drift('DRIFT', 0.088, 'DriftPass'); % +0.088= sb(779.783)
qm1g4c29b = quadrupole('QM1', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 779.783 + 0.25
D_1173_cm1g4c29b = drift('DRIFT', 0.109, 'DriftPass'); % +0.109= sb(780.142)
cm1g4c29b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 780.142 + 0.3
D_1174_b1g5c29b = drift('DRIFT', 0.566, 'DriftPass'); % +0.566= sb(781.008)
b1g5c29b = rbend('BEND', 2.62, 0.10471975512, 0.0523598775598, 0.0523598775598, 0, 'BndMPoleSymplectic4RadPass'); %s= 781.008 + 2.62
D_1175_ch2g6c29b = drift('DRIFT', 0.216, 'DriftPass'); % +0.216= sb(783.844)
ch2g6c29b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 783.844 + 0.3
D_1176_sh4g6c29b = drift('DRIFT', 0.064, 'DriftPass'); % +0.064= sb(784.208)
sh4g6c29b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 784.208 + 0.2
D_1177_ph2g6c29b = drift('DRIFT', 0.09, 'DriftPass'); % +0.09= sb(784.498)
ph2g6c29b = drift('BPM', 0.0, 'DriftPass'); %s= 784.498 + 0.0
D_1178_qh3g6c29b = drift('DRIFT', 0.073, 'DriftPass'); % +0.073= sb(784.571)
qh3g6c29b = quadrupole('QH3', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 784.571 + 0.275
D_1179_sh3g6c29b = drift('DRIFT', 0.182, 'DriftPass'); % +0.182= sb(785.028)
sh3g6c29b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 785.028 + 0.2
D_1180_qh2g6c29b = drift('DRIFT', 0.19, 'DriftPass'); % +0.19= sb(785.418)
qh2g6c29b = quadrupole('QH2', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 785.418 + 0.448
D_1181_ch1g6c29b = drift('DRIFT', 0.485, 'DriftPass'); % +0.485= sb(786.351)
ch1g6c29b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 786.351 + 0.2
D_1182_qh1g6c29b = drift('DRIFT', 0.12, 'DriftPass'); % +0.12= sb(786.671)
qh1g6c29b = quadrupole('QH1', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 786.671 + 0.275
D_1183_ph1g6c29b = drift('DRIFT', 0.077, 'DriftPass'); % +0.077= sb(787.023)
ph1g6c29b = drift('BPM', 0.0, 'DriftPass'); %s= 787.023 + 0.0
D_1184_sh1g6c29b = drift('DRIFT', 0.0849999999999, 'DriftPass'); % +0.0849999999999= sb(787.108)
sh1g6c29b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 787.108 + 0.2
D_1185_fh1g1c30a = drift('DRIFT', 0.441, 'DriftPass'); % +0.441= sb(787.749)
fh1g1c30a = drift('FCOR', 0.044, 'DriftPass'); %s= 787.749 + 0.044
D_1186_TAIL = drift('DRIFT', 4.165, 'DriftPass'); % C=791.958
LV2SR= [ D_0_fh2g1c30a fh2g1c30a D_1_sh1g2c30a sh1g2c30a D_2_ph1g2c30a ph1g2c30a D_3_qh1g2c30a qh1g2c30a D_4_ch1g2c30a ch1g2c30a ...
     D_5_sqhhg2c30a sqhhg2c30a D_6_qh2g2c30a qh2g2c30a ...
     D_7_sh3g2c30a sh3g2c30a D_8_qh3g2c30a qh3g2c30a ...
     D_9_ph2g2c30a ph2g2c30a D_10_sh4g2c30a sh4g2c30a ...
     D_11_ch2g2c30a ch2g2c30a D_12_b1g3c30a b1g3c30a ...
     D_13_cm1g4c30a cm1g4c30a D_14_qm1g4c30a qm1g4c30a ...
     D_15_sm1g4c30a sm1g4c30a D_16_fm1g4c30a fm1g4c30a ...
     D_17_pm1g4c30a pm1g4c30a D_18_qm2g4c30a qm2g4c30a ...
     D_19_sm2g4c30b sm2g4c30b D_20_qm2g4c30b qm2g4c30b ...
     D_21_sm1g4c30b sm1g4c30b D_22_pm1g4c30b pm1g4c30b ...
     D_23_qm1g4c30b qm1g4c30b D_24_cm1g4c30b cm1g4c30b ...
     D_25_b1g5c30b b1g5c30b D_26_ql3g6c30b ql3g6c30b ...
     D_27_pl2g6c30b pl2g6c30b D_28_sl3g6c30b sl3g6c30b ...
     D_29_cl2g6c30b cl2g6c30b D_30_ql2g6c30b ql2g6c30b ...
     D_31_sl2g6c30b sl2g6c30b D_32_cl1g6c30b cl1g6c30b ...
     D_33_ql1g6c30b ql1g6c30b D_34_pl1g6c30b pl1g6c30b ...
     D_35_sl1g6c30b sl1g6c30b D_36_fl1g1c01a fl1g1c01a ...
     D_37_fl2g1c01a fl2g1c01a D_38_sl1g2c01a sl1g2c01a ...
     D_39_pl1g2c01a pl1g2c01a D_40_ql1g2c01a ql1g2c01a ...
     D_41_cl1g2c01a cl1g2c01a D_42_sl2g2c01a sl2g2c01a ...
     D_43_ql2g2c01a ql2g2c01a D_44_cl2g2c01a cl2g2c01a ...
     D_45_sl3g2c01a sl3g2c01a D_46_pl2g2c01a pl2g2c01a ...
     D_47_ql3g2c01a ql3g2c01a D_48_b1g3c01a b1g3c01a ...
     D_49_cm1g4c01a cm1g4c01a sqmhg4c01a D_51_qm1g4c01a qm1g4c01a D_52_sm1g4c01a sm1g4c01a D_53_fm1g4c01a fm1g4c01a ...
     D_54_pm1g4c01a pm1g4c01a D_55_qm2g4c01a qm2g4c01a ...
     D_56_sm2g4c01b sm2g4c01b D_57_qm2g4c01b qm2g4c01b ...
     D_58_sm1g4c01b sm1g4c01b D_59_pm1g4c01b pm1g4c01b ...
     D_60_qm1g4c01b qm1g4c01b D_61_cm1g4c01b cm1g4c01b ...
     D_62_b1g5c01b b1g5c01b D_63_ch2g6c01b ch2g6c01b ...
     D_64_sh4g6c01b sh4g6c01b D_65_ph2g6c01b ph2g6c01b ...
     D_66_qh3g6c01b qh3g6c01b D_67_sh3g6c01b sh3g6c01b ...
     D_68_qh2g6c01b qh2g6c01b D_69_ch1g6c01b ch1g6c01b ...
     D_70_qh1g6c01b qh1g6c01b D_71_ph1g6c01b ph1g6c01b ...
     D_72_sh1g6c01b sh1g6c01b D_73_fh1g1c02a fh1g1c02a ...
     D_74_fh2g1c02a fh2g1c02a D_75_sh1g2c02a sh1g2c02a ...
     D_76_ph1g2c02a ph1g2c02a D_77_qh1g2c02a qh1g2c02a ...
     D_78_ch1g2c02a ch1g2c02a sqhhg2c02a D_80_qh2g2c02a qh2g2c02a D_81_sh3g2c02a sh3g2c02a D_82_qh3g2c02a qh3g2c02a ...
     D_83_ph2g2c02a ph2g2c02a D_84_sh4g2c02a sh4g2c02a ...
     D_85_ch2g2c02a ch2g2c02a D_86_b1g3c02a b1g3c02a ...
     D_87_cm1g4c02a cm1g4c02a D_88_qm1g4c02a qm1g4c02a ...
     D_89_sm1g4c02a sm1g4c02a D_90_fm1g4c02a fm1g4c02a ...
     D_91_pm1g4c02a pm1g4c02a D_92_qm2g4c02a qm2g4c02a ...
     D_93_sm2g4c02b sm2g4c02b D_94_qm2g4c02b qm2g4c02b ...
     D_95_sm1g4c02b sm1g4c02b D_96_pm1g4c02b pm1g4c02b ...
     D_97_qm1g4c02b qm1g4c02b D_98_cm1g4c02b cm1g4c02b ...
     D_99_b1g5c02b b1g5c02b D_100_ql3g6c02b ql3g6c02b ...
     D_101_pl2g6c02b pl2g6c02b D_102_sl3g6c02b sl3g6c02b ...
     D_103_cl2g6c02b cl2g6c02b D_104_ql2g6c02b ql2g6c02b ...
     D_105_sl2g6c02b sl2g6c02b D_106_cl1g6c02b cl1g6c02b ...
     D_107_ql1g6c02b ql1g6c02b D_108_pl1g6c02b pl1g6c02b ...
     D_109_sl1g6c02b sl1g6c02b D_110_fl1g1c03a fl1g1c03a ...
     D_111_pu1g1c03a pu1g1c03a D_112_cu1g1c03id1 cu1g1c03id1 ...
     cs1g1c03id1 ivu20g1c03c cu2g1c03id2 cs2g1c03id2 ...
     D_117_pu4g1c03a pu4g1c03a D_118_fl2g1c03a fl2g1c03a ...
     D_119_sl1g2c03a sl1g2c03a D_120_pl1g2c03a pl1g2c03a ...
     D_121_ql1g2c03a ql1g2c03a D_122_cl1g2c03a cl1g2c03a ...
     D_123_sl2g2c03a sl2g2c03a D_124_ql2g2c03a ql2g2c03a ...
     D_125_cl2g2c03a cl2g2c03a D_126_sl3g2c03a sl3g2c03a ...
     D_127_pl2g2c03a pl2g2c03a D_128_ql3g2c03a ql3g2c03a ...
     D_129_b2g3c03a b2g3c03a D_130_cm1g4c03a cm1g4c03a ...
     D_131_sqmhg4c03a sqmhg4c03a D_132_qm1g4c03a qm1g4c03a ...
     D_133_sm1g4c03a sm1g4c03a D_134_fm1g4c03a fm1g4c03a ...
     D_135_pm1g4c03a pm1g4c03a D_136_qm2g4c03a qm2g4c03a ...
     D_137_sm2g4c03b sm2g4c03b D_138_qm2g4c03b qm2g4c03b ...
     D_139_sm1g4c03b sm1g4c03b D_140_pm1g4c03b pm1g4c03b ...
     D_141_qm1g4c03b qm1g4c03b D_142_cm1g4c03b cm1g4c03b ...
     D_143_b2g5c03b b2g5c03b D_144_ch2g6c03b ch2g6c03b ...
     D_145_sh4g6c03b sh4g6c03b D_146_ph2g6c03b ph2g6c03b ...
     D_147_qh3g6c03b qh3g6c03b D_148_sh3g6c03b sh3g6c03b ...
     D_149_qh2g6c03b qh2g6c03b D_150_ch1g6c03b ch1g6c03b ...
     D_151_qh1g6c03b qh1g6c03b D_152_ph1g6c03b ph1g6c03b ...
     D_153_sh1g6c03b sh1g6c03b D_154_fh1g1c04a fh1g1c04a ...
     D_155_fh2g1c04a fh2g1c04a D_156_sh1g2c04a sh1g2c04a ...
     D_157_ph1g2c04a ph1g2c04a D_158_qh1g2c04a qh1g2c04a ...
     D_159_ch1g2c04a ch1g2c04a D_160_sqhhg2c04a sqhhg2c04a ...
     D_161_qh2g2c04a qh2g2c04a D_162_sh3g2c04a sh3g2c04a ...
     D_163_qh3g2c04a qh3g2c04a D_164_ph2g2c04a ph2g2c04a ...
     D_165_sh4g2c04a sh4g2c04a D_166_ch2g2c04a ch2g2c04a ...
     D_167_b1g3c04a b1g3c04a D_168_cm1g4c04a cm1g4c04a ...
     D_169_qm1g4c04a qm1g4c04a D_170_sm1g4c04a sm1g4c04a ...
     D_171_fm1g4c04a fm1g4c04a D_172_pm1g4c04a pm1g4c04a ...
     D_173_qm2g4c04a qm2g4c04a D_174_sm2g4c04b sm2g4c04b ...
     D_175_qm2g4c04b qm2g4c04b D_176_sm1g4c04b sm1g4c04b ...
     D_177_pm1g4c04b pm1g4c04b D_178_qm1g4c04b qm1g4c04b ...
     D_179_cm1g4c04b cm1g4c04b D_180_b1g5c04b b1g5c04b ...
     D_181_ql3g6c04b ql3g6c04b D_182_pl2g6c04b pl2g6c04b ...
     D_183_sl3g6c04b sl3g6c04b D_184_cl2g6c04b cl2g6c04b ...
     D_185_ql2g6c04b ql2g6c04b D_186_sl2g6c04b sl2g6c04b ...
     D_187_cl1g6c04b cl1g6c04b D_188_ql1g6c04b ql1g6c04b ...
     D_189_pl1g6c04b pl1g6c04b D_190_sl1g6c04b sl1g6c04b ...
     D_191_fl1g1c05a fl1g1c05a D_192_pu1g1c05a pu1g1c05a ...
     D_193_pu2g1c05a pu2g1c05a D_194_cu1g1c05id2 cu1g1c05id2 ...
     cs1g1c05id2 ivu21g1c05d cu2g1c05id2 cs2g1c05id2 ...
     D_199_pu4g1c05a pu4g1c05a D_200_fl2g1c05a fl2g1c05a ...
     D_201_sl1g2c05a sl1g2c05a D_202_pl1g2c05a pl1g2c05a ...
     D_203_ql1g2c05a ql1g2c05a D_204_cl1g2c05a cl1g2c05a ...
     D_205_sl2g2c05a sl2g2c05a D_206_ql2g2c05a ql2g2c05a ...
     D_207_cl2g2c05a cl2g2c05a D_208_sl3g2c05a sl3g2c05a ...
     D_209_pl2g2c05a pl2g2c05a D_210_ql3g2c05a ql3g2c05a ...
     D_211_b1g3c05a b1g3c05a D_212_cm1g4c05a cm1g4c05a ...
     sqmhg4c05a D_214_qm1g4c05a qm1g4c05a D_215_sm1g4c05a sm1g4c05a D_216_fm1g4c05a fm1g4c05a D_217_pm1g4c05a pm1g4c05a ...
     D_218_qm2g4c05a qm2g4c05a D_219_sm2g4c05b sm2g4c05b ...
     D_220_qm2g4c05b qm2g4c05b D_221_sm1g4c05b sm1g4c05b ...
     D_222_pm1g4c05b pm1g4c05b D_223_qm1g4c05b qm1g4c05b ...
     D_224_cm1g4c05b cm1g4c05b D_225_b1g5c05b b1g5c05b ...
     D_226_ch2g6c05b ch2g6c05b D_227_sh4g6c05b sh4g6c05b ...
     D_228_ph2g6c05b ph2g6c05b D_229_qh3g6c05b qh3g6c05b ...
     D_230_sh3g6c05b sh3g6c05b D_231_qh2g6c05b qh2g6c05b ...
     D_232_ch1g6c05b ch1g6c05b D_233_qh1g6c05b qh1g6c05b ...
     D_234_ph1g6c05b ph1g6c05b D_235_sh1g6c05b sh1g6c05b ...
     D_236_fh1g1c06a fh1g1c06a D_237_fh2g1c06a fh2g1c06a ...
     D_238_sh1g2c06a sh1g2c06a D_239_ph1g2c06a ph1g2c06a ...
     D_240_qh1g2c06a qh1g2c06a D_241_ch1g2c06a ch1g2c06a ...
     sqhhg2c06a D_243_qh2g2c06a qh2g2c06a D_244_sh3g2c06a sh3g2c06a D_245_qh3g2c06a qh3g2c06a D_246_ph2g2c06a ph2g2c06a ...
     D_247_sh4g2c06a sh4g2c06a D_248_ch2g2c06a ch2g2c06a ...
     D_249_b1g3c06a b1g3c06a D_250_cm1g4c06a cm1g4c06a ...
     D_251_qm1g4c06a qm1g4c06a D_252_sm1g4c06a sm1g4c06a ...
     D_253_fm1g4c06a fm1g4c06a D_254_pm1g4c06a pm1g4c06a ...
     D_255_qm2g4c06a qm2g4c06a D_256_sm2g4c06b sm2g4c06b ...
     D_257_qm2g4c06b qm2g4c06b D_258_sm1g4c06b sm1g4c06b ...
     D_259_pm1g4c06b pm1g4c06b D_260_qm1g4c06b qm1g4c06b ...
     D_261_cm1g4c06b cm1g4c06b D_262_b1g5c06b b1g5c06b ...
     D_263_ql3g6c06b ql3g6c06b D_264_pl2g6c06b pl2g6c06b ...
     D_265_sl3g6c06b sl3g6c06b D_266_cl2g6c06b cl2g6c06b ...
     D_267_ql2g6c06b ql2g6c06b D_268_sl2g6c06b sl2g6c06b ...
     D_269_cl1g6c06b cl1g6c06b D_270_ql1g6c06b ql1g6c06b ...
     D_271_pl1g6c06b pl1g6c06b D_272_sl1g6c06b sl1g6c06b ...
     D_273_fl1g1c07a fl1g1c07a D_274_fl2g1c07a fl2g1c07a ...
     D_275_sl1g2c07a sl1g2c07a D_276_pl1g2c07a pl1g2c07a ...
     D_277_ql1g2c07a ql1g2c07a D_278_cl1g2c07a cl1g2c07a ...
     D_279_sl2g2c07a sl2g2c07a D_280_ql2g2c07a ql2g2c07a ...
     D_281_cl2g2c07a cl2g2c07a D_282_sl3g2c07a sl3g2c07a ...
     D_283_pl2g2c07a pl2g2c07a D_284_ql3g2c07a ql3g2c07a ...
     D_285_b1g3c07a b1g3c07a D_286_cm1g4c07a cm1g4c07a ...
     sqmhg4c07a D_288_qm1g4c07a qm1g4c07a D_289_sm1g4c07a sm1g4c07a D_290_fm1g4c07a fm1g4c07a D_291_pm1g4c07a pm1g4c07a ...
     D_292_qm2g4c07a qm2g4c07a D_293_sm2g4c07b sm2g4c07b ...
     D_294_qm2g4c07b qm2g4c07b D_295_sm1g4c07b sm1g4c07b ...
     D_296_pm1g4c07b pm1g4c07b D_297_qm1g4c07b qm1g4c07b ...
     D_298_cm1g4c07b cm1g4c07b D_299_b1g5c07b b1g5c07b ...
     D_300_ch2g6c07b ch2g6c07b D_301_sh4g6c07b sh4g6c07b ...
     D_302_ph2g6c07b ph2g6c07b D_303_qh3g6c07b qh3g6c07b ...
     D_304_sh3g6c07b sh3g6c07b D_305_qh2g6c07b qh2g6c07b ...
     D_306_ch1g6c07b ch1g6c07b D_307_qh1g6c07b qh1g6c07b ...
     D_308_ph1g6c07b ph1g6c07b D_309_sh1g6c07b sh1g6c07b ...
     D_310_fh1g1c08a fh1g1c08a D_311_pu1g1c08a pu1g1c08a ...
     D_312_cu1g1c08id1 cu1g1c08id1 cs1g1c08id1 dw100g1c08u ...
     cu2g1c08id1 cs2g1c08id1 D_317_cu1g1c08id2 cu1g1c08id2 ...
     cs1g1c08id2 dw100g1c08d cu2g1c08id2 cs2g1c08id2 ...
     D_322_pu4g1c08a pu4g1c08a D_323_fh2g1c08a fh2g1c08a ...
     D_324_sh1g2c08a sh1g2c08a D_325_ph1g2c08a ph1g2c08a ...
     D_326_qh1g2c08a qh1g2c08a D_327_ch1g2c08a ch1g2c08a ...
     sqhhg2c08a D_329_qh2g2c08a qh2g2c08a D_330_sh3g2c08a sh3g2c08a D_331_qh3g2c08a qh3g2c08a D_332_ph2g2c08a ph2g2c08a ...
     D_333_sh4g2c08a sh4g2c08a D_334_ch2g2c08a ch2g2c08a ...
     D_335_b1g3c08a b1g3c08a D_336_cm1g4c08a cm1g4c08a ...
     D_337_qm1g4c08a qm1g4c08a D_338_sm1g4c08a sm1g4c08a ...
     D_339_fm1g4c08a fm1g4c08a D_340_pm1g4c08a pm1g4c08a ...
     D_341_qm2g4c08a qm2g4c08a D_342_sm2g4c08b sm2g4c08b ...
     D_343_qm2g4c08b qm2g4c08b D_344_sm1g4c08b sm1g4c08b ...
     D_345_pm1g4c08b pm1g4c08b D_346_qm1g4c08b qm1g4c08b ...
     D_347_cm1g4c08b cm1g4c08b D_348_b1g5c08b b1g5c08b ...
     D_349_ql3g6c08b ql3g6c08b D_350_pl2g6c08b pl2g6c08b ...
     D_351_sl3g6c08b sl3g6c08b D_352_cl2g6c08b cl2g6c08b ...
     D_353_ql2g6c08b ql2g6c08b D_354_sl2g6c08b sl2g6c08b ...
     D_355_cl1g6c08b cl1g6c08b D_356_ql1g6c08b ql1g6c08b ...
     D_357_pl1g6c08b pl1g6c08b D_358_sl1g6c08b sl1g6c08b ...
     D_359_fl1g1c09a fl1g1c09a D_360_fl2g1c09a fl2g1c09a ...
     D_361_sl1g2c09a sl1g2c09a D_362_pl1g2c09a pl1g2c09a ...
     D_363_ql1g2c09a ql1g2c09a D_364_cl1g2c09a cl1g2c09a ...
     D_365_sl2g2c09a sl2g2c09a D_366_ql2g2c09a ql2g2c09a ...
     D_367_cl2g2c09a cl2g2c09a D_368_sl3g2c09a sl3g2c09a ...
     D_369_pl2g2c09a pl2g2c09a D_370_ql3g2c09a ql3g2c09a ...
     D_371_b1g3c09a b1g3c09a D_372_cm1g4c09a cm1g4c09a ...
     D_373_sqmhg4c09a sqmhg4c09a D_374_qm1g4c09a qm1g4c09a ...
     D_375_sm1g4c09a sm1g4c09a D_376_fm1g4c09a fm1g4c09a ...
     D_377_pm1g4c09a pm1g4c09a D_378_qm2g4c09a qm2g4c09a ...
     D_379_sm2g4c09b sm2g4c09b D_380_qm2g4c09b qm2g4c09b ...
     D_381_sm1g4c09b sm1g4c09b D_382_pm1g4c09b pm1g4c09b ...
     D_383_qm1g4c09b qm1g4c09b D_384_cm1g4c09b cm1g4c09b ...
     D_385_b1g5c09b b1g5c09b D_386_ch2g6c09b ch2g6c09b ...
     D_387_sh4g6c09b sh4g6c09b D_388_ph2g6c09b ph2g6c09b ...
     D_389_qh3g6c09b qh3g6c09b D_390_sh3g6c09b sh3g6c09b ...
     D_391_qh2g6c09b qh2g6c09b D_392_ch1g6c09b ch1g6c09b ...
     D_393_qh1g6c09b qh1g6c09b D_394_ph1g6c09b ph1g6c09b ...
     D_395_sh1g6c09b sh1g6c09b D_396_fh1g1c10a fh1g1c10a ...
     D_397_pu1g1c10a pu1g1c10a D_398_cu1g1c10id1 cu1g1c10id1 ...
     cs1g1c10id1 ivu22g1c10c cu2g1c10id2 cs2g1c10id2 ...
     D_403_pu4g1c10a pu4g1c10a D_404_fh2g1c10a fh2g1c10a ...
     D_405_sh1g2c10a sh1g2c10a D_406_ph1g2c10a ph1g2c10a ...
     D_407_qh1g2c10a qh1g2c10a D_408_ch1g2c10a ch1g2c10a ...
     sqhhg2c10a D_410_qh2g2c10a qh2g2c10a D_411_sh3g2c10a sh3g2c10a D_412_qh3g2c10a qh3g2c10a D_413_ph2g2c10a ph2g2c10a ...
     D_414_sh4g2c10a sh4g2c10a D_415_ch2g2c10a ch2g2c10a ...
     D_416_b1g3c10a b1g3c10a D_417_cm1g4c10a cm1g4c10a ...
     D_418_qm1g4c10a qm1g4c10a D_419_sm1g4c10a sm1g4c10a ...
     D_420_fm1g4c10a fm1g4c10a D_421_pm1g4c10a pm1g4c10a ...
     D_422_qm2g4c10a qm2g4c10a D_423_sm2g4c10b sm2g4c10b ...
     D_424_qm2g4c10b qm2g4c10b D_425_sm1g4c10b sm1g4c10b ...
     D_426_pm1g4c10b pm1g4c10b D_427_qm1g4c10b qm1g4c10b ...
     D_428_cm1g4c10b cm1g4c10b D_429_b1g5c10b b1g5c10b ...
     D_430_ql3g6c10b ql3g6c10b D_431_pl2g6c10b pl2g6c10b ...
     D_432_sl3g6c10b sl3g6c10b D_433_cl2g6c10b cl2g6c10b ...
     D_434_ql2g6c10b ql2g6c10b D_435_sl2g6c10b sl2g6c10b ...
     D_436_cl1g6c10b cl1g6c10b D_437_ql1g6c10b ql1g6c10b ...
     D_438_pl1g6c10b pl1g6c10b D_439_sl1g6c10b sl1g6c10b ...
     D_440_fl1g1c11a fl1g1c11a D_441_pu1g1c11a pu1g1c11a ...
     D_442_cu1g1c11id1 cu1g1c11id1 cs1g1c11id1 ivu20g1c11c ...
     cu2g1c11id2 cs2g1c11id2 D_447_pu4g1c11a pu4g1c11a ...
     D_448_fl2g1c11a fl2g1c11a D_449_sl1g2c11a sl1g2c11a ...
     D_450_pl1g2c11a pl1g2c11a D_451_ql1g2c11a ql1g2c11a ...
     D_452_cl1g2c11a cl1g2c11a D_453_sl2g2c11a sl2g2c11a ...
     D_454_ql2g2c11a ql2g2c11a D_455_cl2g2c11a cl2g2c11a ...
     D_456_sl3g2c11a sl3g2c11a D_457_pl2g2c11a pl2g2c11a ...
     D_458_ql3g2c11a ql3g2c11a D_459_b1g3c11a b1g3c11a ...
     D_460_cm1g4c11a cm1g4c11a sqmhg4c11a D_462_qm1g4c11a qm1g4c11a D_463_sm1g4c11a sm1g4c11a D_464_fm1g4c11a fm1g4c11a ...
     D_465_pm1g4c11a pm1g4c11a D_466_qm2g4c11a qm2g4c11a ...
     D_467_sm2g4c11b sm2g4c11b D_468_qm2g4c11b qm2g4c11b ...
     D_469_sm1g4c11b sm1g4c11b D_470_pm1g4c11b pm1g4c11b ...
     D_471_qm1g4c11b qm1g4c11b D_472_cm1g4c11b cm1g4c11b ...
     D_473_b1g5c11b b1g5c11b D_474_ch2g6c11b ch2g6c11b ...
     D_475_sh4g6c11b sh4g6c11b D_476_ph2g6c11b ph2g6c11b ...
     D_477_qh3g6c11b qh3g6c11b D_478_sh3g6c11b sh3g6c11b ...
     D_479_qh2g6c11b qh2g6c11b D_480_ch1g6c11b ch1g6c11b ...
     D_481_qh1g6c11b qh1g6c11b D_482_ph1g6c11b ph1g6c11b ...
     D_483_sh1g6c11b sh1g6c11b D_484_fh1g1c12a fh1g1c12a ...
     D_485_fh2g1c12a fh2g1c12a D_486_sh1g2c12a sh1g2c12a ...
     D_487_ph1g2c12a ph1g2c12a D_488_qh1g2c12a qh1g2c12a ...
     D_489_ch1g2c12a ch1g2c12a sqhhg2c12a D_491_qh2g2c12a qh2g2c12a D_492_sh3g2c12a sh3g2c12a D_493_qh3g2c12a qh3g2c12a ...
     D_494_ph2g2c12a ph2g2c12a D_495_sh4g2c12a sh4g2c12a ...
     D_496_ch2g2c12a ch2g2c12a D_497_b1g3c12a b1g3c12a ...
     D_498_cm1g4c12a cm1g4c12a D_499_qm1g4c12a qm1g4c12a ...
     D_500_sm1g4c12a sm1g4c12a D_501_fm1g4c12a fm1g4c12a ...
     D_502_pm1g4c12a pm1g4c12a D_503_qm2g4c12a qm2g4c12a ...
     D_504_sm2g4c12b sm2g4c12b D_505_qm2g4c12b qm2g4c12b ...
     D_506_sm1g4c12b sm1g4c12b D_507_pm1g4c12b pm1g4c12b ...
     D_508_qm1g4c12b qm1g4c12b D_509_cm1g4c12b cm1g4c12b ...
     D_510_b1g5c12b b1g5c12b D_511_ql3g6c12b ql3g6c12b ...
     D_512_pl2g6c12b pl2g6c12b D_513_sl3g6c12b sl3g6c12b ...
     D_514_cl2g6c12b cl2g6c12b D_515_ql2g6c12b ql2g6c12b ...
     D_516_sl2g6c12b sl2g6c12b D_517_cl1g6c12b cl1g6c12b ...
     D_518_ql1g6c12b ql1g6c12b D_519_pl1g6c12b pl1g6c12b ...
     D_520_sl1g6c12b sl1g6c12b D_521_fl1g1c13a fl1g1c13a ...
     D_522_fl2g1c13a fl2g1c13a D_523_sl1g2c13a sl1g2c13a ...
     D_524_pl1g2c13a pl1g2c13a D_525_ql1g2c13a ql1g2c13a ...
     D_526_cl1g2c13a cl1g2c13a D_527_sl2g2c13a sl2g2c13a ...
     D_528_ql2g2c13a ql2g2c13a D_529_cl2g2c13a cl2g2c13a ...
     D_530_sl3g2c13a sl3g2c13a D_531_pl2g2c13a pl2g2c13a ...
     D_532_ql3g2c13a ql3g2c13a D_533_b2g3c13a b2g3c13a ...
     D_534_cm1g4c13a cm1g4c13a sqmhg4c13a D_536_qm1g4c13a qm1g4c13a D_537_sm1g4c13a sm1g4c13a D_538_fm1g4c13a fm1g4c13a ...
     D_539_pm1g4c13a pm1g4c13a D_540_qm2g4c13a qm2g4c13a ...
     D_541_sm2g4c13b sm2g4c13b D_542_qm2g4c13b qm2g4c13b ...
     D_543_sm1g4c13b sm1g4c13b D_544_pm1g4c13b pm1g4c13b ...
     D_545_qm1g4c13b qm1g4c13b D_546_cm1g4c13b cm1g4c13b ...
     D_547_b2g5c13b b2g5c13b D_548_ch2g6c13b ch2g6c13b ...
     D_549_sh4g6c13b sh4g6c13b D_550_ph2g6c13b ph2g6c13b ...
     D_551_qh3g6c13b qh3g6c13b D_552_sh3g6c13b sh3g6c13b ...
     D_553_qh2g6c13b qh2g6c13b D_554_ch1g6c13b ch1g6c13b ...
     D_555_qh1g6c13b qh1g6c13b D_556_ph1g6c13b ph1g6c13b ...
     D_557_sh1g6c13b sh1g6c13b D_558_fh1g1c14a fh1g1c14a ...
     D_559_fh2g1c14a fh2g1c14a D_560_sh1g2c14a sh1g2c14a ...
     D_561_ph1g2c14a ph1g2c14a D_562_qh1g2c14a qh1g2c14a ...
     D_563_ch1g2c14a ch1g2c14a sqhhg2c14a D_565_qh2g2c14a qh2g2c14a D_566_sh3g2c14a sh3g2c14a D_567_qh3g2c14a qh3g2c14a ...
     D_568_ph2g2c14a ph2g2c14a D_569_sh4g2c14a sh4g2c14a ...
     D_570_ch2g2c14a ch2g2c14a D_571_b1g3c14a b1g3c14a ...
     D_572_cm1g4c14a cm1g4c14a D_573_qm1g4c14a qm1g4c14a ...
     D_574_sm1g4c14a sm1g4c14a D_575_fm1g4c14a fm1g4c14a ...
     D_576_pm1g4c14a pm1g4c14a D_577_qm2g4c14a qm2g4c14a ...
     D_578_sm2g4c14b sm2g4c14b D_579_qm2g4c14b qm2g4c14b ...
     D_580_sm1g4c14b sm1g4c14b D_581_pm1g4c14b pm1g4c14b ...
     D_582_qm1g4c14b qm1g4c14b D_583_cm1g4c14b cm1g4c14b ...
     D_584_b1g5c14b b1g5c14b D_585_ql3g6c14b ql3g6c14b ...
     D_586_pl2g6c14b pl2g6c14b D_587_sl3g6c14b sl3g6c14b ...
     D_588_cl2g6c14b cl2g6c14b D_589_ql2g6c14b ql2g6c14b ...
     D_590_sl2g6c14b sl2g6c14b D_591_cl1g6c14b cl1g6c14b ...
     D_592_ql1g6c14b ql1g6c14b D_593_pl1g6c14b pl1g6c14b ...
     D_594_sl1g6c14b sl1g6c14b D_595_fl1g1c15a fl1g1c15a ...
     D_596_fl2g1c15a fl2g1c15a D_597_sl1g2c15a sl1g2c15a ...
     D_598_pl1g2c15a pl1g2c15a D_599_ql1g2c15a ql1g2c15a ...
     D_600_cl1g2c15a cl1g2c15a D_601_sl2g2c15a sl2g2c15a ...
     D_602_ql2g2c15a ql2g2c15a D_603_cl2g2c15a cl2g2c15a ...
     D_604_sl3g2c15a sl3g2c15a D_605_pl2g2c15a pl2g2c15a ...
     D_606_ql3g2c15a ql3g2c15a D_607_b1g3c15a b1g3c15a ...
     D_608_cm1g4c15a cm1g4c15a sqmhg4c15a D_610_qm1g4c15a qm1g4c15a D_611_sm1g4c15a sm1g4c15a D_612_fm1g4c15a fm1g4c15a ...
     D_613_pm1g4c15a pm1g4c15a D_614_qm2g4c15a qm2g4c15a ...
     D_615_sm2g4c15b sm2g4c15b D_616_qm2g4c15b qm2g4c15b ...
     D_617_sm1g4c15b sm1g4c15b D_618_pm1g4c15b pm1g4c15b ...
     D_619_qm1g4c15b qm1g4c15b D_620_cm1g4c15b cm1g4c15b ...
     D_621_b1g5c15b b1g5c15b D_622_ch2g6c15b ch2g6c15b ...
     D_623_sh4g6c15b sh4g6c15b D_624_ph2g6c15b ph2g6c15b ...
     D_625_qh3g6c15b qh3g6c15b D_626_sh3g6c15b sh3g6c15b ...
     D_627_qh2g6c15b qh2g6c15b D_628_ch1g6c15b ch1g6c15b ...
     D_629_qh1g6c15b qh1g6c15b D_630_ph1g6c15b ph1g6c15b ...
     D_631_sh1g6c15b sh1g6c15b D_632_fh1g1c16a fh1g1c16a ...
     D_633_fh2g1c16a fh2g1c16a D_634_sh1g2c16a sh1g2c16a ...
     D_635_ph1g2c16a ph1g2c16a D_636_qh1g2c16a qh1g2c16a ...
     D_637_ch1g2c16a ch1g2c16a sqhhg2c16a D_639_qh2g2c16a qh2g2c16a D_640_sh3g2c16a sh3g2c16a D_641_qh3g2c16a qh3g2c16a ...
     D_642_ph2g2c16a ph2g2c16a D_643_sh4g2c16a sh4g2c16a ...
     D_644_ch2g2c16a ch2g2c16a D_645_b1g3c16a b1g3c16a ...
     D_646_cm1g4c16a cm1g4c16a D_647_qm1g4c16a qm1g4c16a ...
     D_648_sm1g4c16a sm1g4c16a D_649_fm1g4c16a fm1g4c16a ...
     D_650_pm1g4c16a pm1g4c16a D_651_qm2g4c16a qm2g4c16a ...
     D_652_sm2g4c16b sm2g4c16b D_653_qm2g4c16b qm2g4c16b ...
     D_654_sm1g4c16b sm1g4c16b D_655_pm1g4c16b pm1g4c16b ...
     D_656_qm1g4c16b qm1g4c16b D_657_cm1g4c16b cm1g4c16b ...
     D_658_b1g5c16b b1g5c16b D_659_ql3g6c16b ql3g6c16b ...
     D_660_pl2g6c16b pl2g6c16b D_661_sl3g6c16b sl3g6c16b ...
     D_662_cl2g6c16b cl2g6c16b D_663_ql2g6c16b ql2g6c16b ...
     D_664_sl2g6c16b sl2g6c16b D_665_cl1g6c16b cl1g6c16b ...
     D_666_ql1g6c16b ql1g6c16b D_667_pl1g6c16b pl1g6c16b ...
     D_668_sl1g6c16b sl1g6c16b D_669_fl1g1c17a fl1g1c17a ...
     D_670_fl2g1c17a fl2g1c17a D_671_sl1g2c17a sl1g2c17a ...
     D_672_pl1g2c17a pl1g2c17a D_673_ql1g2c17a ql1g2c17a ...
     D_674_cl1g2c17a cl1g2c17a D_675_sl2g2c17a sl2g2c17a ...
     D_676_ql2g2c17a ql2g2c17a D_677_cl2g2c17a cl2g2c17a ...
     D_678_sl3g2c17a sl3g2c17a D_679_pl2g2c17a pl2g2c17a ...
     D_680_ql3g2c17a ql3g2c17a D_681_b1g3c17a b1g3c17a ...
     D_682_cm1g4c17a cm1g4c17a sqmhg4c17a D_684_qm1g4c17a qm1g4c17a D_685_sm1g4c17a sm1g4c17a D_686_fm1g4c17a fm1g4c17a ...
     D_687_pm1g4c17a pm1g4c17a D_688_qm2g4c17a qm2g4c17a ...
     D_689_sm2g4c17b sm2g4c17b D_690_qm2g4c17b qm2g4c17b ...
     D_691_sm1g4c17b sm1g4c17b D_692_pm1g4c17b pm1g4c17b ...
     D_693_qm1g4c17b qm1g4c17b D_694_cm1g4c17b cm1g4c17b ...
     D_695_b1g5c17b b1g5c17b D_696_ch2g6c17b ch2g6c17b ...
     D_697_sh4g6c17b sh4g6c17b D_698_ph2g6c17b ph2g6c17b ...
     D_699_qh3g6c17b qh3g6c17b D_700_sh3g6c17b sh3g6c17b ...
     D_701_qh2g6c17b qh2g6c17b D_702_ch1g6c17b ch1g6c17b ...
     D_703_qh1g6c17b qh1g6c17b D_704_ph1g6c17b ph1g6c17b ...
     D_705_sh1g6c17b sh1g6c17b D_706_fh1g1c18a fh1g1c18a ...
     D_707_pu1g1c18a pu1g1c18a D_708_cu1g1c18id1 cu1g1c18id1 ...
     cs1g1c18id1 dw100g1c18u cu2g1c18id1 cs2g1c18id1 ...
     D_713_cu1g1c18id2 cu1g1c18id2 cs1g1c18id2 dw100g1c18d ...
     cu2g1c18id2 cs2g1c18id2 D_718_pu4g1c18a pu4g1c18a ...
     D_719_fh2g1c18a fh2g1c18a D_720_sh1g2c18a sh1g2c18a ...
     D_721_ph1g2c18a ph1g2c18a D_722_qh1g2c18a qh1g2c18a ...
     D_723_ch1g2c18a ch1g2c18a sqhhg2c18a D_725_qh2g2c18a qh2g2c18a D_726_sh3g2c18a sh3g2c18a D_727_qh3g2c18a qh3g2c18a ...
     D_728_ph2g2c18a ph2g2c18a D_729_sh4g2c18a sh4g2c18a ...
     D_730_ch2g2c18a ch2g2c18a D_731_b1g3c18a b1g3c18a ...
     D_732_cm1g4c18a cm1g4c18a D_733_qm1g4c18a qm1g4c18a ...
     D_734_sm1g4c18a sm1g4c18a D_735_fm1g4c18a fm1g4c18a ...
     D_736_pm1g4c18a pm1g4c18a D_737_qm2g4c18a qm2g4c18a ...
     D_738_sm2g4c18b sm2g4c18b D_739_qm2g4c18b qm2g4c18b ...
     D_740_sm1g4c18b sm1g4c18b D_741_pm1g4c18b pm1g4c18b ...
     D_742_qm1g4c18b qm1g4c18b D_743_cm1g4c18b cm1g4c18b ...
     D_744_b1g5c18b b1g5c18b D_745_ql3g6c18b ql3g6c18b ...
     D_746_pl2g6c18b pl2g6c18b D_747_sl3g6c18b sl3g6c18b ...
     D_748_cl2g6c18b cl2g6c18b D_749_ql2g6c18b ql2g6c18b ...
     D_750_sl2g6c18b sl2g6c18b D_751_cl1g6c18b cl1g6c18b ...
     D_752_ql1g6c18b ql1g6c18b D_753_pl1g6c18b pl1g6c18b ...
     D_754_sl1g6c18b sl1g6c18b D_755_fl1g1c19a fl1g1c19a ...
     D_756_fl2g1c19a fl2g1c19a D_757_sl1g2c19a sl1g2c19a ...
     D_758_pl1g2c19a pl1g2c19a D_759_ql1g2c19a ql1g2c19a ...
     D_760_cl1g2c19a cl1g2c19a D_761_sl2g2c19a sl2g2c19a ...
     D_762_ql2g2c19a ql2g2c19a D_763_cl2g2c19a cl2g2c19a ...
     D_764_sl3g2c19a sl3g2c19a D_765_pl2g2c19a pl2g2c19a ...
     D_766_ql3g2c19a ql3g2c19a D_767_b1g3c19a b1g3c19a ...
     D_768_cm1g4c19a cm1g4c19a sqmhg4c19a D_770_qm1g4c19a qm1g4c19a D_771_sm1g4c19a sm1g4c19a D_772_fm1g4c19a fm1g4c19a ...
     D_773_pm1g4c19a pm1g4c19a D_774_qm2g4c19a qm2g4c19a ...
     D_775_sm2g4c19b sm2g4c19b D_776_qm2g4c19b qm2g4c19b ...
     D_777_sm1g4c19b sm1g4c19b D_778_pm1g4c19b pm1g4c19b ...
     D_779_qm1g4c19b qm1g4c19b D_780_cm1g4c19b cm1g4c19b ...
     D_781_b1g5c19b b1g5c19b D_782_ch2g6c19b ch2g6c19b ...
     D_783_sh4g6c19b sh4g6c19b D_784_ph2g6c19b ph2g6c19b ...
     D_785_qh3g6c19b qh3g6c19b D_786_sh3g6c19b sh3g6c19b ...
     D_787_qh2g6c19b qh2g6c19b D_788_ch1g6c19b ch1g6c19b ...
     D_789_qh1g6c19b qh1g6c19b D_790_ph1g6c19b ph1g6c19b ...
     D_791_sh1g6c19b sh1g6c19b D_792_fh1g1c20a fh1g1c20a ...
     D_793_fh2g1c20a fh2g1c20a D_794_sh1g2c20a sh1g2c20a ...
     D_795_ph1g2c20a ph1g2c20a D_796_qh1g2c20a qh1g2c20a ...
     D_797_ch1g2c20a ch1g2c20a sqhhg2c20a D_799_qh2g2c20a qh2g2c20a D_800_sh3g2c20a sh3g2c20a D_801_qh3g2c20a qh3g2c20a ...
     D_802_ph2g2c20a ph2g2c20a D_803_sh4g2c20a sh4g2c20a ...
     D_804_ch2g2c20a ch2g2c20a D_805_b1g3c20a b1g3c20a ...
     D_806_cm1g4c20a cm1g4c20a D_807_qm1g4c20a qm1g4c20a ...
     D_808_sm1g4c20a sm1g4c20a D_809_fm1g4c20a fm1g4c20a ...
     D_810_pm1g4c20a pm1g4c20a D_811_qm2g4c20a qm2g4c20a ...
     D_812_sm2g4c20b sm2g4c20b D_813_qm2g4c20b qm2g4c20b ...
     D_814_sm1g4c20b sm1g4c20b D_815_pm1g4c20b pm1g4c20b ...
     D_816_qm1g4c20b qm1g4c20b D_817_cm1g4c20b cm1g4c20b ...
     D_818_b1g5c20b b1g5c20b D_819_ql3g6c20b ql3g6c20b ...
     D_820_pl2g6c20b pl2g6c20b D_821_sl3g6c20b sl3g6c20b ...
     D_822_cl2g6c20b cl2g6c20b D_823_ql2g6c20b ql2g6c20b ...
     D_824_sl2g6c20b sl2g6c20b D_825_cl1g6c20b cl1g6c20b ...
     D_826_ql1g6c20b ql1g6c20b D_827_pl1g6c20b pl1g6c20b ...
     D_828_sl1g6c20b sl1g6c20b D_829_fl1g1c21a fl1g1c21a ...
     D_830_fl2g1c21a fl2g1c21a D_831_sl1g2c21a sl1g2c21a ...
     D_832_pl1g2c21a pl1g2c21a D_833_ql1g2c21a ql1g2c21a ...
     D_834_cl1g2c21a cl1g2c21a D_835_sl2g2c21a sl2g2c21a ...
     D_836_ql2g2c21a ql2g2c21a D_837_cl2g2c21a cl2g2c21a ...
     D_838_sl3g2c21a sl3g2c21a D_839_pl2g2c21a pl2g2c21a ...
     D_840_ql3g2c21a ql3g2c21a D_841_b1g3c21a b1g3c21a ...
     D_842_cm1g4c21a cm1g4c21a sqmhg4c21a D_844_qm1g4c21a qm1g4c21a D_845_sm1g4c21a sm1g4c21a D_846_fm1g4c21a fm1g4c21a ...
     D_847_pm1g4c21a pm1g4c21a D_848_qm2g4c21a qm2g4c21a ...
     D_849_sm2g4c21b sm2g4c21b D_850_qm2g4c21b qm2g4c21b ...
     D_851_sm1g4c21b sm1g4c21b D_852_pm1g4c21b pm1g4c21b ...
     D_853_qm1g4c21b qm1g4c21b D_854_cm1g4c21b cm1g4c21b ...
     D_855_b1g5c21b b1g5c21b D_856_ch2g6c21b ch2g6c21b ...
     D_857_sh4g6c21b sh4g6c21b D_858_ph2g6c21b ph2g6c21b ...
     D_859_qh3g6c21b qh3g6c21b D_860_sh3g6c21b sh3g6c21b ...
     D_861_qh2g6c21b qh2g6c21b D_862_ch1g6c21b ch1g6c21b ...
     D_863_qh1g6c21b qh1g6c21b D_864_ph1g6c21b ph1g6c21b ...
     D_865_sh1g6c21b sh1g6c21b D_866_fh1g1c22a fh1g1c22a ...
     D_867_fh2g1c22a fh2g1c22a D_868_sh1g2c22a sh1g2c22a ...
     D_869_ph1g2c22a ph1g2c22a D_870_qh1g2c22a qh1g2c22a ...
     D_871_ch1g2c22a ch1g2c22a sqhhg2c22a D_873_qh2g2c22a qh2g2c22a D_874_sh3g2c22a sh3g2c22a D_875_qh3g2c22a qh3g2c22a ...
     D_876_ph2g2c22a ph2g2c22a D_877_sh4g2c22a sh4g2c22a ...
     D_878_ch2g2c22a ch2g2c22a D_879_b1g3c22a b1g3c22a ...
     D_880_cm1g4c22a cm1g4c22a D_881_qm1g4c22a qm1g4c22a ...
     D_882_sm1g4c22a sm1g4c22a D_883_fm1g4c22a fm1g4c22a ...
     D_884_pm1g4c22a pm1g4c22a D_885_qm2g4c22a qm2g4c22a ...
     D_886_sm2g4c22b sm2g4c22b D_887_qm2g4c22b qm2g4c22b ...
     D_888_sm1g4c22b sm1g4c22b D_889_pm1g4c22b pm1g4c22b ...
     D_890_qm1g4c22b qm1g4c22b D_891_cm1g4c22b cm1g4c22b ...
     D_892_b1g5c22b b1g5c22b D_893_ql3g6c22b ql3g6c22b ...
     D_894_pl2g6c22b pl2g6c22b D_895_sl3g6c22b sl3g6c22b ...
     D_896_cl2g6c22b cl2g6c22b D_897_ql2g6c22b ql2g6c22b ...
     D_898_sl2g6c22b sl2g6c22b D_899_cl1g6c22b cl1g6c22b ...
     D_900_ql1g6c22b ql1g6c22b D_901_pl1g6c22b pl1g6c22b ...
     D_902_sl1g6c22b sl1g6c22b D_903_fl1g1c23a fl1g1c23a ...
     D_904_cu1g1c23id1 cu1g1c23id1 cs1g1c23id1 epu49g1c23u ...
     cu2g1c23id1 cs2g1c23id1 D_909_cu1g1c23id2 cu1g1c23id2 ...
     cs1g1c23id2 epu49g1c23d cu2g1c23id2 cs2g1c23id2 ...
     D_914_fl2g1c23a fl2g1c23a D_915_sl1g2c23a sl1g2c23a ...
     D_916_pl1g2c23a pl1g2c23a D_917_ql1g2c23a ql1g2c23a ...
     D_918_cl1g2c23a cl1g2c23a D_919_sl2g2c23a sl2g2c23a ...
     D_920_ql2g2c23a ql2g2c23a D_921_cl2g2c23a cl2g2c23a ...
     D_922_sl3g2c23a sl3g2c23a D_923_pl2g2c23a pl2g2c23a ...
     D_924_ql3g2c23a ql3g2c23a D_925_b2g3c23a b2g3c23a ...
     D_926_cm1g4c23a cm1g4c23a sqmhg4c23a D_928_qm1g4c23a qm1g4c23a D_929_sm1g4c23a sm1g4c23a D_930_fm1g4c23a fm1g4c23a ...
     D_931_pm1g4c23a pm1g4c23a D_932_qm2g4c23a qm2g4c23a ...
     D_933_sm2g4c23b sm2g4c23b D_934_qm2g4c23b qm2g4c23b ...
     D_935_sm1g4c23b sm1g4c23b D_936_pm1g4c23b pm1g4c23b ...
     D_937_qm1g4c23b qm1g4c23b D_938_cm1g4c23b cm1g4c23b ...
     D_939_b2g5c23b b2g5c23b D_940_ch2g6c23b ch2g6c23b ...
     D_941_sh4g6c23b sh4g6c23b D_942_ph2g6c23b ph2g6c23b ...
     D_943_qh3g6c23b qh3g6c23b D_944_sh3g6c23b sh3g6c23b ...
     D_945_qh2g6c23b qh2g6c23b D_946_ch1g6c23b ch1g6c23b ...
     D_947_qh1g6c23b qh1g6c23b D_948_ph1g6c23b ph1g6c23b ...
     D_949_sh1g6c23b sh1g6c23b D_950_fh1g1c24a fh1g1c24a ...
     D_951_cav cav D_952_fh2g1c24a fh2g1c24a ...
     D_953_sh1g2c24a sh1g2c24a D_954_ph1g2c24a ph1g2c24a ...
     D_955_qh1g2c24a qh1g2c24a D_956_ch1g2c24a ch1g2c24a ...
     sqhhg2c24a D_958_qh2g2c24a qh2g2c24a D_959_sh3g2c24a sh3g2c24a D_960_qh3g2c24a qh3g2c24a D_961_ph2g2c24a ph2g2c24a ...
     D_962_sh4g2c24a sh4g2c24a D_963_ch2g2c24a ch2g2c24a ...
     D_964_b1g3c24a b1g3c24a D_965_cm1g4c24a cm1g4c24a ...
     D_966_qm1g4c24a qm1g4c24a D_967_sm1g4c24a sm1g4c24a ...
     D_968_fm1g4c24a fm1g4c24a D_969_pm1g4c24a pm1g4c24a ...
     D_970_qm2g4c24a qm2g4c24a D_971_sm2g4c24b sm2g4c24b ...
     D_972_qm2g4c24b qm2g4c24b D_973_sm1g4c24b sm1g4c24b ...
     D_974_pm1g4c24b pm1g4c24b D_975_qm1g4c24b qm1g4c24b ...
     D_976_cm1g4c24b cm1g4c24b D_977_b1g5c24b b1g5c24b ...
     D_978_ql3g6c24b ql3g6c24b D_979_pl2g6c24b pl2g6c24b ...
     D_980_sl3g6c24b sl3g6c24b D_981_cl2g6c24b cl2g6c24b ...
     D_982_ql2g6c24b ql2g6c24b D_983_sl2g6c24b sl2g6c24b ...
     D_984_cl1g6c24b cl1g6c24b D_985_ql1g6c24b ql1g6c24b ...
     D_986_pl1g6c24b pl1g6c24b D_987_sl1g6c24b sl1g6c24b ...
     D_988_fl1g1c25a fl1g1c25a D_989_fl2g1c25a fl2g1c25a ...
     D_990_sl1g2c25a sl1g2c25a D_991_pl1g2c25a pl1g2c25a ...
     D_992_ql1g2c25a ql1g2c25a D_993_cl1g2c25a cl1g2c25a ...
     D_994_sl2g2c25a sl2g2c25a D_995_ql2g2c25a ql2g2c25a ...
     D_996_cl2g2c25a cl2g2c25a D_997_sl3g2c25a sl3g2c25a ...
     D_998_pl2g2c25a pl2g2c25a D_999_ql3g2c25a ql3g2c25a ...
     D_1000_b1g3c25a b1g3c25a D_1001_cm1g4c25a cm1g4c25a ...
     sqmhg4c25a D_1003_qm1g4c25a qm1g4c25a D_1004_sm1g4c25a sm1g4c25a D_1005_fm1g4c25a fm1g4c25a D_1006_pm1g4c25a pm1g4c25a ...
     D_1007_qm2g4c25a qm2g4c25a D_1008_sm2g4c25b sm2g4c25b ...
     D_1009_qm2g4c25b qm2g4c25b D_1010_sm1g4c25b sm1g4c25b ...
     D_1011_pm1g4c25b pm1g4c25b D_1012_qm1g4c25b qm1g4c25b ...
     D_1013_cm1g4c25b cm1g4c25b D_1014_b1g5c25b b1g5c25b ...
     D_1015_ch2g6c25b ch2g6c25b D_1016_sh4g6c25b sh4g6c25b ...
     D_1017_ph2g6c25b ph2g6c25b D_1018_qh3g6c25b qh3g6c25b ...
     D_1019_sh3g6c25b sh3g6c25b D_1020_qh2g6c25b qh2g6c25b ...
     D_1021_ch1g6c25b ch1g6c25b D_1022_qh1g6c25b qh1g6c25b ...
     D_1023_ph1g6c25b ph1g6c25b D_1024_sh1g6c25b sh1g6c25b ...
     D_1025_fh1g1c26a fh1g1c26a D_1026_fh2g1c26a fh2g1c26a ...
     D_1027_sh1g2c26a sh1g2c26a D_1028_ph1g2c26a ph1g2c26a ...
     D_1029_qh1g2c26a qh1g2c26a D_1030_ch1g2c26a ch1g2c26a ...
     sqhhg2c26a D_1032_qh2g2c26a qh2g2c26a D_1033_sh3g2c26a sh3g2c26a D_1034_qh3g2c26a qh3g2c26a D_1035_ph2g2c26a ph2g2c26a ...
     D_1036_sh4g2c26a sh4g2c26a D_1037_ch2g2c26a ch2g2c26a ...
     D_1038_b1g3c26a b1g3c26a D_1039_cm1g4c26a cm1g4c26a ...
     D_1040_qm1g4c26a qm1g4c26a D_1041_sm1g4c26a sm1g4c26a ...
     D_1042_fm1g4c26a fm1g4c26a D_1043_pm1g4c26a pm1g4c26a ...
     D_1044_qm2g4c26a qm2g4c26a D_1045_sm2g4c26b sm2g4c26b ...
     D_1046_qm2g4c26b qm2g4c26b D_1047_sm1g4c26b sm1g4c26b ...
     D_1048_pm1g4c26b pm1g4c26b D_1049_qm1g4c26b qm1g4c26b ...
     D_1050_cm1g4c26b cm1g4c26b D_1051_b1g5c26b b1g5c26b ...
     D_1052_ql3g6c26b ql3g6c26b D_1053_pl2g6c26b pl2g6c26b ...
     D_1054_sl3g6c26b sl3g6c26b D_1055_cl2g6c26b cl2g6c26b ...
     D_1056_ql2g6c26b ql2g6c26b D_1057_sl2g6c26b sl2g6c26b ...
     D_1058_cl1g6c26b cl1g6c26b D_1059_ql1g6c26b ql1g6c26b ...
     D_1060_pl1g6c26b pl1g6c26b D_1061_sl1g6c26b sl1g6c26b ...
     D_1062_fl1g1c27a fl1g1c27a D_1063_fl2g1c27a fl2g1c27a ...
     D_1064_sl1g2c27a sl1g2c27a D_1065_pl1g2c27a pl1g2c27a ...
     D_1066_ql1g2c27a ql1g2c27a D_1067_cl1g2c27a cl1g2c27a ...
     D_1068_sl2g2c27a sl2g2c27a D_1069_ql2g2c27a ql2g2c27a ...
     D_1070_cl2g2c27a cl2g2c27a D_1071_sl3g2c27a sl3g2c27a ...
     D_1072_pl2g2c27a pl2g2c27a D_1073_ql3g2c27a ql3g2c27a ...
     D_1074_b1g3c27a b1g3c27a D_1075_cm1g4c27a cm1g4c27a ...
     sqmhg4c27a D_1077_qm1g4c27a qm1g4c27a D_1078_sm1g4c27a sm1g4c27a D_1079_fm1g4c27a fm1g4c27a D_1080_pm1g4c27a pm1g4c27a ...
     D_1081_qm2g4c27a qm2g4c27a D_1082_sm2g4c27b sm2g4c27b ...
     D_1083_qm2g4c27b qm2g4c27b D_1084_sm1g4c27b sm1g4c27b ...
     D_1085_pm1g4c27b pm1g4c27b D_1086_qm1g4c27b qm1g4c27b ...
     D_1087_cm1g4c27b cm1g4c27b D_1088_b1g5c27b b1g5c27b ...
     D_1089_ch2g6c27b ch2g6c27b D_1090_sh4g6c27b sh4g6c27b ...
     D_1091_ph2g6c27b ph2g6c27b D_1092_qh3g6c27b qh3g6c27b ...
     D_1093_sh3g6c27b sh3g6c27b D_1094_qh2g6c27b qh2g6c27b ...
     D_1095_ch1g6c27b ch1g6c27b D_1096_qh1g6c27b qh1g6c27b ...
     D_1097_ph1g6c27b ph1g6c27b D_1098_sh1g6c27b sh1g6c27b ...
     D_1099_fh1g1c28a fh1g1c28a D_1100_pu1g1c28a pu1g1c28a ...
     D_1101_cu1g1c28id1 cu1g1c28id1 cs1g1c28id1 dw100g1c28u ...
     cu2g1c28id1 cs2g1c28id1 D_1106_cu1g1c28id2 cu1g1c28id2 ...
     cs1g1c28id2 dw100g1c28d cu2g1c28id2 cs2g1c28id2 ...
     D_1111_pu4g1c28a pu4g1c28a D_1112_fh2g1c28a fh2g1c28a ...
     D_1113_sh1g2c28a sh1g2c28a D_1114_ph1g2c28a ph1g2c28a ...
     D_1115_qh1g2c28a qh1g2c28a D_1116_ch1g2c28a ch1g2c28a ...
     sqhhg2c28a D_1118_qh2g2c28a qh2g2c28a D_1119_sh3g2c28a sh3g2c28a D_1120_qh3g2c28a qh3g2c28a D_1121_ph2g2c28a ph2g2c28a ...
     D_1122_sh4g2c28a sh4g2c28a D_1123_ch2g2c28a ch2g2c28a ...
     D_1124_b1g3c28a b1g3c28a D_1125_cm1g4c28a cm1g4c28a ...
     D_1126_qm1g4c28a qm1g4c28a D_1127_sm1g4c28a sm1g4c28a ...
     D_1128_fm1g4c28a fm1g4c28a D_1129_pm1g4c28a pm1g4c28a ...
     D_1130_qm2g4c28a qm2g4c28a D_1131_sm2g4c28b sm2g4c28b ...
     D_1132_qm2g4c28b qm2g4c28b D_1133_sm1g4c28b sm1g4c28b ...
     D_1134_pm1g4c28b pm1g4c28b D_1135_qm1g4c28b qm1g4c28b ...
     D_1136_cm1g4c28b cm1g4c28b D_1137_b1g5c28b b1g5c28b ...
     D_1138_ql3g6c28b ql3g6c28b D_1139_pl2g6c28b pl2g6c28b ...
     D_1140_sl3g6c28b sl3g6c28b D_1141_cl2g6c28b cl2g6c28b ...
     D_1142_ql2g6c28b ql2g6c28b D_1143_sl2g6c28b sl2g6c28b ...
     D_1144_cl1g6c28b cl1g6c28b D_1145_ql1g6c28b ql1g6c28b ...
     D_1146_pl1g6c28b pl1g6c28b D_1147_sl1g6c28b sl1g6c28b ...
     D_1148_fl1g1c29a fl1g1c29a D_1149_fl2g1c29a fl2g1c29a ...
     D_1150_sl1g2c29a sl1g2c29a D_1151_pl1g2c29a pl1g2c29a ...
     D_1152_ql1g2c29a ql1g2c29a D_1153_cl1g2c29a cl1g2c29a ...
     D_1154_sl2g2c29a sl2g2c29a D_1155_ql2g2c29a ql2g2c29a ...
     D_1156_cl2g2c29a cl2g2c29a D_1157_sl3g2c29a sl3g2c29a ...
     D_1158_pl2g2c29a pl2g2c29a D_1159_ql3g2c29a ql3g2c29a ...
     D_1160_b1g3c29a b1g3c29a D_1161_cm1g4c29a cm1g4c29a ...
     sqmhg4c29a D_1163_qm1g4c29a qm1g4c29a D_1164_sm1g4c29a sm1g4c29a D_1165_fm1g4c29a fm1g4c29a D_1166_pm1g4c29a pm1g4c29a ...
     D_1167_qm2g4c29a qm2g4c29a D_1168_sm2g4c29b sm2g4c29b ...
     D_1169_qm2g4c29b qm2g4c29b D_1170_sm1g4c29b sm1g4c29b ...
     D_1171_pm1g4c29b pm1g4c29b D_1172_qm1g4c29b qm1g4c29b ...
     D_1173_cm1g4c29b cm1g4c29b D_1174_b1g5c29b b1g5c29b ...
     D_1175_ch2g6c29b ch2g6c29b D_1176_sh4g6c29b sh4g6c29b ...
     D_1177_ph2g6c29b ph2g6c29b D_1178_qh3g6c29b qh3g6c29b ...
     D_1179_sh3g6c29b sh3g6c29b D_1180_qh2g6c29b qh2g6c29b ...
     D_1181_ch1g6c29b ch1g6c29b D_1182_qh1g6c29b qh1g6c29b ...
     D_1183_ph1g6c29b ph1g6c29b D_1184_sh1g6c29b sh1g6c29b ...
     D_1185_fh1g1c30a fh1g1c30a D_1186_TAIL ];


% END of BODY

buildlat(LV2SR);
THERING = setcellstruct(THERING, 'Energy', 1:length(THERING), Energy);

%for i=1:length(THERING),
%  %T = findelemm44(THERING{i},THERING{i}.PassMethod, [1.0e-6 0 0 0 0 0]');
%  s = findspos(THERING, i+1);
%  fprintf('%s L=%f, s=%f, sum(M)=%f\n', THERING{i}.FamName, THERING{i}.Length, s, sum(sum(T)));
%end

L0 = findspos(THERING, length(THERING)+1);
fprintf('   Total Length = %.6f meters  \n', L0);
%Rout = linepass(THERING, [1e-6, 0, 0, 0, 0, 0]');
%fprintf(' %.6f  %.6f  %.6f  %.6f  %.6f  %.6f\n', Rout(1),Rout(2),Rout(3),Rout(4),Rout(5),Rout(6));
%for k=1:length(THERING)
%    fprintf(' %d: %s, %.6f\n', k, THERING{k}.FamName, sum(sum(T)));
%end
