function varargout = v2srlattice(varargin)

global THERING 

if nargin >=1
   Energy = varargin{1};
else
  Energy = 200e6;
end

% BEG_ = marker('BEG', 'IdentityPass');

D_0_sh1g2c30a = drift('DRIFT', 4.65, 'DriftPass');
sh1g2c30a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 4.65
D_1_ph1g2c30a = drift('DRIFT', 0.085, 'DriftPass');
ph1g2c30a = marker('BPM', 'IdentityPass'); %s= 4.935
D_2_qh1g2c30a = drift('DRIFT', 0.0775, 'DriftPass');
qh1g2c30a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 5.0125
D_3_ch1g2c30a = drift('DRIFT', 0.245, 'DriftPass');
ch1g2c30a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 5.5325
D_4_sqhhg2c30a = drift('DRIFT', 8.881784197e-16, 'DriftPass');
sqhhg2c30a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 5.5325
D_5_qh2g2c30a = drift('DRIFT', 0.4595, 'DriftPass');
qh2g2c30a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 6.092
D_6_sh3g2c30a = drift('DRIFT', 0.19, 'DriftPass');
sh3g2c30a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 6.73
D_7_qh3g2c30a = drift('DRIFT', 0.1825, 'DriftPass');
qh3g2c30a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 7.1125
D_8_ph2g2c30a = drift('DRIFT', 0.07252, 'DriftPass');
ph2g2c30a = marker('BPM', 'IdentityPass'); %s= 7.46002
D_9_sh4g2c30a = drift('DRIFT', 0.08998, 'DriftPass');
sh4g2c30a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 7.55
D_10_ch2g2c30a = drift('DRIFT', 0.2485, 'DriftPass');
ch2g2c30a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 7.9985
D_11_cm1g4c30a = drift('DRIFT', 3.1525, 'DriftPass');
cm1g4c30a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 11.451
D_12_qm1g4c30a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c30a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 11.925
D_13_sm1g4c30a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c30a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 12.375
D_14_pm1g4c30a = drift('DRIFT', 0.5696, 'DriftPass');
pm1g4c30a = marker('BPM', 'IdentityPass'); %s= 13.1446
D_15_qm2g4c30a = drift('DRIFT', 0.0839, 'DriftPass');
qm2g4c30a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 13.2285
D_16_sm2g4c30b = drift('DRIFT', 0.1835, 'DriftPass');
sm2g4c30b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 13.695
D_17_qm2g4c30b = drift('DRIFT', 0.1835, 'DriftPass');
qm2g4c30b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 14.1285
D_18_sm1g4c30b = drift('DRIFT', 0.5035, 'DriftPass');
sm1g4c30b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 14.915
D_19_pm1g4c30b = drift('DRIFT', 0.2623, 'DriftPass');
pm1g4c30b = marker('BPM', 'IdentityPass'); %s= 15.3773
D_20_qm1g4c30b = drift('DRIFT', 0.0877, 'DriftPass');
qm1g4c30b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 15.465
D_21_cm1g4c30b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c30b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 15.824
D_22_ql3g6c30b = drift('DRIFT', 3.7735, 'DriftPass');
ql3g6c30b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 19.8975
D_23_pl2g6c30b = drift('DRIFT', 0.0747, 'DriftPass');
pl2g6c30b = marker('BPM', 'IdentityPass'); %s= 20.2472
D_24_sl3g6c30b = drift('DRIFT', 0.0878, 'DriftPass');
sl3g6c30b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 20.335
D_25_cl2g6c30b = drift('DRIFT', 0.1575, 'DriftPass');
cl2g6c30b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 20.6925
D_26_ql2g6c30b = drift('DRIFT', 0.2081, 'DriftPass');
ql2g6c30b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 21.1006
D_27_sl2g6c30b = drift('DRIFT', 0.25, 'DriftPass');
sl2g6c30b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 21.7986
D_28_cl1g6c30b = drift('DRIFT', 0.1313, 'DriftPass');
cl1g6c30b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 22.1299
D_29_ql1g6c30b = drift('DRIFT', 0.1312, 'DriftPass');
ql1g6c30b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 22.4611
D_30_pl1g6c30b = drift('DRIFT', 0.0748, 'DriftPass');
pl1g6c30b = marker('BPM', 'IdentityPass'); %s= 22.8109
D_31_sl1g6c30b = drift('DRIFT', 0.0877, 'DriftPass');
sl1g6c30b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 22.8986
D_32_sl1g2c01a = drift('DRIFT', 6.6, 'DriftPass');
sl1g2c01a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 29.6986
D_33_pl1g2c01a = drift('DRIFT', 0.09, 'DriftPass');
pl1g2c01a = marker('BPM', 'IdentityPass'); %s= 29.9886
D_34_ql1g2c01a = drift('DRIFT', 0.0725, 'DriftPass');
ql1g2c01a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 30.0611
D_35_cl1g2c01a = drift('DRIFT', 0.1312, 'DriftPass');
cl1g2c01a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 30.4673
D_36_sl2g2c01a = drift('DRIFT', 0.1313, 'DriftPass');
sl2g2c01a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 30.7986
D_37_ql2g2c01a = drift('DRIFT', 0.25, 'DriftPass');
ql2g2c01a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 31.2486
D_38_cl2g2c01a = drift('DRIFT', 0.2081, 'DriftPass');
cl2g2c01a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 31.9047
D_39_sl3g2c01a = drift('DRIFT', 0.1575, 'DriftPass');
sl3g2c01a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 32.2622
D_40_pl2g2c01a = drift('DRIFT', 0.0901, 'DriftPass');
pl2g2c01a = marker('BPM', 'IdentityPass'); %s= 32.5523
D_41_ql3g2c01a = drift('DRIFT', 0.0724, 'DriftPass');
ql3g2c01a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 32.6247
D_42_cm1g4c01a = drift('DRIFT', 3.8085, 'DriftPass');
cm1g4c01a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 36.7082
sqmhg4c01a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 36.7082
D_44_qm1g4c01a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c01a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 37.0822
D_45_sm1g4c01a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c01a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 37.5322
D_46_pm1g4c01a = drift('DRIFT', 0.5696, 'DriftPass');
pm1g4c01a = marker('BPM', 'IdentityPass'); %s= 38.3018
D_47_qm2g4c01a = drift('DRIFT', 0.0839, 'DriftPass');
qm2g4c01a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 38.3857
D_48_sm2g4c01b = drift('DRIFT', 0.1835, 'DriftPass');
sm2g4c01b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 38.8522
D_49_qm2g4c01b = drift('DRIFT', 0.1835, 'DriftPass');
qm2g4c01b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 39.2857
D_50_sm1g4c01b = drift('DRIFT', 0.5035, 'DriftPass');
sm1g4c01b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 40.0722
D_51_pm1g4c01b = drift('DRIFT', 0.2623, 'DriftPass');
pm1g4c01b = marker('BPM', 'IdentityPass'); %s= 40.5345
D_52_qm1g4c01b = drift('DRIFT', 0.0877, 'DriftPass');
qm1g4c01b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 40.6222
D_53_cm1g4c01b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c01b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 40.9812
D_54_ch2g6c01b = drift('DRIFT', 3.4023, 'DriftPass');
ch2g6c01b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 44.6835
D_55_sh4g6c01b = drift('DRIFT', 0.0637, 'DriftPass');
sh4g6c01b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 45.0472
D_56_ph2g6c01b = drift('DRIFT', 0.0896, 'DriftPass');
ph2g6c01b = marker('BPM', 'IdentityPass'); %s= 45.3368
D_57_qh3g6c01b = drift('DRIFT', 0.0729, 'DriftPass');
qh3g6c01b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 45.4097
D_58_sh3g6c01b = drift('DRIFT', 0.1825, 'DriftPass');
sh3g6c01b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 45.8672
D_59_qh2g6c01b = drift('DRIFT', 0.19, 'DriftPass');
qh2g6c01b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 46.2572
D_60_ch1g6c01b = drift('DRIFT', 0.4845, 'DriftPass');
ch1g6c01b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 47.1897
D_61_qh1g6c01b = drift('DRIFT', 0.12, 'DriftPass');
qh1g6c01b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 47.5097
D_62_ph1g6c01b = drift('DRIFT', 0.0771, 'DriftPass');
ph1g6c01b = marker('BPM', 'IdentityPass'); %s= 47.8618
D_63_sh1g6c01b = drift('DRIFT', 0.0854, 'DriftPass');
sh1g6c01b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 47.9472
D_64_sh1g2c02a = drift('DRIFT', 9.3, 'DriftPass');
sh1g2c02a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 57.4472
D_65_ph1g2c02a = drift('DRIFT', 0.085, 'DriftPass');
ph1g2c02a = marker('BPM', 'IdentityPass'); %s= 57.7322
D_66_qh1g2c02a = drift('DRIFT', 0.0775, 'DriftPass');
qh1g2c02a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 57.8097
D_67_ch1g2c02a = drift('DRIFT', 0.245, 'DriftPass');
ch1g2c02a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 58.3297
sqhhg2c02a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 58.3297
D_69_qh2g2c02a = drift('DRIFT', 0.4595, 'DriftPass');
qh2g2c02a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 58.8892
D_70_sh3g2c02a = drift('DRIFT', 0.19, 'DriftPass');
sh3g2c02a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 59.5272
D_71_qh3g2c02a = drift('DRIFT', 0.1825, 'DriftPass');
qh3g2c02a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 59.9097
D_72_ph2g2c02a = drift('DRIFT', 0.0725, 'DriftPass');
ph2g2c02a = marker('BPM', 'IdentityPass'); %s= 60.2572
D_73_sh4g2c02a = drift('DRIFT', 0.09, 'DriftPass');
sh4g2c02a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 60.3472
D_74_ch2g2c02a = drift('DRIFT', 0.2485, 'DriftPass');
ch2g2c02a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 60.7957
D_75_cm1g4c02a = drift('DRIFT', 3.1525, 'DriftPass');
cm1g4c02a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 64.2482
D_76_qm1g4c02a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c02a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 64.7222
D_77_sm1g4c02a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c02a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 65.1722
D_78_pm1g4c02a = drift('DRIFT', 0.5696, 'DriftPass');
pm1g4c02a = marker('BPM', 'IdentityPass'); %s= 65.9418
D_79_qm2g4c02a = drift('DRIFT', 0.0839, 'DriftPass');
qm2g4c02a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 66.0257
D_80_sm2g4c02b = drift('DRIFT', 0.1835, 'DriftPass');
sm2g4c02b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 66.4922
D_81_qm2g4c02b = drift('DRIFT', 0.1835, 'DriftPass');
qm2g4c02b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 66.9257
D_82_sm1g4c02b = drift('DRIFT', 0.5035, 'DriftPass');
sm1g4c02b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 67.7122
D_83_pm1g4c02b = drift('DRIFT', 0.2623, 'DriftPass');
pm1g4c02b = marker('BPM', 'IdentityPass'); %s= 68.1745
D_84_qm1g4c02b = drift('DRIFT', 0.0877, 'DriftPass');
qm1g4c02b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 68.2622
D_85_cm1g4c02b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c02b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 68.6212
D_86_ql3g6c02b = drift('DRIFT', 3.7735, 'DriftPass');
ql3g6c02b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 72.6947
D_87_pl2g6c02b = drift('DRIFT', 0.0747, 'DriftPass');
pl2g6c02b = marker('BPM', 'IdentityPass'); %s= 73.0444
D_88_sl3g6c02b = drift('DRIFT', 0.0878, 'DriftPass');
sl3g6c02b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 73.1322
D_89_cl2g6c02b = drift('DRIFT', 0.1575, 'DriftPass');
cl2g6c02b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 73.4897
D_90_ql2g6c02b = drift('DRIFT', 0.2081, 'DriftPass');
ql2g6c02b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 73.8978
D_91_sl2g6c02b = drift('DRIFT', 0.25, 'DriftPass');
sl2g6c02b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 74.5958
D_92_cl1g6c02b = drift('DRIFT', 0.1312, 'DriftPass');
cl1g6c02b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 74.927
D_93_ql1g6c02b = drift('DRIFT', 0.1313, 'DriftPass');
ql1g6c02b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 75.2583
D_94_pl1g6c02b = drift('DRIFT', 0.0748, 'DriftPass');
pl1g6c02b = marker('BPM', 'IdentityPass'); %s= 75.6081
D_95_sl1g6c02b = drift('DRIFT', 0.0877, 'DriftPass');
sl1g6c02b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 75.6958
D_96_sl1g2c03a = drift('DRIFT', 6.6, 'DriftPass');
sl1g2c03a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 82.4958
D_97_pl1g2c03a = drift('DRIFT', 0.09, 'DriftPass');
pl1g2c03a = marker('BPM', 'IdentityPass'); %s= 82.7858
D_98_ql1g2c03a = drift('DRIFT', 0.0725, 'DriftPass');
ql1g2c03a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 82.8583
D_99_cl1g2c03a = drift('DRIFT', 0.1312, 'DriftPass');
cl1g2c03a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 83.2645
D_100_sl2g2c03a = drift('DRIFT', 0.1313, 'DriftPass');
sl2g2c03a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 83.5958
D_101_ql2g2c03a = drift('DRIFT', 0.25, 'DriftPass');
ql2g2c03a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 84.0458
D_102_cl2g2c03a = drift('DRIFT', 0.2081, 'DriftPass');
cl2g2c03a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 84.7019
D_103_sl3g2c03a = drift('DRIFT', 0.1575, 'DriftPass');
sl3g2c03a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 85.0594
D_104_pl2g2c03a = drift('DRIFT', 0.0901, 'DriftPass');
pl2g2c03a = marker('BPM', 'IdentityPass'); %s= 85.3495
D_105_ql3g2c03a = drift('DRIFT', 0.0724, 'DriftPass');
ql3g2c03a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 85.4219
D_106_cm1g4c03a = drift('DRIFT', 3.8085, 'DriftPass');
cm1g4c03a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 89.5054
D_107_sqmhg4c03a = drift('DRIFT', 1.42108547152e-14, 'DriftPass');
sqmhg4c03a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 89.5054
D_108_qm1g4c03a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c03a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 89.8794
D_109_sm1g4c03a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c03a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 90.3294
D_110_pm1g4c03a = drift('DRIFT', 0.5696, 'DriftPass');
pm1g4c03a = marker('BPM', 'IdentityPass'); %s= 91.099
D_111_qm2g4c03a = drift('DRIFT', 0.0839, 'DriftPass');
qm2g4c03a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 91.1829
D_112_sm2g4c03b = drift('DRIFT', 0.1835, 'DriftPass');
sm2g4c03b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 91.6494
D_113_qm2g4c03b = drift('DRIFT', 0.1835, 'DriftPass');
qm2g4c03b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 92.0829
D_114_sm1g4c03b = drift('DRIFT', 0.5035, 'DriftPass');
sm1g4c03b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 92.8694
D_115_pm1g4c03b = drift('DRIFT', 0.2623, 'DriftPass');
pm1g4c03b = marker('BPM', 'IdentityPass'); %s= 93.3317
D_116_qm1g4c03b = drift('DRIFT', 0.0877, 'DriftPass');
qm1g4c03b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 93.4194
D_117_cm1g4c03b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c03b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 93.7784
D_118_ch2g6c03b = drift('DRIFT', 3.4023, 'DriftPass');
ch2g6c03b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 97.4807
D_119_sh4g6c03b = drift('DRIFT', 0.0637, 'DriftPass');
sh4g6c03b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 97.8444
D_120_ph2g6c03b = drift('DRIFT', 0.0896, 'DriftPass');
ph2g6c03b = marker('BPM', 'IdentityPass'); %s= 98.134
D_121_qh3g6c03b = drift('DRIFT', 0.0729, 'DriftPass');
qh3g6c03b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 98.2069
D_122_sh3g6c03b = drift('DRIFT', 0.1825, 'DriftPass');
sh3g6c03b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 98.6644
D_123_qh2g6c03b = drift('DRIFT', 0.19, 'DriftPass');
qh2g6c03b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 99.0544
D_124_ch1g6c03b = drift('DRIFT', 0.4846, 'DriftPass');
ch1g6c03b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 99.987
D_125_qh1g6c03b = drift('DRIFT', 0.12, 'DriftPass');
qh1g6c03b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 100.307
D_126_ph1g6c03b = drift('DRIFT', 0.077, 'DriftPass');
ph1g6c03b = marker('BPM', 'IdentityPass'); %s= 100.659
D_127_sh1g6c03b = drift('DRIFT', 0.085, 'DriftPass');
sh1g6c03b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 100.744
D_128_sh1g2c04a = drift('DRIFT', 9.3, 'DriftPass');
sh1g2c04a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 110.244
D_129_ph1g2c04a = drift('DRIFT', 0.085, 'DriftPass');
ph1g2c04a = marker('BPM', 'IdentityPass'); %s= 110.529
D_130_qh1g2c04a = drift('DRIFT', 0.078, 'DriftPass');
qh1g2c04a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 110.607
D_131_ch1g2c04a = drift('DRIFT', 0.245, 'DriftPass');
ch1g2c04a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 111.127
D_132_sqhhg2c04a = drift('DRIFT', 1.42108547152e-14, 'DriftPass');
sqhhg2c04a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 111.127
D_133_qh2g2c04a = drift('DRIFT', 0.459, 'DriftPass');
qh2g2c04a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 111.686
D_134_sh3g2c04a = drift('DRIFT', 0.19, 'DriftPass');
sh3g2c04a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 112.324
D_135_qh3g2c04a = drift('DRIFT', 0.183, 'DriftPass');
qh3g2c04a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 112.707
D_136_ph2g2c04a = drift('DRIFT', 0.072, 'DriftPass');
ph2g2c04a = marker('BPM', 'IdentityPass'); %s= 113.054
D_137_sh4g2c04a = drift('DRIFT', 0.09, 'DriftPass');
sh4g2c04a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 113.144
D_138_ch2g2c04a = drift('DRIFT', 0.249, 'DriftPass');
ch2g2c04a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 113.593
D_139_cm1g4c04a = drift('DRIFT', 3.152, 'DriftPass');
cm1g4c04a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 117.045
D_140_qm1g4c04a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c04a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 117.519
D_141_sm1g4c04a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c04a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 117.969
D_142_pm1g4c04a = drift('DRIFT', 0.57, 'DriftPass');
pm1g4c04a = marker('BPM', 'IdentityPass'); %s= 118.739
D_143_qm2g4c04a = drift('DRIFT', 0.084, 'DriftPass');
qm2g4c04a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 118.823
D_144_sm2g4c04b = drift('DRIFT', 0.183, 'DriftPass');
sm2g4c04b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 119.289
D_145_qm2g4c04b = drift('DRIFT', 0.184, 'DriftPass');
qm2g4c04b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 119.723
D_146_sm1g4c04b = drift('DRIFT', 0.503, 'DriftPass');
sm1g4c04b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 120.509
D_147_pm1g4c04b = drift('DRIFT', 0.263, 'DriftPass');
pm1g4c04b = marker('BPM', 'IdentityPass'); %s= 120.972
D_148_qm1g4c04b = drift('DRIFT', 0.087, 'DriftPass');
qm1g4c04b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 121.059
D_149_cm1g4c04b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c04b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 121.418
D_150_ql3g6c04b = drift('DRIFT', 3.774, 'DriftPass');
ql3g6c04b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 125.492
D_151_pl2g6c04b = drift('DRIFT', 0.075, 'DriftPass');
pl2g6c04b = marker('BPM', 'IdentityPass'); %s= 125.842
D_152_sl3g6c04b = drift('DRIFT', 0.087, 'DriftPass');
sl3g6c04b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 125.929
D_153_cl2g6c04b = drift('DRIFT', 0.158, 'DriftPass');
cl2g6c04b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 126.287
D_154_ql2g6c04b = drift('DRIFT', 0.208, 'DriftPass');
ql2g6c04b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 126.695
D_155_sl2g6c04b = drift('DRIFT', 0.25, 'DriftPass');
sl2g6c04b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 127.393
D_156_cl1g6c04b = drift('DRIFT', 0.131, 'DriftPass');
cl1g6c04b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 127.724
D_157_ql1g6c04b = drift('DRIFT', 0.132, 'DriftPass');
ql1g6c04b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 128.056
D_158_pl1g6c04b = drift('DRIFT', 0.074, 'DriftPass');
pl1g6c04b = marker('BPM', 'IdentityPass'); %s= 128.405
D_159_sl1g6c04b = drift('DRIFT', 0.088, 'DriftPass');
sl1g6c04b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 128.493
D_160_sl1g2c05a = drift('DRIFT', 6.6, 'DriftPass');
sl1g2c05a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 135.293
D_161_pl1g2c05a = drift('DRIFT', 0.09, 'DriftPass');
pl1g2c05a = marker('BPM', 'IdentityPass'); %s= 135.583
D_162_ql1g2c05a = drift('DRIFT', 0.072, 'DriftPass');
ql1g2c05a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 135.655
D_163_cl1g2c05a = drift('DRIFT', 0.132, 'DriftPass');
cl1g2c05a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 136.062
D_164_sl2g2c05a = drift('DRIFT', 0.131, 'DriftPass');
sl2g2c05a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 136.393
D_165_ql2g2c05a = drift('DRIFT', 0.25, 'DriftPass');
ql2g2c05a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 136.843
D_166_cl2g2c05a = drift('DRIFT', 0.208, 'DriftPass');
cl2g2c05a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 137.499
D_167_sl3g2c05a = drift('DRIFT', 0.158, 'DriftPass');
sl3g2c05a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 137.857
D_168_pl2g2c05a = drift('DRIFT', 0.09, 'DriftPass');
pl2g2c05a = marker('BPM', 'IdentityPass'); %s= 138.147
D_169_ql3g2c05a = drift('DRIFT', 0.072, 'DriftPass');
ql3g2c05a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 138.219
D_170_cm1g4c05a = drift('DRIFT', 3.809, 'DriftPass');
cm1g4c05a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 142.303
sqmhg4c05a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 142.303
D_172_qm1g4c05a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c05a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 142.677
D_173_sm1g4c05a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c05a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 143.127
D_174_pm1g4c05a = drift('DRIFT', 0.569, 'DriftPass');
pm1g4c05a = marker('BPM', 'IdentityPass'); %s= 143.896
D_175_qm2g4c05a = drift('DRIFT', 0.084, 'DriftPass');
qm2g4c05a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 143.98
D_176_sm2g4c05b = drift('DRIFT', 0.184, 'DriftPass');
sm2g4c05b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 144.447
D_177_qm2g4c05b = drift('DRIFT', 0.183, 'DriftPass');
qm2g4c05b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 144.88
D_178_sm1g4c05b = drift('DRIFT', 0.504, 'DriftPass');
sm1g4c05b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 145.667
D_179_pm1g4c05b = drift('DRIFT', 0.262, 'DriftPass');
pm1g4c05b = marker('BPM', 'IdentityPass'); %s= 146.129
D_180_qm1g4c05b = drift('DRIFT', 0.088, 'DriftPass');
qm1g4c05b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 146.217
D_181_cm1g4c05b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c05b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 146.576
D_182_ch2g6c05b = drift('DRIFT', 3.402, 'DriftPass');
ch2g6c05b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 150.278
D_183_sh4g6c05b = drift('DRIFT', 0.064, 'DriftPass');
sh4g6c05b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 150.642
D_184_ph2g6c05b = drift('DRIFT', 0.089, 'DriftPass');
ph2g6c05b = marker('BPM', 'IdentityPass'); %s= 150.931
D_185_qh3g6c05b = drift('DRIFT', 0.073, 'DriftPass');
qh3g6c05b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 151.004
D_186_sh3g6c05b = drift('DRIFT', 0.183, 'DriftPass');
sh3g6c05b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 151.462
D_187_qh2g6c05b = drift('DRIFT', 0.19, 'DriftPass');
qh2g6c05b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 151.852
D_188_ch1g6c05b = drift('DRIFT', 0.484, 'DriftPass');
ch1g6c05b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 152.784
D_189_qh1g6c05b = drift('DRIFT', 0.12, 'DriftPass');
qh1g6c05b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 153.104
D_190_ph1g6c05b = drift('DRIFT', 0.077, 'DriftPass');
ph1g6c05b = marker('BPM', 'IdentityPass'); %s= 153.456
D_191_sh1g6c05b = drift('DRIFT', 0.086, 'DriftPass');
sh1g6c05b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 153.542
D_192_sh1g2c06a = drift('DRIFT', 9.3, 'DriftPass');
sh1g2c06a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 163.042
D_193_ph1g2c06a = drift('DRIFT', 0.085, 'DriftPass');
ph1g2c06a = marker('BPM', 'IdentityPass'); %s= 163.327
D_194_qh1g2c06a = drift('DRIFT', 0.077, 'DriftPass');
qh1g2c06a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 163.404
D_195_ch1g2c06a = drift('DRIFT', 0.245, 'DriftPass');
ch1g2c06a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 163.924
sqhhg2c06a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 163.924
D_197_qh2g2c06a = drift('DRIFT', 0.46, 'DriftPass');
qh2g2c06a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 164.484
D_198_sh3g2c06a = drift('DRIFT', 0.19, 'DriftPass');
sh3g2c06a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 165.122
D_199_qh3g2c06a = drift('DRIFT', 0.182, 'DriftPass');
qh3g2c06a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 165.504
D_200_ph2g2c06a = drift('DRIFT', 0.073, 'DriftPass');
ph2g2c06a = marker('BPM', 'IdentityPass'); %s= 165.852
D_201_sh4g2c06a = drift('DRIFT', 0.09, 'DriftPass');
sh4g2c06a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 165.942
D_202_ch2g2c06a = drift('DRIFT', 0.248, 'DriftPass');
ch2g2c06a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 166.39
D_203_cm1g4c06a = drift('DRIFT', 3.153, 'DriftPass');
cm1g4c06a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 169.843
D_204_qm1g4c06a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c06a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 170.317
D_205_sm1g4c06a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c06a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 170.767
D_206_pm1g4c06a = drift('DRIFT', 0.569, 'DriftPass');
pm1g4c06a = marker('BPM', 'IdentityPass'); %s= 171.536
D_207_qm2g4c06a = drift('DRIFT', 0.084, 'DriftPass');
qm2g4c06a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 171.62
D_208_sm2g4c06b = drift('DRIFT', 0.184, 'DriftPass');
sm2g4c06b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 172.087
D_209_qm2g4c06b = drift('DRIFT', 0.183, 'DriftPass');
qm2g4c06b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 172.52
D_210_sm1g4c06b = drift('DRIFT', 0.504, 'DriftPass');
sm1g4c06b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 173.307
D_211_pm1g4c06b = drift('DRIFT', 0.262, 'DriftPass');
pm1g4c06b = marker('BPM', 'IdentityPass'); %s= 173.769
D_212_qm1g4c06b = drift('DRIFT', 0.088, 'DriftPass');
qm1g4c06b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 173.857
D_213_cm1g4c06b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c06b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 174.216
D_214_ql3g6c06b = drift('DRIFT', 3.773, 'DriftPass');
ql3g6c06b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 178.289
D_215_pl2g6c06b = drift('DRIFT', 0.075, 'DriftPass');
pl2g6c06b = marker('BPM', 'IdentityPass'); %s= 178.639
D_216_sl3g6c06b = drift('DRIFT', 0.088, 'DriftPass');
sl3g6c06b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 178.727
D_217_cl2g6c06b = drift('DRIFT', 0.157, 'DriftPass');
cl2g6c06b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 179.084
D_218_ql2g6c06b = drift('DRIFT', 0.208, 'DriftPass');
ql2g6c06b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 179.492
D_219_sl2g6c06b = drift('DRIFT', 0.25, 'DriftPass');
sl2g6c06b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 180.19
D_220_cl1g6c06b = drift('DRIFT', 0.131, 'DriftPass');
cl1g6c06b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 180.521
D_221_ql1g6c06b = drift('DRIFT', 0.132, 'DriftPass');
ql1g6c06b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 180.853
D_222_pl1g6c06b = drift('DRIFT', 0.074, 'DriftPass');
pl1g6c06b = marker('BPM', 'IdentityPass'); %s= 181.202
D_223_sl1g6c06b = drift('DRIFT', 0.088, 'DriftPass');
sl1g6c06b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 181.29
D_224_sl1g2c07a = drift('DRIFT', 6.6, 'DriftPass');
sl1g2c07a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 188.09
D_225_pl1g2c07a = drift('DRIFT', 0.09, 'DriftPass');
pl1g2c07a = marker('BPM', 'IdentityPass'); %s= 188.38
D_226_ql1g2c07a = drift('DRIFT', 0.073, 'DriftPass');
ql1g2c07a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 188.453
D_227_cl1g2c07a = drift('DRIFT', 0.131, 'DriftPass');
cl1g2c07a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 188.859
D_228_sl2g2c07a = drift('DRIFT', 0.131, 'DriftPass');
sl2g2c07a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 189.19
D_229_ql2g2c07a = drift('DRIFT', 0.25, 'DriftPass');
ql2g2c07a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 189.64
D_230_cl2g2c07a = drift('DRIFT', 0.208, 'DriftPass');
cl2g2c07a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 190.296
D_231_sl3g2c07a = drift('DRIFT', 0.158, 'DriftPass');
sl3g2c07a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 190.654
D_232_pl2g2c07a = drift('DRIFT', 0.09, 'DriftPass');
pl2g2c07a = marker('BPM', 'IdentityPass'); %s= 190.944
D_233_ql3g2c07a = drift('DRIFT', 0.072, 'DriftPass');
ql3g2c07a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 191.016
D_234_cm1g4c07a = drift('DRIFT', 3.809, 'DriftPass');
cm1g4c07a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 195.1
sqmhg4c07a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 195.1
D_236_qm1g4c07a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c07a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 195.474
D_237_sm1g4c07a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c07a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 195.924
D_238_pm1g4c07a = drift('DRIFT', 0.569, 'DriftPass');
pm1g4c07a = marker('BPM', 'IdentityPass'); %s= 196.693
D_239_qm2g4c07a = drift('DRIFT', 0.084, 'DriftPass');
qm2g4c07a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 196.777
D_240_sm2g4c07b = drift('DRIFT', 0.184, 'DriftPass');
sm2g4c07b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 197.244
D_241_qm2g4c07b = drift('DRIFT', 0.183, 'DriftPass');
qm2g4c07b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 197.677
D_242_sm1g4c07b = drift('DRIFT', 0.504, 'DriftPass');
sm1g4c07b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 198.464
D_243_pm1g4c07b = drift('DRIFT', 0.262, 'DriftPass');
pm1g4c07b = marker('BPM', 'IdentityPass'); %s= 198.926
D_244_qm1g4c07b = drift('DRIFT', 0.088, 'DriftPass');
qm1g4c07b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 199.014
D_245_cm1g4c07b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c07b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 199.373
D_246_ch2g6c07b = drift('DRIFT', 3.402, 'DriftPass');
ch2g6c07b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 203.075
D_247_sh4g6c07b = drift('DRIFT', 0.064, 'DriftPass');
sh4g6c07b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 203.439
D_248_ph2g6c07b = drift('DRIFT', 0.089, 'DriftPass');
ph2g6c07b = marker('BPM', 'IdentityPass'); %s= 203.728
D_249_qh3g6c07b = drift('DRIFT', 0.073, 'DriftPass');
qh3g6c07b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 203.801
D_250_sh3g6c07b = drift('DRIFT', 0.183, 'DriftPass');
sh3g6c07b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 204.259
D_251_qh2g6c07b = drift('DRIFT', 0.19, 'DriftPass');
qh2g6c07b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 204.649
D_252_ch1g6c07b = drift('DRIFT', 0.484, 'DriftPass');
ch1g6c07b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 205.581
D_253_qh1g6c07b = drift('DRIFT', 0.12, 'DriftPass');
qh1g6c07b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 205.901
D_254_ph1g6c07b = drift('DRIFT', 0.077, 'DriftPass');
ph1g6c07b = marker('BPM', 'IdentityPass'); %s= 206.253
D_255_sh1g6c07b = drift('DRIFT', 0.086, 'DriftPass');
sh1g6c07b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 206.339
D_256_sh1g2c08a = drift('DRIFT', 9.3, 'DriftPass');
sh1g2c08a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 215.839
D_257_ph1g2c08a = drift('DRIFT', 0.085, 'DriftPass');
ph1g2c08a = marker('BPM', 'IdentityPass'); %s= 216.124
D_258_qh1g2c08a = drift('DRIFT', 0.077, 'DriftPass');
qh1g2c08a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 216.201
D_259_ch1g2c08a = drift('DRIFT', 0.245, 'DriftPass');
ch1g2c08a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 216.721
sqhhg2c08a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 216.721
D_261_qh2g2c08a = drift('DRIFT', 0.46, 'DriftPass');
qh2g2c08a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 217.281
D_262_sh3g2c08a = drift('DRIFT', 0.19, 'DriftPass');
sh3g2c08a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 217.919
D_263_qh3g2c08a = drift('DRIFT', 0.182, 'DriftPass');
qh3g2c08a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 218.301
D_264_ph2g2c08a = drift('DRIFT', 0.073, 'DriftPass');
ph2g2c08a = marker('BPM', 'IdentityPass'); %s= 218.649
D_265_sh4g2c08a = drift('DRIFT', 0.09, 'DriftPass');
sh4g2c08a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 218.739
D_266_ch2g2c08a = drift('DRIFT', 0.248, 'DriftPass');
ch2g2c08a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 219.187
D_267_cm1g4c08a = drift('DRIFT', 3.153, 'DriftPass');
cm1g4c08a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 222.64
D_268_qm1g4c08a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c08a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 223.114
D_269_sm1g4c08a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c08a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 223.564
D_270_pm1g4c08a = drift('DRIFT', 0.569, 'DriftPass');
pm1g4c08a = marker('BPM', 'IdentityPass'); %s= 224.333
D_271_qm2g4c08a = drift('DRIFT', 0.084, 'DriftPass');
qm2g4c08a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 224.417
D_272_sm2g4c08b = drift('DRIFT', 0.184, 'DriftPass');
sm2g4c08b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 224.884
D_273_qm2g4c08b = drift('DRIFT', 0.183, 'DriftPass');
qm2g4c08b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 225.317
D_274_sm1g4c08b = drift('DRIFT', 0.504, 'DriftPass');
sm1g4c08b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 226.104
D_275_pm1g4c08b = drift('DRIFT', 0.262, 'DriftPass');
pm1g4c08b = marker('BPM', 'IdentityPass'); %s= 226.566
D_276_qm1g4c08b = drift('DRIFT', 0.088, 'DriftPass');
qm1g4c08b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 226.654
D_277_cm1g4c08b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c08b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 227.013
D_278_ql3g6c08b = drift('DRIFT', 3.773, 'DriftPass');
ql3g6c08b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 231.086
D_279_pl2g6c08b = drift('DRIFT', 0.075, 'DriftPass');
pl2g6c08b = marker('BPM', 'IdentityPass'); %s= 231.436
D_280_sl3g6c08b = drift('DRIFT', 0.088, 'DriftPass');
sl3g6c08b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 231.524
D_281_cl2g6c08b = drift('DRIFT', 0.157, 'DriftPass');
cl2g6c08b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 231.881
D_282_ql2g6c08b = drift('DRIFT', 0.208, 'DriftPass');
ql2g6c08b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 232.289
D_283_sl2g6c08b = drift('DRIFT', 0.25, 'DriftPass');
sl2g6c08b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 232.987
D_284_cl1g6c08b = drift('DRIFT', 0.132, 'DriftPass');
cl1g6c08b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 233.319
D_285_ql1g6c08b = drift('DRIFT', 0.131, 'DriftPass');
ql1g6c08b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 233.65
D_286_pl1g6c08b = drift('DRIFT', 0.075, 'DriftPass');
pl1g6c08b = marker('BPM', 'IdentityPass'); %s= 234.0
D_287_sl1g6c08b = drift('DRIFT', 0.087, 'DriftPass');
sl1g6c08b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 234.087
D_288_sl1g2c09a = drift('DRIFT', 6.6, 'DriftPass');
sl1g2c09a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 240.887
D_289_pl1g2c09a = drift('DRIFT', 0.09, 'DriftPass');
pl1g2c09a = marker('BPM', 'IdentityPass'); %s= 241.177
D_290_ql1g2c09a = drift('DRIFT', 0.073, 'DriftPass');
ql1g2c09a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 241.25
D_291_cl1g2c09a = drift('DRIFT', 0.131, 'DriftPass');
cl1g2c09a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 241.656
D_292_sl2g2c09a = drift('DRIFT', 0.131, 'DriftPass');
sl2g2c09a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 241.987
D_293_ql2g2c09a = drift('DRIFT', 0.25, 'DriftPass');
ql2g2c09a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 242.437
D_294_cl2g2c09a = drift('DRIFT', 0.208, 'DriftPass');
cl2g2c09a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 243.093
D_295_sl3g2c09a = drift('DRIFT', 0.158, 'DriftPass');
sl3g2c09a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 243.451
D_296_pl2g2c09a = drift('DRIFT', 0.09, 'DriftPass');
pl2g2c09a = marker('BPM', 'IdentityPass'); %s= 243.741
D_297_ql3g2c09a = drift('DRIFT', 0.072, 'DriftPass');
ql3g2c09a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 243.813
D_298_cm1g4c09a = drift('DRIFT', 3.809, 'DriftPass');
cm1g4c09a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 247.897
D_299_sqmhg4c09a = drift('DRIFT', 2.84217094304e-14, 'DriftPass');
sqmhg4c09a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 247.897
D_300_qm1g4c09a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c09a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 248.271
D_301_sm1g4c09a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c09a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 248.721
D_302_pm1g4c09a = drift('DRIFT', 0.57, 'DriftPass');
pm1g4c09a = marker('BPM', 'IdentityPass'); %s= 249.491
D_303_qm2g4c09a = drift('DRIFT', 0.083, 'DriftPass');
qm2g4c09a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 249.574
D_304_sm2g4c09b = drift('DRIFT', 0.184, 'DriftPass');
sm2g4c09b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 250.041
D_305_qm2g4c09b = drift('DRIFT', 0.183, 'DriftPass');
qm2g4c09b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 250.474
D_306_sm1g4c09b = drift('DRIFT', 0.504, 'DriftPass');
sm1g4c09b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 251.261
D_307_pm1g4c09b = drift('DRIFT', 0.262, 'DriftPass');
pm1g4c09b = marker('BPM', 'IdentityPass'); %s= 251.723
D_308_qm1g4c09b = drift('DRIFT', 0.088, 'DriftPass');
qm1g4c09b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 251.811
D_309_cm1g4c09b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c09b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 252.17
D_310_ch2g6c09b = drift('DRIFT', 3.402, 'DriftPass');
ch2g6c09b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 255.872
D_311_sh4g6c09b = drift('DRIFT', 0.064, 'DriftPass');
sh4g6c09b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 256.236
D_312_ph2g6c09b = drift('DRIFT', 0.09, 'DriftPass');
ph2g6c09b = marker('BPM', 'IdentityPass'); %s= 256.526
D_313_qh3g6c09b = drift('DRIFT', 0.072, 'DriftPass');
qh3g6c09b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 256.598
D_314_sh3g6c09b = drift('DRIFT', 0.183, 'DriftPass');
sh3g6c09b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 257.056
D_315_qh2g6c09b = drift('DRIFT', 0.19, 'DriftPass');
qh2g6c09b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 257.446
D_316_ch1g6c09b = drift('DRIFT', 0.484, 'DriftPass');
ch1g6c09b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 258.378
D_317_qh1g6c09b = drift('DRIFT', 0.12, 'DriftPass');
qh1g6c09b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 258.698
D_318_ph1g6c09b = drift('DRIFT', 0.078, 'DriftPass');
ph1g6c09b = marker('BPM', 'IdentityPass'); %s= 259.051
D_319_sh1g6c09b = drift('DRIFT', 0.085, 'DriftPass');
sh1g6c09b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 259.136
D_320_sh1g2c10a = drift('DRIFT', 9.3, 'DriftPass');
sh1g2c10a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 268.636
D_321_ph1g2c10a = drift('DRIFT', 0.085, 'DriftPass');
ph1g2c10a = marker('BPM', 'IdentityPass'); %s= 268.921
D_322_qh1g2c10a = drift('DRIFT', 0.0770000000001, 'DriftPass');
qh1g2c10a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 268.998
D_323_ch1g2c10a = drift('DRIFT', 0.245, 'DriftPass');
ch1g2c10a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 269.518
sqhhg2c10a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 269.518
D_325_qh2g2c10a = drift('DRIFT', 0.46, 'DriftPass');
qh2g2c10a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 270.078
D_326_sh3g2c10a = drift('DRIFT', 0.19, 'DriftPass');
sh3g2c10a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 270.716
D_327_qh3g2c10a = drift('DRIFT', 0.182, 'DriftPass');
qh3g2c10a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 271.098
D_328_ph2g2c10a = drift('DRIFT', 0.073, 'DriftPass');
ph2g2c10a = marker('BPM', 'IdentityPass'); %s= 271.446
D_329_sh4g2c10a = drift('DRIFT', 0.09, 'DriftPass');
sh4g2c10a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 271.536
D_330_ch2g2c10a = drift('DRIFT', 0.248, 'DriftPass');
ch2g2c10a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 271.984
D_331_cm1g4c10a = drift('DRIFT', 3.153, 'DriftPass');
cm1g4c10a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 275.437
D_332_qm1g4c10a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c10a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 275.911
D_333_sm1g4c10a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c10a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 276.361
D_334_pm1g4c10a = drift('DRIFT', 0.57, 'DriftPass');
pm1g4c10a = marker('BPM', 'IdentityPass'); %s= 277.131
D_335_qm2g4c10a = drift('DRIFT', 0.083, 'DriftPass');
qm2g4c10a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 277.214
D_336_sm2g4c10b = drift('DRIFT', 0.184, 'DriftPass');
sm2g4c10b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 277.681
D_337_qm2g4c10b = drift('DRIFT', 0.183, 'DriftPass');
qm2g4c10b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 278.114
D_338_sm1g4c10b = drift('DRIFT', 0.504, 'DriftPass');
sm1g4c10b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 278.901
D_339_pm1g4c10b = drift('DRIFT', 0.262, 'DriftPass');
pm1g4c10b = marker('BPM', 'IdentityPass'); %s= 279.363
D_340_qm1g4c10b = drift('DRIFT', 0.088, 'DriftPass');
qm1g4c10b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 279.451
D_341_cm1g4c10b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c10b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 279.81
D_342_ql3g6c10b = drift('DRIFT', 3.773, 'DriftPass');
ql3g6c10b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 283.883
D_343_pl2g6c10b = drift('DRIFT', 0.075, 'DriftPass');
pl2g6c10b = marker('BPM', 'IdentityPass'); %s= 284.233
D_344_sl3g6c10b = drift('DRIFT', 0.088, 'DriftPass');
sl3g6c10b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 284.321
D_345_cl2g6c10b = drift('DRIFT', 0.157, 'DriftPass');
cl2g6c10b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 284.678
D_346_ql2g6c10b = drift('DRIFT', 0.209, 'DriftPass');
ql2g6c10b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 285.087
D_347_sl2g6c10b = drift('DRIFT', 0.25, 'DriftPass');
sl2g6c10b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 285.785
D_348_cl1g6c10b = drift('DRIFT', 0.131, 'DriftPass');
cl1g6c10b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 286.116
D_349_ql1g6c10b = drift('DRIFT', 0.131, 'DriftPass');
ql1g6c10b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 286.447
D_350_pl1g6c10b = drift('DRIFT', 0.075, 'DriftPass');
pl1g6c10b = marker('BPM', 'IdentityPass'); %s= 286.797
D_351_sl1g6c10b = drift('DRIFT', 0.088, 'DriftPass');
sl1g6c10b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 286.885
D_352_sl1g2c11a = drift('DRIFT', 6.6, 'DriftPass');
sl1g2c11a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 293.685
D_353_pl1g2c11a = drift('DRIFT', 0.09, 'DriftPass');
pl1g2c11a = marker('BPM', 'IdentityPass'); %s= 293.975
D_354_ql1g2c11a = drift('DRIFT', 0.072, 'DriftPass');
ql1g2c11a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 294.047
D_355_cl1g2c11a = drift('DRIFT', 0.131, 'DriftPass');
cl1g2c11a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 294.453
D_356_sl2g2c11a = drift('DRIFT', 0.132, 'DriftPass');
sl2g2c11a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 294.785
D_357_ql2g2c11a = drift('DRIFT', 0.25, 'DriftPass');
ql2g2c11a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 295.235
D_358_cl2g2c11a = drift('DRIFT', 0.208, 'DriftPass');
cl2g2c11a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 295.891
D_359_sl3g2c11a = drift('DRIFT', 0.157, 'DriftPass');
sl3g2c11a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 296.248
D_360_pl2g2c11a = drift('DRIFT', 0.09, 'DriftPass');
pl2g2c11a = marker('BPM', 'IdentityPass'); %s= 296.538
D_361_ql3g2c11a = drift('DRIFT', 0.073, 'DriftPass');
ql3g2c11a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 296.611
D_362_cm1g4c11a = drift('DRIFT', 3.808, 'DriftPass');
cm1g4c11a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 300.694
sqmhg4c11a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 300.694
D_364_qm1g4c11a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c11a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 301.068
D_365_sm1g4c11a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c11a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 301.518
D_366_pm1g4c11a = drift('DRIFT', 0.57, 'DriftPass');
pm1g4c11a = marker('BPM', 'IdentityPass'); %s= 302.288
D_367_qm2g4c11a = drift('DRIFT', 0.0839999999999, 'DriftPass');
qm2g4c11a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 302.372
D_368_sm2g4c11b = drift('DRIFT', 0.183, 'DriftPass');
sm2g4c11b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 302.838
D_369_qm2g4c11b = drift('DRIFT', 0.184, 'DriftPass');
qm2g4c11b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 303.272
D_370_sm1g4c11b = drift('DRIFT', 0.503, 'DriftPass');
sm1g4c11b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 304.058
D_371_pm1g4c11b = drift('DRIFT', 0.262, 'DriftPass');
pm1g4c11b = marker('BPM', 'IdentityPass'); %s= 304.52
D_372_qm1g4c11b = drift('DRIFT', 0.088, 'DriftPass');
qm1g4c11b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 304.608
D_373_cm1g4c11b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c11b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 304.967
D_374_ch2g6c11b = drift('DRIFT', 3.403, 'DriftPass');
ch2g6c11b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 308.67
D_375_sh4g6c11b = drift('DRIFT', 0.063, 'DriftPass');
sh4g6c11b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 309.033
D_376_ph2g6c11b = drift('DRIFT', 0.09, 'DriftPass');
ph2g6c11b = marker('BPM', 'IdentityPass'); %s= 309.323
D_377_qh3g6c11b = drift('DRIFT', 0.073, 'DriftPass');
qh3g6c11b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 309.396
D_378_sh3g6c11b = drift('DRIFT', 0.182, 'DriftPass');
sh3g6c11b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 309.853
D_379_qh2g6c11b = drift('DRIFT', 0.19, 'DriftPass');
qh2g6c11b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 310.243
D_380_ch1g6c11b = drift('DRIFT', 0.485, 'DriftPass');
ch1g6c11b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 311.176
D_381_qh1g6c11b = drift('DRIFT', 0.12, 'DriftPass');
qh1g6c11b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 311.496
D_382_ph1g6c11b = drift('DRIFT', 0.077, 'DriftPass');
ph1g6c11b = marker('BPM', 'IdentityPass'); %s= 311.848
D_383_sh1g6c11b = drift('DRIFT', 0.085, 'DriftPass');
sh1g6c11b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 311.933
D_384_sh1g2c12a = drift('DRIFT', 9.3, 'DriftPass');
sh1g2c12a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 321.433
D_385_ph1g2c12a = drift('DRIFT', 0.085, 'DriftPass');
ph1g2c12a = marker('BPM', 'IdentityPass'); %s= 321.718
D_386_qh1g2c12a = drift('DRIFT', 0.078, 'DriftPass');
qh1g2c12a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 321.796
D_387_ch1g2c12a = drift('DRIFT', 0.245, 'DriftPass');
ch1g2c12a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 322.316
sqhhg2c12a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 322.316
D_389_qh2g2c12a = drift('DRIFT', 0.459, 'DriftPass');
qh2g2c12a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 322.875
D_390_sh3g2c12a = drift('DRIFT', 0.19, 'DriftPass');
sh3g2c12a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 323.513
D_391_qh3g2c12a = drift('DRIFT', 0.183, 'DriftPass');
qh3g2c12a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 323.896
D_392_ph2g2c12a = drift('DRIFT', 0.072, 'DriftPass');
ph2g2c12a = marker('BPM', 'IdentityPass'); %s= 324.243
D_393_sh4g2c12a = drift('DRIFT', 0.09, 'DriftPass');
sh4g2c12a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 324.333
D_394_ch2g2c12a = drift('DRIFT', 0.249, 'DriftPass');
ch2g2c12a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 324.782
D_395_cm1g4c12a = drift('DRIFT', 3.152, 'DriftPass');
cm1g4c12a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 328.234
D_396_qm1g4c12a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c12a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 328.708
D_397_sm1g4c12a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c12a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 329.158
D_398_pm1g4c12a = drift('DRIFT', 0.57, 'DriftPass');
pm1g4c12a = marker('BPM', 'IdentityPass'); %s= 329.928
D_399_qm2g4c12a = drift('DRIFT', 0.084, 'DriftPass');
qm2g4c12a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 330.012
D_400_sm2g4c12b = drift('DRIFT', 0.183, 'DriftPass');
sm2g4c12b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 330.478
D_401_qm2g4c12b = drift('DRIFT', 0.184, 'DriftPass');
qm2g4c12b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 330.912
D_402_sm1g4c12b = drift('DRIFT', 0.503, 'DriftPass');
sm1g4c12b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 331.698
D_403_pm1g4c12b = drift('DRIFT', 0.262, 'DriftPass');
pm1g4c12b = marker('BPM', 'IdentityPass'); %s= 332.16
D_404_qm1g4c12b = drift('DRIFT', 0.088, 'DriftPass');
qm1g4c12b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 332.248
D_405_cm1g4c12b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c12b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 332.607
D_406_ql3g6c12b = drift('DRIFT', 3.774, 'DriftPass');
ql3g6c12b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 336.681
D_407_pl2g6c12b = drift('DRIFT', 0.074, 'DriftPass');
pl2g6c12b = marker('BPM', 'IdentityPass'); %s= 337.03
D_408_sl3g6c12b = drift('DRIFT', 0.088, 'DriftPass');
sl3g6c12b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 337.118
D_409_cl2g6c12b = drift('DRIFT', 0.158, 'DriftPass');
cl2g6c12b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 337.476
D_410_ql2g6c12b = drift('DRIFT', 0.208, 'DriftPass');
ql2g6c12b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 337.884
D_411_sl2g6c12b = drift('DRIFT', 0.25, 'DriftPass');
sl2g6c12b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 338.582
D_412_cl1g6c12b = drift('DRIFT', 0.131, 'DriftPass');
cl1g6c12b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 338.913
D_413_ql1g6c12b = drift('DRIFT', 0.131, 'DriftPass');
ql1g6c12b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 339.244
D_414_pl1g6c12b = drift('DRIFT', 0.075, 'DriftPass');
pl1g6c12b = marker('BPM', 'IdentityPass'); %s= 339.594
D_415_sl1g6c12b = drift('DRIFT', 0.088, 'DriftPass');
sl1g6c12b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 339.682
D_416_sl1g2c13a = drift('DRIFT', 6.6, 'DriftPass');
sl1g2c13a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 346.482
D_417_pl1g2c13a = drift('DRIFT', 0.09, 'DriftPass');
pl1g2c13a = marker('BPM', 'IdentityPass'); %s= 346.772
D_418_ql1g2c13a = drift('DRIFT', 0.0720000000001, 'DriftPass');
ql1g2c13a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 346.844
D_419_cl1g2c13a = drift('DRIFT', 0.132, 'DriftPass');
cl1g2c13a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 347.251
D_420_sl2g2c13a = drift('DRIFT', 0.131, 'DriftPass');
sl2g2c13a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 347.582
D_421_ql2g2c13a = drift('DRIFT', 0.25, 'DriftPass');
ql2g2c13a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 348.032
D_422_cl2g2c13a = drift('DRIFT', 0.208, 'DriftPass');
cl2g2c13a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 348.688
D_423_sl3g2c13a = drift('DRIFT', 0.157, 'DriftPass');
sl3g2c13a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 349.045
D_424_pl2g2c13a = drift('DRIFT', 0.09, 'DriftPass');
pl2g2c13a = marker('BPM', 'IdentityPass'); %s= 349.335
D_425_ql3g2c13a = drift('DRIFT', 0.073, 'DriftPass');
ql3g2c13a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 349.408
D_426_cm1g4c13a = drift('DRIFT', 3.808, 'DriftPass');
cm1g4c13a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 353.491
sqmhg4c13a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 353.491
D_428_qm1g4c13a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c13a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 353.865
D_429_sm1g4c13a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c13a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 354.315
D_430_pm1g4c13a = drift('DRIFT', 0.57, 'DriftPass');
pm1g4c13a = marker('BPM', 'IdentityPass'); %s= 355.085
D_431_qm2g4c13a = drift('DRIFT', 0.084, 'DriftPass');
qm2g4c13a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 355.169
D_432_sm2g4c13b = drift('DRIFT', 0.183, 'DriftPass');
sm2g4c13b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 355.635
D_433_qm2g4c13b = drift('DRIFT', 0.184, 'DriftPass');
qm2g4c13b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 356.069
D_434_sm1g4c13b = drift('DRIFT', 0.503, 'DriftPass');
sm1g4c13b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 356.855
D_435_pm1g4c13b = drift('DRIFT', 0.263, 'DriftPass');
pm1g4c13b = marker('BPM', 'IdentityPass'); %s= 357.318
D_436_qm1g4c13b = drift('DRIFT', 0.087, 'DriftPass');
qm1g4c13b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 357.405
D_437_cm1g4c13b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c13b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 357.764
D_438_ch2g6c13b = drift('DRIFT', 3.403, 'DriftPass');
ch2g6c13b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 361.467
D_439_sh4g6c13b = drift('DRIFT', 0.063, 'DriftPass');
sh4g6c13b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 361.83
D_440_ph2g6c13b = drift('DRIFT', 0.09, 'DriftPass');
ph2g6c13b = marker('BPM', 'IdentityPass'); %s= 362.12
D_441_qh3g6c13b = drift('DRIFT', 0.073, 'DriftPass');
qh3g6c13b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 362.193
D_442_sh3g6c13b = drift('DRIFT', 0.182, 'DriftPass');
sh3g6c13b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 362.65
D_443_qh2g6c13b = drift('DRIFT', 0.19, 'DriftPass');
qh2g6c13b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 363.04
D_444_ch1g6c13b = drift('DRIFT', 0.485, 'DriftPass');
ch1g6c13b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 363.973
D_445_qh1g6c13b = drift('DRIFT', 0.12, 'DriftPass');
qh1g6c13b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 364.293
D_446_ph1g6c13b = drift('DRIFT', 0.077, 'DriftPass');
ph1g6c13b = marker('BPM', 'IdentityPass'); %s= 364.645
D_447_sh1g6c13b = drift('DRIFT', 0.085, 'DriftPass');
sh1g6c13b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 364.73
D_448_sh1g2c14a = drift('DRIFT', 9.3, 'DriftPass');
sh1g2c14a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 374.23
D_449_ph1g2c14a = drift('DRIFT', 0.085, 'DriftPass');
ph1g2c14a = marker('BPM', 'IdentityPass'); %s= 374.515
D_450_qh1g2c14a = drift('DRIFT', 0.078, 'DriftPass');
qh1g2c14a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 374.593
D_451_ch1g2c14a = drift('DRIFT', 0.245, 'DriftPass');
ch1g2c14a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 375.113
sqhhg2c14a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 375.113
D_453_qh2g2c14a = drift('DRIFT', 0.459, 'DriftPass');
qh2g2c14a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 375.672
D_454_sh3g2c14a = drift('DRIFT', 0.19, 'DriftPass');
sh3g2c14a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 376.31
D_455_qh3g2c14a = drift('DRIFT', 0.183, 'DriftPass');
qh3g2c14a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 376.693
D_456_ph2g2c14a = drift('DRIFT', 0.072, 'DriftPass');
ph2g2c14a = marker('BPM', 'IdentityPass'); %s= 377.04
D_457_sh4g2c14a = drift('DRIFT', 0.09, 'DriftPass');
sh4g2c14a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 377.13
D_458_ch2g2c14a = drift('DRIFT', 0.249, 'DriftPass');
ch2g2c14a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 377.579
D_459_cm1g4c14a = drift('DRIFT', 3.152, 'DriftPass');
cm1g4c14a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 381.031
D_460_qm1g4c14a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c14a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 381.505
D_461_sm1g4c14a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c14a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 381.955
D_462_pm1g4c14a = drift('DRIFT', 0.57, 'DriftPass');
pm1g4c14a = marker('BPM', 'IdentityPass'); %s= 382.725
D_463_qm2g4c14a = drift('DRIFT', 0.0839999999999, 'DriftPass');
qm2g4c14a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 382.809
D_464_sm2g4c14b = drift('DRIFT', 0.183, 'DriftPass');
sm2g4c14b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 383.275
D_465_qm2g4c14b = drift('DRIFT', 0.184, 'DriftPass');
qm2g4c14b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 383.709
D_466_sm1g4c14b = drift('DRIFT', 0.503, 'DriftPass');
sm1g4c14b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 384.495
D_467_pm1g4c14b = drift('DRIFT', 0.263, 'DriftPass');
pm1g4c14b = marker('BPM', 'IdentityPass'); %s= 384.958
D_468_qm1g4c14b = drift('DRIFT', 0.087, 'DriftPass');
qm1g4c14b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 385.045
D_469_cm1g4c14b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c14b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 385.404
D_470_ql3g6c14b = drift('DRIFT', 3.774, 'DriftPass');
ql3g6c14b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 389.478
D_471_pl2g6c14b = drift('DRIFT', 0.075, 'DriftPass');
pl2g6c14b = marker('BPM', 'IdentityPass'); %s= 389.828
D_472_sl3g6c14b = drift('DRIFT', 0.087, 'DriftPass');
sl3g6c14b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 389.915
D_473_cl2g6c14b = drift('DRIFT', 0.158, 'DriftPass');
cl2g6c14b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 390.273
D_474_ql2g6c14b = drift('DRIFT', 0.208, 'DriftPass');
ql2g6c14b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 390.681
D_475_sl2g6c14b = drift('DRIFT', 0.25, 'DriftPass');
sl2g6c14b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 391.379
D_476_cl1g6c14b = drift('DRIFT', 0.131, 'DriftPass');
cl1g6c14b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 391.71
D_477_ql1g6c14b = drift('DRIFT', 0.131, 'DriftPass');
ql1g6c14b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 392.041
D_478_pl1g6c14b = drift('DRIFT', 0.075, 'DriftPass');
pl1g6c14b = marker('BPM', 'IdentityPass'); %s= 392.391
D_479_sl1g6c14b = drift('DRIFT', 0.088, 'DriftPass');
sl1g6c14b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 392.479
D_480_sl1g2c15a = drift('DRIFT', 6.6, 'DriftPass');
sl1g2c15a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 399.279
D_481_pl1g2c15a = drift('DRIFT', 0.09, 'DriftPass');
pl1g2c15a = marker('BPM', 'IdentityPass'); %s= 399.569
D_482_ql1g2c15a = drift('DRIFT', 0.072, 'DriftPass');
ql1g2c15a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 399.641
D_483_cl1g2c15a = drift('DRIFT', 0.132, 'DriftPass');
cl1g2c15a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 400.048
D_484_sl2g2c15a = drift('DRIFT', 0.131, 'DriftPass');
sl2g2c15a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 400.379
D_485_ql2g2c15a = drift('DRIFT', 0.25, 'DriftPass');
ql2g2c15a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 400.829
D_486_cl2g2c15a = drift('DRIFT', 0.208, 'DriftPass');
cl2g2c15a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 401.485
D_487_sl3g2c15a = drift('DRIFT', 0.158, 'DriftPass');
sl3g2c15a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 401.843
D_488_pl2g2c15a = drift('DRIFT', 0.09, 'DriftPass');
pl2g2c15a = marker('BPM', 'IdentityPass'); %s= 402.133
D_489_ql3g2c15a = drift('DRIFT', 0.0720000000001, 'DriftPass');
ql3g2c15a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 402.205
D_490_cm1g4c15a = drift('DRIFT', 3.809, 'DriftPass');
cm1g4c15a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 406.289
sqmhg4c15a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 406.289
D_492_qm1g4c15a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c15a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 406.663
D_493_sm1g4c15a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c15a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 407.113
D_494_pm1g4c15a = drift('DRIFT', 0.569, 'DriftPass');
pm1g4c15a = marker('BPM', 'IdentityPass'); %s= 407.882
D_495_qm2g4c15a = drift('DRIFT', 0.084, 'DriftPass');
qm2g4c15a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 407.966
D_496_sm2g4c15b = drift('DRIFT', 0.184, 'DriftPass');
sm2g4c15b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 408.433
D_497_qm2g4c15b = drift('DRIFT', 0.183, 'DriftPass');
qm2g4c15b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 408.866
D_498_sm1g4c15b = drift('DRIFT', 0.504, 'DriftPass');
sm1g4c15b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 409.653
D_499_pm1g4c15b = drift('DRIFT', 0.262, 'DriftPass');
pm1g4c15b = marker('BPM', 'IdentityPass'); %s= 410.115
D_500_qm1g4c15b = drift('DRIFT', 0.088, 'DriftPass');
qm1g4c15b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 410.203
D_501_cm1g4c15b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c15b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 410.562
D_502_ch2g6c15b = drift('DRIFT', 3.402, 'DriftPass');
ch2g6c15b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 414.264
D_503_sh4g6c15b = drift('DRIFT', 0.064, 'DriftPass');
sh4g6c15b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 414.628
D_504_ph2g6c15b = drift('DRIFT', 0.089, 'DriftPass');
ph2g6c15b = marker('BPM', 'IdentityPass'); %s= 414.917
D_505_qh3g6c15b = drift('DRIFT', 0.073, 'DriftPass');
qh3g6c15b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 414.99
D_506_sh3g6c15b = drift('DRIFT', 0.183, 'DriftPass');
sh3g6c15b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 415.448
D_507_qh2g6c15b = drift('DRIFT', 0.19, 'DriftPass');
qh2g6c15b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 415.838
D_508_ch1g6c15b = drift('DRIFT', 0.484, 'DriftPass');
ch1g6c15b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 416.77
D_509_qh1g6c15b = drift('DRIFT', 0.12, 'DriftPass');
qh1g6c15b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 417.09
D_510_ph1g6c15b = drift('DRIFT', 0.077, 'DriftPass');
ph1g6c15b = marker('BPM', 'IdentityPass'); %s= 417.442
D_511_sh1g6c15b = drift('DRIFT', 0.086, 'DriftPass');
sh1g6c15b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 417.528
D_512_sh1g2c16a = drift('DRIFT', 9.3, 'DriftPass');
sh1g2c16a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 427.028
D_513_ph1g2c16a = drift('DRIFT', 0.085, 'DriftPass');
ph1g2c16a = marker('BPM', 'IdentityPass'); %s= 427.313
D_514_qh1g2c16a = drift('DRIFT', 0.0770000000001, 'DriftPass');
qh1g2c16a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 427.39
D_515_ch1g2c16a = drift('DRIFT', 0.245, 'DriftPass');
ch1g2c16a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 427.91
sqhhg2c16a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 427.91
D_517_qh2g2c16a = drift('DRIFT', 0.46, 'DriftPass');
qh2g2c16a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 428.47
D_518_sh3g2c16a = drift('DRIFT', 0.19, 'DriftPass');
sh3g2c16a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 429.108
D_519_qh3g2c16a = drift('DRIFT', 0.182, 'DriftPass');
qh3g2c16a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 429.49
D_520_ph2g2c16a = drift('DRIFT', 0.073, 'DriftPass');
ph2g2c16a = marker('BPM', 'IdentityPass'); %s= 429.838
D_521_sh4g2c16a = drift('DRIFT', 0.09, 'DriftPass');
sh4g2c16a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 429.928
D_522_ch2g2c16a = drift('DRIFT', 0.248, 'DriftPass');
ch2g2c16a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 430.376
D_523_cm1g4c16a = drift('DRIFT', 3.153, 'DriftPass');
cm1g4c16a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 433.829
D_524_qm1g4c16a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c16a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 434.303
D_525_sm1g4c16a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c16a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 434.753
D_526_pm1g4c16a = drift('DRIFT', 0.569, 'DriftPass');
pm1g4c16a = marker('BPM', 'IdentityPass'); %s= 435.522
D_527_qm2g4c16a = drift('DRIFT', 0.084, 'DriftPass');
qm2g4c16a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 435.606
D_528_sm2g4c16b = drift('DRIFT', 0.184, 'DriftPass');
sm2g4c16b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 436.073
D_529_qm2g4c16b = drift('DRIFT', 0.183, 'DriftPass');
qm2g4c16b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 436.506
D_530_sm1g4c16b = drift('DRIFT', 0.504, 'DriftPass');
sm1g4c16b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 437.293
D_531_pm1g4c16b = drift('DRIFT', 0.262, 'DriftPass');
pm1g4c16b = marker('BPM', 'IdentityPass'); %s= 437.755
D_532_qm1g4c16b = drift('DRIFT', 0.088, 'DriftPass');
qm1g4c16b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 437.843
D_533_cm1g4c16b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c16b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 438.202
D_534_ql3g6c16b = drift('DRIFT', 3.773, 'DriftPass');
ql3g6c16b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 442.275
D_535_pl2g6c16b = drift('DRIFT', 0.075, 'DriftPass');
pl2g6c16b = marker('BPM', 'IdentityPass'); %s= 442.625
D_536_sl3g6c16b = drift('DRIFT', 0.088, 'DriftPass');
sl3g6c16b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 442.713
D_537_cl2g6c16b = drift('DRIFT', 0.157, 'DriftPass');
cl2g6c16b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 443.07
D_538_ql2g6c16b = drift('DRIFT', 0.208, 'DriftPass');
ql2g6c16b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 443.478
D_539_sl2g6c16b = drift('DRIFT', 0.25, 'DriftPass');
sl2g6c16b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 444.176
D_540_cl1g6c16b = drift('DRIFT', 0.131, 'DriftPass');
cl1g6c16b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 444.507
D_541_ql1g6c16b = drift('DRIFT', 0.132, 'DriftPass');
ql1g6c16b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 444.839
D_542_pl1g6c16b = drift('DRIFT', 0.074, 'DriftPass');
pl1g6c16b = marker('BPM', 'IdentityPass'); %s= 445.188
D_543_sl1g6c16b = drift('DRIFT', 0.088, 'DriftPass');
sl1g6c16b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 445.276
D_544_sl1g2c17a = drift('DRIFT', 6.6, 'DriftPass');
sl1g2c17a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 452.076
D_545_pl1g2c17a = drift('DRIFT', 0.09, 'DriftPass');
pl1g2c17a = marker('BPM', 'IdentityPass'); %s= 452.366
D_546_ql1g2c17a = drift('DRIFT', 0.073, 'DriftPass');
ql1g2c17a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 452.439
D_547_cl1g2c17a = drift('DRIFT', 0.131, 'DriftPass');
cl1g2c17a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 452.845
D_548_sl2g2c17a = drift('DRIFT', 0.131, 'DriftPass');
sl2g2c17a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 453.176
D_549_ql2g2c17a = drift('DRIFT', 0.25, 'DriftPass');
ql2g2c17a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 453.626
D_550_cl2g2c17a = drift('DRIFT', 0.208, 'DriftPass');
cl2g2c17a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 454.282
D_551_sl3g2c17a = drift('DRIFT', 0.158, 'DriftPass');
sl3g2c17a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 454.64
D_552_pl2g2c17a = drift('DRIFT', 0.09, 'DriftPass');
pl2g2c17a = marker('BPM', 'IdentityPass'); %s= 454.93
D_553_ql3g2c17a = drift('DRIFT', 0.072, 'DriftPass');
ql3g2c17a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 455.002
D_554_cm1g4c17a = drift('DRIFT', 3.809, 'DriftPass');
cm1g4c17a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 459.086
sqmhg4c17a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 459.086
D_556_qm1g4c17a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c17a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 459.46
D_557_sm1g4c17a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c17a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 459.91
D_558_pm1g4c17a = drift('DRIFT', 0.569, 'DriftPass');
pm1g4c17a = marker('BPM', 'IdentityPass'); %s= 460.679
D_559_qm2g4c17a = drift('DRIFT', 0.084, 'DriftPass');
qm2g4c17a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 460.763
D_560_sm2g4c17b = drift('DRIFT', 0.184, 'DriftPass');
sm2g4c17b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 461.23
D_561_qm2g4c17b = drift('DRIFT', 0.183, 'DriftPass');
qm2g4c17b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 461.663
D_562_sm1g4c17b = drift('DRIFT', 0.504, 'DriftPass');
sm1g4c17b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 462.45
D_563_pm1g4c17b = drift('DRIFT', 0.262, 'DriftPass');
pm1g4c17b = marker('BPM', 'IdentityPass'); %s= 462.912
D_564_qm1g4c17b = drift('DRIFT', 0.088, 'DriftPass');
qm1g4c17b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 463.0
D_565_cm1g4c17b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c17b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 463.359
D_566_ch2g6c17b = drift('DRIFT', 3.402, 'DriftPass');
ch2g6c17b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 467.061
D_567_sh4g6c17b = drift('DRIFT', 0.064, 'DriftPass');
sh4g6c17b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 467.425
D_568_ph2g6c17b = drift('DRIFT', 0.089, 'DriftPass');
ph2g6c17b = marker('BPM', 'IdentityPass'); %s= 467.714
D_569_qh3g6c17b = drift('DRIFT', 0.073, 'DriftPass');
qh3g6c17b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 467.787
D_570_sh3g6c17b = drift('DRIFT', 0.183, 'DriftPass');
sh3g6c17b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 468.245
D_571_qh2g6c17b = drift('DRIFT', 0.19, 'DriftPass');
qh2g6c17b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 468.635
D_572_ch1g6c17b = drift('DRIFT', 0.484, 'DriftPass');
ch1g6c17b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 469.567
D_573_qh1g6c17b = drift('DRIFT', 0.12, 'DriftPass');
qh1g6c17b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 469.887
D_574_ph1g6c17b = drift('DRIFT', 0.077, 'DriftPass');
ph1g6c17b = marker('BPM', 'IdentityPass'); %s= 470.239
D_575_sh1g6c17b = drift('DRIFT', 0.086, 'DriftPass');
sh1g6c17b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 470.325
D_576_sh1g2c18a = drift('DRIFT', 9.3, 'DriftPass');
sh1g2c18a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 479.825
D_577_ph1g2c18a = drift('DRIFT', 0.085, 'DriftPass');
ph1g2c18a = marker('BPM', 'IdentityPass'); %s= 480.11
D_578_qh1g2c18a = drift('DRIFT', 0.077, 'DriftPass');
qh1g2c18a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 480.187
D_579_ch1g2c18a = drift('DRIFT', 0.245, 'DriftPass');
ch1g2c18a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 480.707
sqhhg2c18a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 480.707
D_581_qh2g2c18a = drift('DRIFT', 0.46, 'DriftPass');
qh2g2c18a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 481.267
D_582_sh3g2c18a = drift('DRIFT', 0.19, 'DriftPass');
sh3g2c18a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 481.905
D_583_qh3g2c18a = drift('DRIFT', 0.182, 'DriftPass');
qh3g2c18a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 482.287
D_584_ph2g2c18a = drift('DRIFT', 0.073, 'DriftPass');
ph2g2c18a = marker('BPM', 'IdentityPass'); %s= 482.635
D_585_sh4g2c18a = drift('DRIFT', 0.09, 'DriftPass');
sh4g2c18a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 482.725
D_586_ch2g2c18a = drift('DRIFT', 0.248, 'DriftPass');
ch2g2c18a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 483.173
D_587_cm1g4c18a = drift('DRIFT', 3.153, 'DriftPass');
cm1g4c18a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 486.626
D_588_qm1g4c18a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c18a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 487.1
D_589_sm1g4c18a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c18a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 487.55
D_590_pm1g4c18a = drift('DRIFT', 0.569, 'DriftPass');
pm1g4c18a = marker('BPM', 'IdentityPass'); %s= 488.319
D_591_qm2g4c18a = drift('DRIFT', 0.0839999999999, 'DriftPass');
qm2g4c18a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 488.403
D_592_sm2g4c18b = drift('DRIFT', 0.184, 'DriftPass');
sm2g4c18b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 488.87
D_593_qm2g4c18b = drift('DRIFT', 0.183, 'DriftPass');
qm2g4c18b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 489.303
D_594_sm1g4c18b = drift('DRIFT', 0.504, 'DriftPass');
sm1g4c18b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 490.09
D_595_pm1g4c18b = drift('DRIFT', 0.262, 'DriftPass');
pm1g4c18b = marker('BPM', 'IdentityPass'); %s= 490.552
D_596_qm1g4c18b = drift('DRIFT', 0.088, 'DriftPass');
qm1g4c18b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 490.64
D_597_cm1g4c18b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c18b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 490.999
D_598_ql3g6c18b = drift('DRIFT', 3.773, 'DriftPass');
ql3g6c18b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 495.072
D_599_pl2g6c18b = drift('DRIFT', 0.075, 'DriftPass');
pl2g6c18b = marker('BPM', 'IdentityPass'); %s= 495.422
D_600_sl3g6c18b = drift('DRIFT', 0.088, 'DriftPass');
sl3g6c18b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 495.51
D_601_cl2g6c18b = drift('DRIFT', 0.157, 'DriftPass');
cl2g6c18b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 495.867
D_602_ql2g6c18b = drift('DRIFT', 0.208, 'DriftPass');
ql2g6c18b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 496.275
D_603_sl2g6c18b = drift('DRIFT', 0.25, 'DriftPass');
sl2g6c18b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 496.973
D_604_cl1g6c18b = drift('DRIFT', 0.132, 'DriftPass');
cl1g6c18b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 497.305
D_605_ql1g6c18b = drift('DRIFT', 0.131, 'DriftPass');
ql1g6c18b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 497.636
D_606_pl1g6c18b = drift('DRIFT', 0.075, 'DriftPass');
pl1g6c18b = marker('BPM', 'IdentityPass'); %s= 497.986
D_607_sl1g6c18b = drift('DRIFT', 0.087, 'DriftPass');
sl1g6c18b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 498.073
D_608_sl1g2c19a = drift('DRIFT', 6.6, 'DriftPass');
sl1g2c19a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 504.873
D_609_pl1g2c19a = drift('DRIFT', 0.09, 'DriftPass');
pl1g2c19a = marker('BPM', 'IdentityPass'); %s= 505.163
D_610_ql1g2c19a = drift('DRIFT', 0.073, 'DriftPass');
ql1g2c19a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 505.236
D_611_cl1g2c19a = drift('DRIFT', 0.131, 'DriftPass');
cl1g2c19a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 505.642
D_612_sl2g2c19a = drift('DRIFT', 0.131, 'DriftPass');
sl2g2c19a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 505.973
D_613_ql2g2c19a = drift('DRIFT', 0.25, 'DriftPass');
ql2g2c19a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 506.423
D_614_cl2g2c19a = drift('DRIFT', 0.208, 'DriftPass');
cl2g2c19a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 507.079
D_615_sl3g2c19a = drift('DRIFT', 0.158, 'DriftPass');
sl3g2c19a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 507.437
D_616_pl2g2c19a = drift('DRIFT', 0.09, 'DriftPass');
pl2g2c19a = marker('BPM', 'IdentityPass'); %s= 507.727
D_617_ql3g2c19a = drift('DRIFT', 0.0720000000001, 'DriftPass');
ql3g2c19a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 507.799
D_618_cm1g4c19a = drift('DRIFT', 3.809, 'DriftPass');
cm1g4c19a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 511.883
sqmhg4c19a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 511.883
D_620_qm1g4c19a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c19a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 512.257
D_621_sm1g4c19a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c19a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 512.707
D_622_pm1g4c19a = drift('DRIFT', 0.57, 'DriftPass');
pm1g4c19a = marker('BPM', 'IdentityPass'); %s= 513.477
D_623_qm2g4c19a = drift('DRIFT', 0.083, 'DriftPass');
qm2g4c19a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 513.56
D_624_sm2g4c19b = drift('DRIFT', 0.184, 'DriftPass');
sm2g4c19b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 514.027
D_625_qm2g4c19b = drift('DRIFT', 0.183, 'DriftPass');
qm2g4c19b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 514.46
D_626_sm1g4c19b = drift('DRIFT', 0.504, 'DriftPass');
sm1g4c19b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 515.247
D_627_pm1g4c19b = drift('DRIFT', 0.262, 'DriftPass');
pm1g4c19b = marker('BPM', 'IdentityPass'); %s= 515.709
D_628_qm1g4c19b = drift('DRIFT', 0.0880000000001, 'DriftPass');
qm1g4c19b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 515.797
D_629_cm1g4c19b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c19b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 516.156
D_630_ch2g6c19b = drift('DRIFT', 3.402, 'DriftPass');
ch2g6c19b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 519.858
D_631_sh4g6c19b = drift('DRIFT', 0.064, 'DriftPass');
sh4g6c19b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 520.222
D_632_ph2g6c19b = drift('DRIFT', 0.0899999999999, 'DriftPass');
ph2g6c19b = marker('BPM', 'IdentityPass'); %s= 520.512
D_633_qh3g6c19b = drift('DRIFT', 0.0720000000001, 'DriftPass');
qh3g6c19b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 520.584
D_634_sh3g6c19b = drift('DRIFT', 0.183, 'DriftPass');
sh3g6c19b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 521.042
D_635_qh2g6c19b = drift('DRIFT', 0.19, 'DriftPass');
qh2g6c19b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 521.432
D_636_ch1g6c19b = drift('DRIFT', 0.484, 'DriftPass');
ch1g6c19b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 522.364
D_637_qh1g6c19b = drift('DRIFT', 0.12, 'DriftPass');
qh1g6c19b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 522.684
D_638_ph1g6c19b = drift('DRIFT', 0.0780000000001, 'DriftPass');
ph1g6c19b = marker('BPM', 'IdentityPass'); %s= 523.037
D_639_sh1g6c19b = drift('DRIFT', 0.0849999999999, 'DriftPass');
sh1g6c19b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 523.122
D_640_sh1g2c20a = drift('DRIFT', 9.3, 'DriftPass');
sh1g2c20a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 532.622
D_641_ph1g2c20a = drift('DRIFT', 0.085, 'DriftPass');
ph1g2c20a = marker('BPM', 'IdentityPass'); %s= 532.907
D_642_qh1g2c20a = drift('DRIFT', 0.077, 'DriftPass');
qh1g2c20a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 532.984
D_643_ch1g2c20a = drift('DRIFT', 0.245, 'DriftPass');
ch1g2c20a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 533.504
sqhhg2c20a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 533.504
D_645_qh2g2c20a = drift('DRIFT', 0.46, 'DriftPass');
qh2g2c20a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 534.064
D_646_sh3g2c20a = drift('DRIFT', 0.19, 'DriftPass');
sh3g2c20a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 534.702
D_647_qh3g2c20a = drift('DRIFT', 0.182, 'DriftPass');
qh3g2c20a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 535.084
D_648_ph2g2c20a = drift('DRIFT', 0.073, 'DriftPass');
ph2g2c20a = marker('BPM', 'IdentityPass'); %s= 535.432
D_649_sh4g2c20a = drift('DRIFT', 0.0899999999999, 'DriftPass');
sh4g2c20a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 535.522
D_650_ch2g2c20a = drift('DRIFT', 0.248, 'DriftPass');
ch2g2c20a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 535.97
D_651_cm1g4c20a = drift('DRIFT', 3.153, 'DriftPass');
cm1g4c20a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 539.423
D_652_qm1g4c20a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c20a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 539.897
D_653_sm1g4c20a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c20a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 540.347
D_654_pm1g4c20a = drift('DRIFT', 0.57, 'DriftPass');
pm1g4c20a = marker('BPM', 'IdentityPass'); %s= 541.117
D_655_qm2g4c20a = drift('DRIFT', 0.0840000000001, 'DriftPass');
qm2g4c20a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 541.201
D_656_sm2g4c20b = drift('DRIFT', 0.183, 'DriftPass');
sm2g4c20b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 541.667
D_657_qm2g4c20b = drift('DRIFT', 0.184, 'DriftPass');
qm2g4c20b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 542.101
D_658_sm1g4c20b = drift('DRIFT', 0.503, 'DriftPass');
sm1g4c20b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 542.887
D_659_pm1g4c20b = drift('DRIFT', 0.262, 'DriftPass');
pm1g4c20b = marker('BPM', 'IdentityPass'); %s= 543.349
D_660_qm1g4c20b = drift('DRIFT', 0.088, 'DriftPass');
qm1g4c20b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 543.437
D_661_cm1g4c20b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c20b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 543.796
D_662_ql3g6c20b = drift('DRIFT', 3.774, 'DriftPass');
ql3g6c20b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 547.87
D_663_pl2g6c20b = drift('DRIFT', 0.0740000000001, 'DriftPass');
pl2g6c20b = marker('BPM', 'IdentityPass'); %s= 548.219
D_664_sl3g6c20b = drift('DRIFT', 0.0879999999999, 'DriftPass');
sl3g6c20b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 548.307
D_665_cl2g6c20b = drift('DRIFT', 0.158, 'DriftPass');
cl2g6c20b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 548.665
D_666_ql2g6c20b = drift('DRIFT', 0.208, 'DriftPass');
ql2g6c20b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 549.073
D_667_sl2g6c20b = drift('DRIFT', 0.25, 'DriftPass');
sl2g6c20b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 549.771
D_668_cl1g6c20b = drift('DRIFT', 0.131, 'DriftPass');
cl1g6c20b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 550.102
D_669_ql1g6c20b = drift('DRIFT', 0.131, 'DriftPass');
ql1g6c20b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 550.433
D_670_pl1g6c20b = drift('DRIFT', 0.075, 'DriftPass');
pl1g6c20b = marker('BPM', 'IdentityPass'); %s= 550.783
D_671_sl1g6c20b = drift('DRIFT', 0.088, 'DriftPass');
sl1g6c20b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 550.871
D_672_sl1g2c21a = drift('DRIFT', 6.6, 'DriftPass');
sl1g2c21a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 557.671
D_673_pl1g2c21a = drift('DRIFT', 0.09, 'DriftPass');
pl1g2c21a = marker('BPM', 'IdentityPass'); %s= 557.961
D_674_ql1g2c21a = drift('DRIFT', 0.072, 'DriftPass');
ql1g2c21a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 558.033
D_675_cl1g2c21a = drift('DRIFT', 0.131, 'DriftPass');
cl1g2c21a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 558.439
D_676_sl2g2c21a = drift('DRIFT', 0.132, 'DriftPass');
sl2g2c21a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 558.771
D_677_ql2g2c21a = drift('DRIFT', 0.25, 'DriftPass');
ql2g2c21a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 559.221
D_678_cl2g2c21a = drift('DRIFT', 0.208, 'DriftPass');
cl2g2c21a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 559.877
D_679_sl3g2c21a = drift('DRIFT', 0.157, 'DriftPass');
sl3g2c21a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 560.234
D_680_pl2g2c21a = drift('DRIFT', 0.09, 'DriftPass');
pl2g2c21a = marker('BPM', 'IdentityPass'); %s= 560.524
D_681_ql3g2c21a = drift('DRIFT', 0.073, 'DriftPass');
ql3g2c21a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 560.597
D_682_cm1g4c21a = drift('DRIFT', 3.808, 'DriftPass');
cm1g4c21a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 564.68
sqmhg4c21a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 564.68
D_684_qm1g4c21a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c21a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 565.054
D_685_sm1g4c21a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c21a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 565.504
D_686_pm1g4c21a = drift('DRIFT', 0.57, 'DriftPass');
pm1g4c21a = marker('BPM', 'IdentityPass'); %s= 566.274
D_687_qm2g4c21a = drift('DRIFT', 0.0839999999999, 'DriftPass');
qm2g4c21a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 566.358
D_688_sm2g4c21b = drift('DRIFT', 0.183, 'DriftPass');
sm2g4c21b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 566.824
D_689_qm2g4c21b = drift('DRIFT', 0.184, 'DriftPass');
qm2g4c21b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 567.258
D_690_sm1g4c21b = drift('DRIFT', 0.503, 'DriftPass');
sm1g4c21b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 568.044
D_691_pm1g4c21b = drift('DRIFT', 0.262, 'DriftPass');
pm1g4c21b = marker('BPM', 'IdentityPass'); %s= 568.506
D_692_qm1g4c21b = drift('DRIFT', 0.0880000000001, 'DriftPass');
qm1g4c21b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 568.594
D_693_cm1g4c21b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c21b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 568.953
D_694_ch2g6c21b = drift('DRIFT', 3.403, 'DriftPass');
ch2g6c21b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 572.656
D_695_sh4g6c21b = drift('DRIFT', 0.063, 'DriftPass');
sh4g6c21b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 573.019
D_696_ph2g6c21b = drift('DRIFT', 0.0899999999999, 'DriftPass');
ph2g6c21b = marker('BPM', 'IdentityPass'); %s= 573.309
D_697_qh3g6c21b = drift('DRIFT', 0.0730000000001, 'DriftPass');
qh3g6c21b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 573.382
D_698_sh3g6c21b = drift('DRIFT', 0.182, 'DriftPass');
sh3g6c21b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 573.839
D_699_qh2g6c21b = drift('DRIFT', 0.19, 'DriftPass');
qh2g6c21b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 574.229
D_700_ch1g6c21b = drift('DRIFT', 0.485, 'DriftPass');
ch1g6c21b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 575.162
D_701_qh1g6c21b = drift('DRIFT', 0.12, 'DriftPass');
qh1g6c21b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 575.482
D_702_ph1g6c21b = drift('DRIFT', 0.077, 'DriftPass');
ph1g6c21b = marker('BPM', 'IdentityPass'); %s= 575.834
D_703_sh1g6c21b = drift('DRIFT', 0.085, 'DriftPass');
sh1g6c21b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 575.919
D_704_sh1g2c22a = drift('DRIFT', 9.3, 'DriftPass');
sh1g2c22a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 585.419
D_705_ph1g2c22a = drift('DRIFT', 0.0849999999999, 'DriftPass');
ph1g2c22a = marker('BPM', 'IdentityPass'); %s= 585.704
D_706_qh1g2c22a = drift('DRIFT', 0.0780000000001, 'DriftPass');
qh1g2c22a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 585.782
D_707_ch1g2c22a = drift('DRIFT', 0.245, 'DriftPass');
ch1g2c22a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 586.302
sqhhg2c22a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 586.302
D_709_qh2g2c22a = drift('DRIFT', 0.459, 'DriftPass');
qh2g2c22a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 586.861
D_710_sh3g2c22a = drift('DRIFT', 0.19, 'DriftPass');
sh3g2c22a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 587.499
D_711_qh3g2c22a = drift('DRIFT', 0.183, 'DriftPass');
qh3g2c22a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 587.882
D_712_ph2g2c22a = drift('DRIFT', 0.072, 'DriftPass');
ph2g2c22a = marker('BPM', 'IdentityPass'); %s= 588.229
D_713_sh4g2c22a = drift('DRIFT', 0.0899999999999, 'DriftPass');
sh4g2c22a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 588.319
D_714_ch2g2c22a = drift('DRIFT', 0.249, 'DriftPass');
ch2g2c22a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 588.768
D_715_cm1g4c22a = drift('DRIFT', 3.152, 'DriftPass');
cm1g4c22a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 592.22
D_716_qm1g4c22a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c22a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 592.694
D_717_sm1g4c22a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c22a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 593.144
D_718_pm1g4c22a = drift('DRIFT', 0.57, 'DriftPass');
pm1g4c22a = marker('BPM', 'IdentityPass'); %s= 593.914
D_719_qm2g4c22a = drift('DRIFT', 0.0839999999999, 'DriftPass');
qm2g4c22a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 593.998
D_720_sm2g4c22b = drift('DRIFT', 0.183, 'DriftPass');
sm2g4c22b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 594.464
D_721_qm2g4c22b = drift('DRIFT', 0.184, 'DriftPass');
qm2g4c22b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 594.898
D_722_sm1g4c22b = drift('DRIFT', 0.503, 'DriftPass');
sm1g4c22b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 595.684
D_723_pm1g4c22b = drift('DRIFT', 0.262, 'DriftPass');
pm1g4c22b = marker('BPM', 'IdentityPass'); %s= 596.146
D_724_qm1g4c22b = drift('DRIFT', 0.0880000000001, 'DriftPass');
qm1g4c22b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 596.234
D_725_cm1g4c22b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c22b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 596.593
D_726_ql3g6c22b = drift('DRIFT', 3.774, 'DriftPass');
ql3g6c22b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 600.667
D_727_pl2g6c22b = drift('DRIFT', 0.074, 'DriftPass');
pl2g6c22b = marker('BPM', 'IdentityPass'); %s= 601.016
D_728_sl3g6c22b = drift('DRIFT', 0.088, 'DriftPass');
sl3g6c22b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 601.104
D_729_cl2g6c22b = drift('DRIFT', 0.158, 'DriftPass');
cl2g6c22b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 601.462
D_730_ql2g6c22b = drift('DRIFT', 0.208, 'DriftPass');
ql2g6c22b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 601.87
D_731_sl2g6c22b = drift('DRIFT', 0.25, 'DriftPass');
sl2g6c22b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 602.568
D_732_cl1g6c22b = drift('DRIFT', 0.131, 'DriftPass');
cl1g6c22b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 602.899
D_733_ql1g6c22b = drift('DRIFT', 0.131, 'DriftPass');
ql1g6c22b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 603.23
D_734_pl1g6c22b = drift('DRIFT', 0.075, 'DriftPass');
pl1g6c22b = marker('BPM', 'IdentityPass'); %s= 603.58
D_735_sl1g6c22b = drift('DRIFT', 0.088, 'DriftPass');
sl1g6c22b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 603.668
D_736_sl1g2c23a = drift('DRIFT', 6.6, 'DriftPass');
sl1g2c23a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 610.468
D_737_pl1g2c23a = drift('DRIFT', 0.09, 'DriftPass');
pl1g2c23a = marker('BPM', 'IdentityPass'); %s= 610.758
D_738_ql1g2c23a = drift('DRIFT', 0.072, 'DriftPass');
ql1g2c23a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 610.83
D_739_cl1g2c23a = drift('DRIFT', 0.132, 'DriftPass');
cl1g2c23a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 611.237
D_740_sl2g2c23a = drift('DRIFT', 0.131, 'DriftPass');
sl2g2c23a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 611.568
D_741_ql2g2c23a = drift('DRIFT', 0.25, 'DriftPass');
ql2g2c23a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 612.018
D_742_cl2g2c23a = drift('DRIFT', 0.208, 'DriftPass');
cl2g2c23a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 612.674
D_743_sl3g2c23a = drift('DRIFT', 0.157, 'DriftPass');
sl3g2c23a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 613.031
D_744_pl2g2c23a = drift('DRIFT', 0.09, 'DriftPass');
pl2g2c23a = marker('BPM', 'IdentityPass'); %s= 613.321
D_745_ql3g2c23a = drift('DRIFT', 0.073, 'DriftPass');
ql3g2c23a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 613.394
D_746_cm1g4c23a = drift('DRIFT', 3.808, 'DriftPass');
cm1g4c23a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 617.477
sqmhg4c23a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 617.477
D_748_qm1g4c23a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c23a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 617.851
D_749_sm1g4c23a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c23a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 618.301
D_750_pm1g4c23a = drift('DRIFT', 0.57, 'DriftPass');
pm1g4c23a = marker('BPM', 'IdentityPass'); %s= 619.071
D_751_qm2g4c23a = drift('DRIFT', 0.0839999999999, 'DriftPass');
qm2g4c23a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 619.155
D_752_sm2g4c23b = drift('DRIFT', 0.183, 'DriftPass');
sm2g4c23b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 619.621
D_753_qm2g4c23b = drift('DRIFT', 0.184, 'DriftPass');
qm2g4c23b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 620.055
D_754_sm1g4c23b = drift('DRIFT', 0.503, 'DriftPass');
sm1g4c23b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 620.841
D_755_pm1g4c23b = drift('DRIFT', 0.263, 'DriftPass');
pm1g4c23b = marker('BPM', 'IdentityPass'); %s= 621.304
D_756_qm1g4c23b = drift('DRIFT', 0.087, 'DriftPass');
qm1g4c23b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 621.391
D_757_cm1g4c23b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c23b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 621.75
D_758_ch2g6c23b = drift('DRIFT', 3.403, 'DriftPass');
ch2g6c23b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 625.453
D_759_sh4g6c23b = drift('DRIFT', 0.0629999999999, 'DriftPass');
sh4g6c23b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 625.816
D_760_ph2g6c23b = drift('DRIFT', 0.09, 'DriftPass');
ph2g6c23b = marker('BPM', 'IdentityPass'); %s= 626.106
D_761_qh3g6c23b = drift('DRIFT', 0.073, 'DriftPass');
qh3g6c23b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 626.179
D_762_sh3g6c23b = drift('DRIFT', 0.182, 'DriftPass');
sh3g6c23b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 626.636
D_763_qh2g6c23b = drift('DRIFT', 0.19, 'DriftPass');
qh2g6c23b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 627.026
D_764_ch1g6c23b = drift('DRIFT', 0.485, 'DriftPass');
ch1g6c23b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 627.959
D_765_qh1g6c23b = drift('DRIFT', 0.12, 'DriftPass');
qh1g6c23b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 628.279
D_766_ph1g6c23b = drift('DRIFT', 0.077, 'DriftPass');
ph1g6c23b = marker('BPM', 'IdentityPass'); %s= 628.631
D_767_sh1g6c23b = drift('DRIFT', 0.085, 'DriftPass');
sh1g6c23b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 628.716
D_768_sh1g2c24a = drift('DRIFT', 9.3, 'DriftPass');
sh1g2c24a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 638.216
D_769_ph1g2c24a = drift('DRIFT', 0.0849999999999, 'DriftPass');
ph1g2c24a = marker('BPM', 'IdentityPass'); %s= 638.501
D_770_qh1g2c24a = drift('DRIFT', 0.0780000000001, 'DriftPass');
qh1g2c24a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 638.579
D_771_ch1g2c24a = drift('DRIFT', 0.245, 'DriftPass');
ch1g2c24a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 639.099
sqhhg2c24a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 639.099
D_773_qh2g2c24a = drift('DRIFT', 0.459, 'DriftPass');
qh2g2c24a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 639.658
D_774_sh3g2c24a = drift('DRIFT', 0.19, 'DriftPass');
sh3g2c24a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 640.296
D_775_qh3g2c24a = drift('DRIFT', 0.183, 'DriftPass');
qh3g2c24a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 640.679
D_776_ph2g2c24a = drift('DRIFT', 0.072, 'DriftPass');
ph2g2c24a = marker('BPM', 'IdentityPass'); %s= 641.026
D_777_sh4g2c24a = drift('DRIFT', 0.09, 'DriftPass');
sh4g2c24a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 641.116
D_778_ch2g2c24a = drift('DRIFT', 0.249, 'DriftPass');
ch2g2c24a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 641.565
D_779_cm1g4c24a = drift('DRIFT', 3.152, 'DriftPass');
cm1g4c24a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 645.017
D_780_qm1g4c24a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c24a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 645.491
D_781_sm1g4c24a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c24a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 645.941
D_782_pm1g4c24a = drift('DRIFT', 0.57, 'DriftPass');
pm1g4c24a = marker('BPM', 'IdentityPass'); %s= 646.711
D_783_qm2g4c24a = drift('DRIFT', 0.0839999999999, 'DriftPass');
qm2g4c24a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 646.795
D_784_sm2g4c24b = drift('DRIFT', 0.183, 'DriftPass');
sm2g4c24b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 647.261
D_785_qm2g4c24b = drift('DRIFT', 0.184, 'DriftPass');
qm2g4c24b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 647.695
D_786_sm1g4c24b = drift('DRIFT', 0.503, 'DriftPass');
sm1g4c24b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 648.481
D_787_pm1g4c24b = drift('DRIFT', 0.263, 'DriftPass');
pm1g4c24b = marker('BPM', 'IdentityPass'); %s= 648.944
D_788_qm1g4c24b = drift('DRIFT', 0.087, 'DriftPass');
qm1g4c24b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 649.031
D_789_cm1g4c24b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c24b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 649.39
D_790_ql3g6c24b = drift('DRIFT', 3.774, 'DriftPass');
ql3g6c24b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 653.464
D_791_pl2g6c24b = drift('DRIFT', 0.0749999999999, 'DriftPass');
pl2g6c24b = marker('BPM', 'IdentityPass'); %s= 653.814
D_792_sl3g6c24b = drift('DRIFT', 0.087, 'DriftPass');
sl3g6c24b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 653.901
D_793_cl2g6c24b = drift('DRIFT', 0.158, 'DriftPass');
cl2g6c24b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 654.259
D_794_ql2g6c24b = drift('DRIFT', 0.208, 'DriftPass');
ql2g6c24b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 654.667
D_795_sl2g6c24b = drift('DRIFT', 0.25, 'DriftPass');
sl2g6c24b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 655.365
D_796_cl1g6c24b = drift('DRIFT', 0.131, 'DriftPass');
cl1g6c24b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 655.696
D_797_ql1g6c24b = drift('DRIFT', 0.132, 'DriftPass');
ql1g6c24b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 656.028
D_798_pl1g6c24b = drift('DRIFT', 0.074, 'DriftPass');
pl1g6c24b = marker('BPM', 'IdentityPass'); %s= 656.377
D_799_sl1g6c24b = drift('DRIFT', 0.088, 'DriftPass');
sl1g6c24b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 656.465
D_800_sl1g2c25a = drift('DRIFT', 6.6, 'DriftPass');
sl1g2c25a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 663.265
D_801_pl1g2c25a = drift('DRIFT', 0.0899999999999, 'DriftPass');
pl1g2c25a = marker('BPM', 'IdentityPass'); %s= 663.555
D_802_ql1g2c25a = drift('DRIFT', 0.0730000000001, 'DriftPass');
ql1g2c25a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 663.628
D_803_cl1g2c25a = drift('DRIFT', 0.131, 'DriftPass');
cl1g2c25a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 664.034
D_804_sl2g2c25a = drift('DRIFT', 0.131, 'DriftPass');
sl2g2c25a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 664.365
D_805_ql2g2c25a = drift('DRIFT', 0.25, 'DriftPass');
ql2g2c25a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 664.815
D_806_cl2g2c25a = drift('DRIFT', 0.208, 'DriftPass');
cl2g2c25a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 665.471
D_807_sl3g2c25a = drift('DRIFT', 0.158, 'DriftPass');
sl3g2c25a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 665.829
D_808_pl2g2c25a = drift('DRIFT', 0.09, 'DriftPass');
pl2g2c25a = marker('BPM', 'IdentityPass'); %s= 666.119
D_809_ql3g2c25a = drift('DRIFT', 0.072, 'DriftPass');
ql3g2c25a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 666.191
D_810_cm1g4c25a = drift('DRIFT', 3.809, 'DriftPass');
cm1g4c25a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 670.275
sqmhg4c25a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 670.275
D_812_qm1g4c25a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c25a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 670.649
D_813_sm1g4c25a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c25a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 671.099
D_814_pm1g4c25a = drift('DRIFT', 0.569, 'DriftPass');
pm1g4c25a = marker('BPM', 'IdentityPass'); %s= 671.868
D_815_qm2g4c25a = drift('DRIFT', 0.0839999999999, 'DriftPass');
qm2g4c25a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 671.952
D_816_sm2g4c25b = drift('DRIFT', 0.184, 'DriftPass');
sm2g4c25b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 672.419
D_817_qm2g4c25b = drift('DRIFT', 0.183, 'DriftPass');
qm2g4c25b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 672.852
D_818_sm1g4c25b = drift('DRIFT', 0.504, 'DriftPass');
sm1g4c25b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 673.639
D_819_pm1g4c25b = drift('DRIFT', 0.262, 'DriftPass');
pm1g4c25b = marker('BPM', 'IdentityPass'); %s= 674.101
D_820_qm1g4c25b = drift('DRIFT', 0.088, 'DriftPass');
qm1g4c25b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 674.189
D_821_cm1g4c25b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c25b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 674.548
D_822_ch2g6c25b = drift('DRIFT', 3.402, 'DriftPass');
ch2g6c25b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 678.25
D_823_sh4g6c25b = drift('DRIFT', 0.064, 'DriftPass');
sh4g6c25b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 678.614
D_824_ph2g6c25b = drift('DRIFT', 0.0890000000001, 'DriftPass');
ph2g6c25b = marker('BPM', 'IdentityPass'); %s= 678.903
D_825_qh3g6c25b = drift('DRIFT', 0.073, 'DriftPass');
qh3g6c25b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 678.976
D_826_sh3g6c25b = drift('DRIFT', 0.183, 'DriftPass');
sh3g6c25b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 679.434
D_827_qh2g6c25b = drift('DRIFT', 0.19, 'DriftPass');
qh2g6c25b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 679.824
D_828_ch1g6c25b = drift('DRIFT', 0.484, 'DriftPass');
ch1g6c25b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 680.756
D_829_qh1g6c25b = drift('DRIFT', 0.12, 'DriftPass');
qh1g6c25b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 681.076
D_830_ph1g6c25b = drift('DRIFT', 0.077, 'DriftPass');
ph1g6c25b = marker('BPM', 'IdentityPass'); %s= 681.428
D_831_sh1g6c25b = drift('DRIFT', 0.086, 'DriftPass');
sh1g6c25b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 681.514
D_832_sh1g2c26a = drift('DRIFT', 9.3, 'DriftPass');
sh1g2c26a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 691.014
D_833_ph1g2c26a = drift('DRIFT', 0.0849999999999, 'DriftPass');
ph1g2c26a = marker('BPM', 'IdentityPass'); %s= 691.299
D_834_qh1g2c26a = drift('DRIFT', 0.077, 'DriftPass');
qh1g2c26a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 691.376
D_835_ch1g2c26a = drift('DRIFT', 0.245, 'DriftPass');
ch1g2c26a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 691.896
sqhhg2c26a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 691.896
D_837_qh2g2c26a = drift('DRIFT', 0.46, 'DriftPass');
qh2g2c26a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 692.456
D_838_sh3g2c26a = drift('DRIFT', 0.19, 'DriftPass');
sh3g2c26a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 693.094
D_839_qh3g2c26a = drift('DRIFT', 0.182, 'DriftPass');
qh3g2c26a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 693.476
D_840_ph2g2c26a = drift('DRIFT', 0.073, 'DriftPass');
ph2g2c26a = marker('BPM', 'IdentityPass'); %s= 693.824
D_841_sh4g2c26a = drift('DRIFT', 0.09, 'DriftPass');
sh4g2c26a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 693.914
D_842_ch2g2c26a = drift('DRIFT', 0.248, 'DriftPass');
ch2g2c26a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 694.362
D_843_cm1g4c26a = drift('DRIFT', 3.153, 'DriftPass');
cm1g4c26a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 697.815
D_844_qm1g4c26a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c26a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 698.289
D_845_sm1g4c26a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c26a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 698.739
D_846_pm1g4c26a = drift('DRIFT', 0.569, 'DriftPass');
pm1g4c26a = marker('BPM', 'IdentityPass'); %s= 699.508
D_847_qm2g4c26a = drift('DRIFT', 0.0839999999999, 'DriftPass');
qm2g4c26a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 699.592
D_848_sm2g4c26b = drift('DRIFT', 0.184, 'DriftPass');
sm2g4c26b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 700.059
D_849_qm2g4c26b = drift('DRIFT', 0.183, 'DriftPass');
qm2g4c26b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 700.492
D_850_sm1g4c26b = drift('DRIFT', 0.504, 'DriftPass');
sm1g4c26b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 701.279
D_851_pm1g4c26b = drift('DRIFT', 0.262, 'DriftPass');
pm1g4c26b = marker('BPM', 'IdentityPass'); %s= 701.741
D_852_qm1g4c26b = drift('DRIFT', 0.088, 'DriftPass');
qm1g4c26b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 701.829
D_853_cm1g4c26b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c26b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 702.188
D_854_ql3g6c26b = drift('DRIFT', 3.773, 'DriftPass');
ql3g6c26b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 706.261
D_855_pl2g6c26b = drift('DRIFT', 0.075, 'DriftPass');
pl2g6c26b = marker('BPM', 'IdentityPass'); %s= 706.611
D_856_sl3g6c26b = drift('DRIFT', 0.088, 'DriftPass');
sl3g6c26b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 706.699
D_857_cl2g6c26b = drift('DRIFT', 0.157, 'DriftPass');
cl2g6c26b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 707.056
D_858_ql2g6c26b = drift('DRIFT', 0.208, 'DriftPass');
ql2g6c26b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 707.464
D_859_sl2g6c26b = drift('DRIFT', 0.25, 'DriftPass');
sl2g6c26b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 708.162
D_860_cl1g6c26b = drift('DRIFT', 0.131, 'DriftPass');
cl1g6c26b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 708.493
D_861_ql1g6c26b = drift('DRIFT', 0.132, 'DriftPass');
ql1g6c26b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 708.825
D_862_pl1g6c26b = drift('DRIFT', 0.0749999999999, 'DriftPass');
pl1g6c26b = marker('BPM', 'IdentityPass'); %s= 709.175
D_863_sl1g6c26b = drift('DRIFT', 0.087, 'DriftPass');
sl1g6c26b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 709.262
D_864_sl1g2c27a = drift('DRIFT', 6.6, 'DriftPass');
sl1g2c27a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 716.062
D_865_pl1g2c27a = drift('DRIFT', 0.09, 'DriftPass');
pl1g2c27a = marker('BPM', 'IdentityPass'); %s= 716.352
D_866_ql1g2c27a = drift('DRIFT', 0.0730000000001, 'DriftPass');
ql1g2c27a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 716.425
D_867_cl1g2c27a = drift('DRIFT', 0.131, 'DriftPass');
cl1g2c27a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 716.831
D_868_sl2g2c27a = drift('DRIFT', 0.131, 'DriftPass');
sl2g2c27a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 717.162
D_869_ql2g2c27a = drift('DRIFT', 0.25, 'DriftPass');
ql2g2c27a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 717.612
D_870_cl2g2c27a = drift('DRIFT', 0.208, 'DriftPass');
cl2g2c27a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 718.268
D_871_sl3g2c27a = drift('DRIFT', 0.158, 'DriftPass');
sl3g2c27a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 718.626
D_872_pl2g2c27a = drift('DRIFT', 0.09, 'DriftPass');
pl2g2c27a = marker('BPM', 'IdentityPass'); %s= 718.916
D_873_ql3g2c27a = drift('DRIFT', 0.072, 'DriftPass');
ql3g2c27a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 718.988
D_874_cm1g4c27a = drift('DRIFT', 3.809, 'DriftPass');
cm1g4c27a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 723.072
sqmhg4c27a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 723.072
D_876_qm1g4c27a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c27a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 723.446
D_877_sm1g4c27a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c27a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 723.896
D_878_pm1g4c27a = drift('DRIFT', 0.569, 'DriftPass');
pm1g4c27a = marker('BPM', 'IdentityPass'); %s= 724.665
D_879_qm2g4c27a = drift('DRIFT', 0.0840000000001, 'DriftPass');
qm2g4c27a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 724.749
D_880_sm2g4c27b = drift('DRIFT', 0.184, 'DriftPass');
sm2g4c27b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 725.216
D_881_qm2g4c27b = drift('DRIFT', 0.183, 'DriftPass');
qm2g4c27b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 725.649
D_882_sm1g4c27b = drift('DRIFT', 0.504, 'DriftPass');
sm1g4c27b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 726.436
D_883_pm1g4c27b = drift('DRIFT', 0.262, 'DriftPass');
pm1g4c27b = marker('BPM', 'IdentityPass'); %s= 726.898
D_884_qm1g4c27b = drift('DRIFT', 0.088, 'DriftPass');
qm1g4c27b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 726.986
D_885_cm1g4c27b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c27b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 727.345
D_886_ch2g6c27b = drift('DRIFT', 3.402, 'DriftPass');
ch2g6c27b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 731.047
D_887_sh4g6c27b = drift('DRIFT', 0.064, 'DriftPass');
sh4g6c27b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 731.411
D_888_ph2g6c27b = drift('DRIFT', 0.0890000000001, 'DriftPass');
ph2g6c27b = marker('BPM', 'IdentityPass'); %s= 731.7
D_889_qh3g6c27b = drift('DRIFT', 0.073, 'DriftPass');
qh3g6c27b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 731.773
D_890_sh3g6c27b = drift('DRIFT', 0.183, 'DriftPass');
sh3g6c27b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 732.231
D_891_qh2g6c27b = drift('DRIFT', 0.19, 'DriftPass');
qh2g6c27b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 732.621
D_892_ch1g6c27b = drift('DRIFT', 0.484, 'DriftPass');
ch1g6c27b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 733.553
D_893_qh1g6c27b = drift('DRIFT', 0.12, 'DriftPass');
qh1g6c27b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 733.873
D_894_ph1g6c27b = drift('DRIFT', 0.077, 'DriftPass');
ph1g6c27b = marker('BPM', 'IdentityPass'); %s= 734.225
D_895_sh1g6c27b = drift('DRIFT', 0.0859999999999, 'DriftPass');
sh1g6c27b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 734.311
D_896_sh1g2c28a = drift('DRIFT', 9.3, 'DriftPass');
sh1g2c28a = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 743.811
D_897_ph1g2c28a = drift('DRIFT', 0.085, 'DriftPass');
ph1g2c28a = marker('BPM', 'IdentityPass'); %s= 744.096
D_898_qh1g2c28a = drift('DRIFT', 0.077, 'DriftPass');
qh1g2c28a = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 744.173
D_899_ch1g2c28a = drift('DRIFT', 0.245, 'DriftPass');
ch1g2c28a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 744.693
sqhhg2c28a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 744.693
D_901_qh2g2c28a = drift('DRIFT', 0.46, 'DriftPass');
qh2g2c28a = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 745.253
D_902_sh3g2c28a = drift('DRIFT', 0.19, 'DriftPass');
sh3g2c28a = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 745.891
D_903_qh3g2c28a = drift('DRIFT', 0.182, 'DriftPass');
qh3g2c28a = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 746.273
D_904_ph2g2c28a = drift('DRIFT', 0.073, 'DriftPass');
ph2g2c28a = marker('BPM', 'IdentityPass'); %s= 746.621
D_905_sh4g2c28a = drift('DRIFT', 0.0899999999999, 'DriftPass');
sh4g2c28a = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 746.711
D_906_ch2g2c28a = drift('DRIFT', 0.248, 'DriftPass');
ch2g2c28a = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 747.159
D_907_cm1g4c28a = drift('DRIFT', 3.153, 'DriftPass');
cm1g4c28a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 750.612
D_908_qm1g4c28a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c28a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 751.086
D_909_sm1g4c28a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c28a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 751.536
D_910_pm1g4c28a = drift('DRIFT', 0.569, 'DriftPass');
pm1g4c28a = marker('BPM', 'IdentityPass'); %s= 752.305
D_911_qm2g4c28a = drift('DRIFT', 0.0840000000001, 'DriftPass');
qm2g4c28a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 752.389
D_912_sm2g4c28b = drift('DRIFT', 0.184, 'DriftPass');
sm2g4c28b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 752.856
D_913_qm2g4c28b = drift('DRIFT', 0.183, 'DriftPass');
qm2g4c28b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 753.289
D_914_sm1g4c28b = drift('DRIFT', 0.504, 'DriftPass');
sm1g4c28b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 754.076
D_915_pm1g4c28b = drift('DRIFT', 0.262, 'DriftPass');
pm1g4c28b = marker('BPM', 'IdentityPass'); %s= 754.538
D_916_qm1g4c28b = drift('DRIFT', 0.088, 'DriftPass');
qm1g4c28b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 754.626
D_917_cm1g4c28b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c28b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 754.985
D_918_ql3g6c28b = drift('DRIFT', 3.773, 'DriftPass');
ql3g6c28b = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 759.058
D_919_pl2g6c28b = drift('DRIFT', 0.075, 'DriftPass');
pl2g6c28b = marker('BPM', 'IdentityPass'); %s= 759.408
D_920_sl3g6c28b = drift('DRIFT', 0.088, 'DriftPass');
sl3g6c28b = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 759.496
D_921_cl2g6c28b = drift('DRIFT', 0.157, 'DriftPass');
cl2g6c28b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 759.853
D_922_ql2g6c28b = drift('DRIFT', 0.208, 'DriftPass');
ql2g6c28b = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 760.261
D_923_sl2g6c28b = drift('DRIFT', 0.25, 'DriftPass');
sl2g6c28b = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 760.959
D_924_cl1g6c28b = drift('DRIFT', 0.132, 'DriftPass');
cl1g6c28b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 761.291
D_925_ql1g6c28b = drift('DRIFT', 0.131, 'DriftPass');
ql1g6c28b = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 761.622
D_926_pl1g6c28b = drift('DRIFT', 0.0749999999999, 'DriftPass');
pl1g6c28b = marker('BPM', 'IdentityPass'); %s= 761.972
D_927_sl1g6c28b = drift('DRIFT', 0.087, 'DriftPass');
sl1g6c28b = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 762.059
D_928_sl1g2c29a = drift('DRIFT', 6.6, 'DriftPass');
sl1g2c29a = sextupole('SEXT', 0.2, -0.97877, 'StrMPoleSymplectic4Pass'); %s= 768.859
D_929_pl1g2c29a = drift('DRIFT', 0.09, 'DriftPass');
pl1g2c29a = marker('BPM', 'IdentityPass'); %s= 769.149
D_930_ql1g2c29a = drift('DRIFT', 0.073, 'DriftPass');
ql1g2c29a = quadrupole('QUAD', 0.275, -1.56216, 'StrMPoleSymplectic4Pass'); %s= 769.222
D_931_cl1g2c29a = drift('DRIFT', 0.131, 'DriftPass');
cl1g2c29a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 769.628
D_932_sl2g2c29a = drift('DRIFT', 0.131, 'DriftPass');
sl2g2c29a = sextupole('SEXT', 0.2, 12.9841, 'StrMPoleSymplectic4Pass'); %s= 769.959
D_933_ql2g2c29a = drift('DRIFT', 0.25, 'DriftPass');
ql2g2c29a = quadrupole('QUAD', 0.448, 1.81307, 'StrMPoleSymplectic4Pass'); %s= 770.409
D_934_cl2g2c29a = drift('DRIFT', 0.209, 'DriftPass');
cl2g2c29a = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 771.066
D_935_sl3g2c29a = drift('DRIFT', 0.157, 'DriftPass');
sl3g2c29a = sextupole('SEXT', 0.2, -14.1309, 'StrMPoleSymplectic4Pass'); %s= 771.423
D_936_pl2g2c29a = drift('DRIFT', 0.0899999999999, 'DriftPass');
pl2g2c29a = marker('BPM', 'IdentityPass'); %s= 771.713
D_937_ql3g2c29a = drift('DRIFT', 0.0730000000001, 'DriftPass');
ql3g2c29a = quadrupole('QUAD', 0.275, -1.48928, 'StrMPoleSymplectic4Pass'); %s= 771.786
D_938_cm1g4c29a = drift('DRIFT', 3.808, 'DriftPass');
cm1g4c29a = corrector('COR', 0.0, [0 0], 'CorrectorPass'); %s= 775.869
sqmhg4c29a = quadrupole('QUAD', 0.1, 0, 'StrMPoleSymplectic4Pass'); %s= 775.869
D_940_qm1g4c29a = drift('DRIFT', 0.274, 'DriftPass');
qm1g4c29a = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 776.243
D_941_sm1g4c29a = drift('DRIFT', 0.2, 'DriftPass');
sm1g4c29a = sextupole('SEXT', 0.2, -12.0655, 'StrMPoleSymplectic4Pass'); %s= 776.693
D_942_pm1g4c29a = drift('DRIFT', 0.57, 'DriftPass');
pm1g4c29a = marker('BPM', 'IdentityPass'); %s= 777.463
D_943_qm2g4c29a = drift('DRIFT', 0.0840000000001, 'DriftPass');
qm2g4c29a = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 777.547
D_944_sm2g4c29b = drift('DRIFT', 0.183, 'DriftPass');
sm2g4c29b = sextupole('SEXT', 0.25, 14.35785, 'StrMPoleSymplectic4Pass'); %s= 778.013
D_945_qm2g4c29b = drift('DRIFT', 0.184, 'DriftPass');
qm2g4c29b = quadrupole('QUAD', 0.283, 1.2223, 'StrMPoleSymplectic4Pass'); %s= 778.447
D_946_sm1g4c29b = drift('DRIFT', 0.503, 'DriftPass');
sm1g4c29b = sextupole('SEXT', 0.2, -13.04745, 'StrMPoleSymplectic4Pass'); %s= 779.233
D_947_pm1g4c29b = drift('DRIFT', 0.262, 'DriftPass');
pm1g4c29b = marker('BPM', 'IdentityPass'); %s= 779.695
D_948_qm1g4c29b = drift('DRIFT', 0.088, 'DriftPass');
qm1g4c29b = quadrupole('QUAD', 0.25, -0.803148, 'StrMPoleSymplectic4Pass'); %s= 779.783
D_949_cm1g4c29b = drift('DRIFT', 0.109, 'DriftPass');
cm1g4c29b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 780.142
D_950_ch2g6c29b = drift('DRIFT', 3.402, 'DriftPass');
ch2g6c29b = corrector('COR', 0.3, [0 0], 'CorrectorPass'); %s= 783.844
D_951_sh4g6c29b = drift('DRIFT', 0.064, 'DriftPass');
sh4g6c29b = sextupole('SEXT', 0.2, -10.24345, 'StrMPoleSymplectic4Pass'); %s= 784.208
D_952_ph2g6c29b = drift('DRIFT', 0.09, 'DriftPass');
ph2g6c29b = marker('BPM', 'IdentityPass'); %s= 784.498
D_953_qh3g6c29b = drift('DRIFT', 0.073, 'DriftPass');
qh3g6c29b = quadrupole('QUAD', 0.275, -1.70755, 'StrMPoleSymplectic4Pass'); %s= 784.571
D_954_sh3g6c29b = drift('DRIFT', 0.182, 'DriftPass');
sh3g6c29b = sextupole('SEXT', 0.2, -2.07785, 'StrMPoleSymplectic4Pass'); %s= 785.028
D_955_qh2g6c29b = drift('DRIFT', 0.19, 'DriftPass');
qh2g6c29b = quadrupole('QUAD', 0.448, 1.47765, 'StrMPoleSymplectic4Pass'); %s= 785.418
D_956_ch1g6c29b = drift('DRIFT', 0.485, 'DriftPass');
ch1g6c29b = corrector('COR', 0.2, [0 0], 'CorrectorPass'); %s= 786.351
D_957_qh1g6c29b = drift('DRIFT', 0.12, 'DriftPass');
qh1g6c29b = quadrupole('QUAD', 0.275, -0.633004, 'StrMPoleSymplectic4Pass'); %s= 786.671
D_958_ph1g6c29b = drift('DRIFT', 0.077, 'DriftPass');
ph1g6c29b = marker('BPM', 'IdentityPass'); %s= 787.023
D_959_sh1g6c29b = drift('DRIFT', 0.0849999999999, 'DriftPass');
sh1g6c29b = sextupole('SEXT', 0.2, 12.09885, 'StrMPoleSymplectic4Pass'); %s= 787.108
LV2SR= [ D_0_sh1g2c30a sh1g2c30a D_1_ph1g2c30a ph1g2c30a D_2_qh1g2c30a qh1g2c30a D_3_ch1g2c30a ch1g2c30a D_4_sqhhg2c30a sqhhg2c30a D_5_qh2g2c30a qh2g2c30a D_6_sh3g2c30a sh3g2c30a D_7_qh3g2c30a qh3g2c30a D_8_ph2g2c30a ph2g2c30a D_9_sh4g2c30a sh4g2c30a D_10_ch2g2c30a ch2g2c30a D_11_cm1g4c30a cm1g4c30a D_12_qm1g4c30a qm1g4c30a D_13_sm1g4c30a sm1g4c30a D_14_pm1g4c30a pm1g4c30a D_15_qm2g4c30a qm2g4c30a D_16_sm2g4c30b sm2g4c30b D_17_qm2g4c30b qm2g4c30b D_18_sm1g4c30b sm1g4c30b D_19_pm1g4c30b pm1g4c30b D_20_qm1g4c30b qm1g4c30b D_21_cm1g4c30b cm1g4c30b D_22_ql3g6c30b ql3g6c30b D_23_pl2g6c30b pl2g6c30b D_24_sl3g6c30b sl3g6c30b D_25_cl2g6c30b cl2g6c30b D_26_ql2g6c30b ql2g6c30b D_27_sl2g6c30b sl2g6c30b D_28_cl1g6c30b cl1g6c30b D_29_ql1g6c30b ql1g6c30b D_30_pl1g6c30b pl1g6c30b D_31_sl1g6c30b sl1g6c30b D_32_sl1g2c01a sl1g2c01a D_33_pl1g2c01a pl1g2c01a D_34_ql1g2c01a ql1g2c01a D_35_cl1g2c01a cl1g2c01a D_36_sl2g2c01a sl2g2c01a D_37_ql2g2c01a ql2g2c01a D_38_cl2g2c01a cl2g2c01a D_39_sl3g2c01a sl3g2c01a D_40_pl2g2c01a pl2g2c01a D_41_ql3g2c01a ql3g2c01a D_42_cm1g4c01a cm1g4c01a sqmhg4c01a D_44_qm1g4c01a qm1g4c01a D_45_sm1g4c01a sm1g4c01a D_46_pm1g4c01a pm1g4c01a D_47_qm2g4c01a qm2g4c01a D_48_sm2g4c01b sm2g4c01b D_49_qm2g4c01b qm2g4c01b D_50_sm1g4c01b sm1g4c01b D_51_pm1g4c01b pm1g4c01b D_52_qm1g4c01b qm1g4c01b D_53_cm1g4c01b cm1g4c01b D_54_ch2g6c01b ch2g6c01b D_55_sh4g6c01b sh4g6c01b D_56_ph2g6c01b ph2g6c01b D_57_qh3g6c01b qh3g6c01b D_58_sh3g6c01b sh3g6c01b D_59_qh2g6c01b qh2g6c01b D_60_ch1g6c01b ch1g6c01b D_61_qh1g6c01b qh1g6c01b D_62_ph1g6c01b ph1g6c01b D_63_sh1g6c01b sh1g6c01b D_64_sh1g2c02a sh1g2c02a D_65_ph1g2c02a ph1g2c02a D_66_qh1g2c02a qh1g2c02a D_67_ch1g2c02a ch1g2c02a sqhhg2c02a D_69_qh2g2c02a qh2g2c02a D_70_sh3g2c02a sh3g2c02a D_71_qh3g2c02a qh3g2c02a D_72_ph2g2c02a ph2g2c02a D_73_sh4g2c02a sh4g2c02a D_74_ch2g2c02a ch2g2c02a D_75_cm1g4c02a cm1g4c02a D_76_qm1g4c02a qm1g4c02a D_77_sm1g4c02a sm1g4c02a D_78_pm1g4c02a pm1g4c02a D_79_qm2g4c02a qm2g4c02a D_80_sm2g4c02b sm2g4c02b D_81_qm2g4c02b qm2g4c02b D_82_sm1g4c02b sm1g4c02b D_83_pm1g4c02b pm1g4c02b D_84_qm1g4c02b qm1g4c02b D_85_cm1g4c02b cm1g4c02b D_86_ql3g6c02b ql3g6c02b D_87_pl2g6c02b pl2g6c02b D_88_sl3g6c02b sl3g6c02b D_89_cl2g6c02b cl2g6c02b D_90_ql2g6c02b ql2g6c02b D_91_sl2g6c02b sl2g6c02b D_92_cl1g6c02b cl1g6c02b D_93_ql1g6c02b ql1g6c02b D_94_pl1g6c02b pl1g6c02b D_95_sl1g6c02b sl1g6c02b D_96_sl1g2c03a sl1g2c03a D_97_pl1g2c03a pl1g2c03a D_98_ql1g2c03a ql1g2c03a D_99_cl1g2c03a cl1g2c03a D_100_sl2g2c03a sl2g2c03a D_101_ql2g2c03a ql2g2c03a D_102_cl2g2c03a cl2g2c03a D_103_sl3g2c03a sl3g2c03a D_104_pl2g2c03a pl2g2c03a D_105_ql3g2c03a ql3g2c03a D_106_cm1g4c03a cm1g4c03a D_107_sqmhg4c03a sqmhg4c03a D_108_qm1g4c03a qm1g4c03a D_109_sm1g4c03a sm1g4c03a D_110_pm1g4c03a pm1g4c03a D_111_qm2g4c03a qm2g4c03a D_112_sm2g4c03b sm2g4c03b D_113_qm2g4c03b qm2g4c03b D_114_sm1g4c03b sm1g4c03b D_115_pm1g4c03b pm1g4c03b D_116_qm1g4c03b qm1g4c03b D_117_cm1g4c03b cm1g4c03b D_118_ch2g6c03b ch2g6c03b D_119_sh4g6c03b sh4g6c03b D_120_ph2g6c03b ph2g6c03b D_121_qh3g6c03b qh3g6c03b D_122_sh3g6c03b sh3g6c03b D_123_qh2g6c03b qh2g6c03b D_124_ch1g6c03b ch1g6c03b D_125_qh1g6c03b qh1g6c03b D_126_ph1g6c03b ph1g6c03b D_127_sh1g6c03b sh1g6c03b D_128_sh1g2c04a sh1g2c04a D_129_ph1g2c04a ph1g2c04a D_130_qh1g2c04a qh1g2c04a D_131_ch1g2c04a ch1g2c04a D_132_sqhhg2c04a sqhhg2c04a D_133_qh2g2c04a qh2g2c04a D_134_sh3g2c04a sh3g2c04a D_135_qh3g2c04a qh3g2c04a D_136_ph2g2c04a ph2g2c04a D_137_sh4g2c04a sh4g2c04a D_138_ch2g2c04a ch2g2c04a D_139_cm1g4c04a cm1g4c04a D_140_qm1g4c04a qm1g4c04a D_141_sm1g4c04a sm1g4c04a D_142_pm1g4c04a pm1g4c04a D_143_qm2g4c04a qm2g4c04a D_144_sm2g4c04b sm2g4c04b D_145_qm2g4c04b qm2g4c04b D_146_sm1g4c04b sm1g4c04b D_147_pm1g4c04b pm1g4c04b D_148_qm1g4c04b qm1g4c04b D_149_cm1g4c04b cm1g4c04b D_150_ql3g6c04b ql3g6c04b D_151_pl2g6c04b pl2g6c04b D_152_sl3g6c04b sl3g6c04b D_153_cl2g6c04b cl2g6c04b D_154_ql2g6c04b ql2g6c04b D_155_sl2g6c04b sl2g6c04b D_156_cl1g6c04b cl1g6c04b D_157_ql1g6c04b ql1g6c04b D_158_pl1g6c04b pl1g6c04b D_159_sl1g6c04b sl1g6c04b D_160_sl1g2c05a sl1g2c05a D_161_pl1g2c05a pl1g2c05a D_162_ql1g2c05a ql1g2c05a D_163_cl1g2c05a cl1g2c05a D_164_sl2g2c05a sl2g2c05a D_165_ql2g2c05a ql2g2c05a D_166_cl2g2c05a cl2g2c05a D_167_sl3g2c05a sl3g2c05a D_168_pl2g2c05a pl2g2c05a D_169_ql3g2c05a ql3g2c05a D_170_cm1g4c05a cm1g4c05a sqmhg4c05a D_172_qm1g4c05a qm1g4c05a D_173_sm1g4c05a sm1g4c05a D_174_pm1g4c05a pm1g4c05a D_175_qm2g4c05a qm2g4c05a D_176_sm2g4c05b sm2g4c05b D_177_qm2g4c05b qm2g4c05b D_178_sm1g4c05b sm1g4c05b D_179_pm1g4c05b pm1g4c05b D_180_qm1g4c05b qm1g4c05b D_181_cm1g4c05b cm1g4c05b D_182_ch2g6c05b ch2g6c05b D_183_sh4g6c05b sh4g6c05b D_184_ph2g6c05b ph2g6c05b D_185_qh3g6c05b qh3g6c05b D_186_sh3g6c05b sh3g6c05b D_187_qh2g6c05b qh2g6c05b D_188_ch1g6c05b ch1g6c05b D_189_qh1g6c05b qh1g6c05b D_190_ph1g6c05b ph1g6c05b D_191_sh1g6c05b sh1g6c05b D_192_sh1g2c06a sh1g2c06a D_193_ph1g2c06a ph1g2c06a D_194_qh1g2c06a qh1g2c06a D_195_ch1g2c06a ch1g2c06a sqhhg2c06a D_197_qh2g2c06a qh2g2c06a D_198_sh3g2c06a sh3g2c06a D_199_qh3g2c06a qh3g2c06a D_200_ph2g2c06a ph2g2c06a D_201_sh4g2c06a sh4g2c06a D_202_ch2g2c06a ch2g2c06a D_203_cm1g4c06a cm1g4c06a D_204_qm1g4c06a qm1g4c06a D_205_sm1g4c06a sm1g4c06a D_206_pm1g4c06a pm1g4c06a D_207_qm2g4c06a qm2g4c06a D_208_sm2g4c06b sm2g4c06b D_209_qm2g4c06b qm2g4c06b D_210_sm1g4c06b sm1g4c06b D_211_pm1g4c06b pm1g4c06b D_212_qm1g4c06b qm1g4c06b D_213_cm1g4c06b cm1g4c06b D_214_ql3g6c06b ql3g6c06b D_215_pl2g6c06b pl2g6c06b D_216_sl3g6c06b sl3g6c06b D_217_cl2g6c06b cl2g6c06b D_218_ql2g6c06b ql2g6c06b D_219_sl2g6c06b sl2g6c06b D_220_cl1g6c06b cl1g6c06b D_221_ql1g6c06b ql1g6c06b D_222_pl1g6c06b pl1g6c06b D_223_sl1g6c06b sl1g6c06b D_224_sl1g2c07a sl1g2c07a D_225_pl1g2c07a pl1g2c07a D_226_ql1g2c07a ql1g2c07a D_227_cl1g2c07a cl1g2c07a D_228_sl2g2c07a sl2g2c07a D_229_ql2g2c07a ql2g2c07a D_230_cl2g2c07a cl2g2c07a D_231_sl3g2c07a sl3g2c07a D_232_pl2g2c07a pl2g2c07a D_233_ql3g2c07a ql3g2c07a D_234_cm1g4c07a cm1g4c07a sqmhg4c07a D_236_qm1g4c07a qm1g4c07a D_237_sm1g4c07a sm1g4c07a D_238_pm1g4c07a pm1g4c07a D_239_qm2g4c07a qm2g4c07a D_240_sm2g4c07b sm2g4c07b D_241_qm2g4c07b qm2g4c07b D_242_sm1g4c07b sm1g4c07b D_243_pm1g4c07b pm1g4c07b D_244_qm1g4c07b qm1g4c07b D_245_cm1g4c07b cm1g4c07b D_246_ch2g6c07b ch2g6c07b D_247_sh4g6c07b sh4g6c07b D_248_ph2g6c07b ph2g6c07b D_249_qh3g6c07b qh3g6c07b D_250_sh3g6c07b sh3g6c07b D_251_qh2g6c07b qh2g6c07b D_252_ch1g6c07b ch1g6c07b D_253_qh1g6c07b qh1g6c07b D_254_ph1g6c07b ph1g6c07b D_255_sh1g6c07b sh1g6c07b D_256_sh1g2c08a sh1g2c08a D_257_ph1g2c08a ph1g2c08a D_258_qh1g2c08a qh1g2c08a D_259_ch1g2c08a ch1g2c08a sqhhg2c08a D_261_qh2g2c08a qh2g2c08a D_262_sh3g2c08a sh3g2c08a D_263_qh3g2c08a qh3g2c08a D_264_ph2g2c08a ph2g2c08a D_265_sh4g2c08a sh4g2c08a D_266_ch2g2c08a ch2g2c08a D_267_cm1g4c08a cm1g4c08a D_268_qm1g4c08a qm1g4c08a D_269_sm1g4c08a sm1g4c08a D_270_pm1g4c08a pm1g4c08a D_271_qm2g4c08a qm2g4c08a D_272_sm2g4c08b sm2g4c08b D_273_qm2g4c08b qm2g4c08b D_274_sm1g4c08b sm1g4c08b D_275_pm1g4c08b pm1g4c08b D_276_qm1g4c08b qm1g4c08b D_277_cm1g4c08b cm1g4c08b D_278_ql3g6c08b ql3g6c08b D_279_pl2g6c08b pl2g6c08b D_280_sl3g6c08b sl3g6c08b D_281_cl2g6c08b cl2g6c08b D_282_ql2g6c08b ql2g6c08b D_283_sl2g6c08b sl2g6c08b D_284_cl1g6c08b cl1g6c08b D_285_ql1g6c08b ql1g6c08b D_286_pl1g6c08b pl1g6c08b D_287_sl1g6c08b sl1g6c08b D_288_sl1g2c09a sl1g2c09a D_289_pl1g2c09a pl1g2c09a D_290_ql1g2c09a ql1g2c09a D_291_cl1g2c09a cl1g2c09a D_292_sl2g2c09a sl2g2c09a D_293_ql2g2c09a ql2g2c09a D_294_cl2g2c09a cl2g2c09a D_295_sl3g2c09a sl3g2c09a D_296_pl2g2c09a pl2g2c09a D_297_ql3g2c09a ql3g2c09a D_298_cm1g4c09a cm1g4c09a D_299_sqmhg4c09a sqmhg4c09a D_300_qm1g4c09a qm1g4c09a D_301_sm1g4c09a sm1g4c09a D_302_pm1g4c09a pm1g4c09a D_303_qm2g4c09a qm2g4c09a D_304_sm2g4c09b sm2g4c09b D_305_qm2g4c09b qm2g4c09b D_306_sm1g4c09b sm1g4c09b D_307_pm1g4c09b pm1g4c09b D_308_qm1g4c09b qm1g4c09b D_309_cm1g4c09b cm1g4c09b D_310_ch2g6c09b ch2g6c09b D_311_sh4g6c09b sh4g6c09b D_312_ph2g6c09b ph2g6c09b D_313_qh3g6c09b qh3g6c09b D_314_sh3g6c09b sh3g6c09b D_315_qh2g6c09b qh2g6c09b D_316_ch1g6c09b ch1g6c09b D_317_qh1g6c09b qh1g6c09b D_318_ph1g6c09b ph1g6c09b D_319_sh1g6c09b sh1g6c09b D_320_sh1g2c10a sh1g2c10a D_321_ph1g2c10a ph1g2c10a D_322_qh1g2c10a qh1g2c10a D_323_ch1g2c10a ch1g2c10a sqhhg2c10a D_325_qh2g2c10a qh2g2c10a D_326_sh3g2c10a sh3g2c10a D_327_qh3g2c10a qh3g2c10a D_328_ph2g2c10a ph2g2c10a D_329_sh4g2c10a sh4g2c10a D_330_ch2g2c10a ch2g2c10a D_331_cm1g4c10a cm1g4c10a D_332_qm1g4c10a qm1g4c10a D_333_sm1g4c10a sm1g4c10a D_334_pm1g4c10a pm1g4c10a D_335_qm2g4c10a qm2g4c10a D_336_sm2g4c10b sm2g4c10b D_337_qm2g4c10b qm2g4c10b D_338_sm1g4c10b sm1g4c10b D_339_pm1g4c10b pm1g4c10b D_340_qm1g4c10b qm1g4c10b D_341_cm1g4c10b cm1g4c10b D_342_ql3g6c10b ql3g6c10b D_343_pl2g6c10b pl2g6c10b D_344_sl3g6c10b sl3g6c10b D_345_cl2g6c10b cl2g6c10b D_346_ql2g6c10b ql2g6c10b D_347_sl2g6c10b sl2g6c10b D_348_cl1g6c10b cl1g6c10b D_349_ql1g6c10b ql1g6c10b D_350_pl1g6c10b pl1g6c10b D_351_sl1g6c10b sl1g6c10b D_352_sl1g2c11a sl1g2c11a D_353_pl1g2c11a pl1g2c11a D_354_ql1g2c11a ql1g2c11a D_355_cl1g2c11a cl1g2c11a D_356_sl2g2c11a sl2g2c11a D_357_ql2g2c11a ql2g2c11a D_358_cl2g2c11a cl2g2c11a D_359_sl3g2c11a sl3g2c11a D_360_pl2g2c11a pl2g2c11a D_361_ql3g2c11a ql3g2c11a D_362_cm1g4c11a cm1g4c11a sqmhg4c11a D_364_qm1g4c11a qm1g4c11a D_365_sm1g4c11a sm1g4c11a D_366_pm1g4c11a pm1g4c11a D_367_qm2g4c11a qm2g4c11a D_368_sm2g4c11b sm2g4c11b D_369_qm2g4c11b qm2g4c11b D_370_sm1g4c11b sm1g4c11b D_371_pm1g4c11b pm1g4c11b D_372_qm1g4c11b qm1g4c11b D_373_cm1g4c11b cm1g4c11b D_374_ch2g6c11b ch2g6c11b D_375_sh4g6c11b sh4g6c11b D_376_ph2g6c11b ph2g6c11b D_377_qh3g6c11b qh3g6c11b D_378_sh3g6c11b sh3g6c11b D_379_qh2g6c11b qh2g6c11b D_380_ch1g6c11b ch1g6c11b D_381_qh1g6c11b qh1g6c11b D_382_ph1g6c11b ph1g6c11b D_383_sh1g6c11b sh1g6c11b D_384_sh1g2c12a sh1g2c12a D_385_ph1g2c12a ph1g2c12a D_386_qh1g2c12a qh1g2c12a D_387_ch1g2c12a ch1g2c12a sqhhg2c12a D_389_qh2g2c12a qh2g2c12a D_390_sh3g2c12a sh3g2c12a D_391_qh3g2c12a qh3g2c12a D_392_ph2g2c12a ph2g2c12a D_393_sh4g2c12a sh4g2c12a D_394_ch2g2c12a ch2g2c12a D_395_cm1g4c12a cm1g4c12a D_396_qm1g4c12a qm1g4c12a D_397_sm1g4c12a sm1g4c12a D_398_pm1g4c12a pm1g4c12a D_399_qm2g4c12a qm2g4c12a D_400_sm2g4c12b sm2g4c12b D_401_qm2g4c12b qm2g4c12b D_402_sm1g4c12b sm1g4c12b D_403_pm1g4c12b pm1g4c12b D_404_qm1g4c12b qm1g4c12b D_405_cm1g4c12b cm1g4c12b D_406_ql3g6c12b ql3g6c12b D_407_pl2g6c12b pl2g6c12b D_408_sl3g6c12b sl3g6c12b D_409_cl2g6c12b cl2g6c12b D_410_ql2g6c12b ql2g6c12b D_411_sl2g6c12b sl2g6c12b D_412_cl1g6c12b cl1g6c12b D_413_ql1g6c12b ql1g6c12b D_414_pl1g6c12b pl1g6c12b D_415_sl1g6c12b sl1g6c12b D_416_sl1g2c13a sl1g2c13a D_417_pl1g2c13a pl1g2c13a D_418_ql1g2c13a ql1g2c13a D_419_cl1g2c13a cl1g2c13a D_420_sl2g2c13a sl2g2c13a D_421_ql2g2c13a ql2g2c13a D_422_cl2g2c13a cl2g2c13a D_423_sl3g2c13a sl3g2c13a D_424_pl2g2c13a pl2g2c13a D_425_ql3g2c13a ql3g2c13a D_426_cm1g4c13a cm1g4c13a sqmhg4c13a D_428_qm1g4c13a qm1g4c13a D_429_sm1g4c13a sm1g4c13a D_430_pm1g4c13a pm1g4c13a D_431_qm2g4c13a qm2g4c13a D_432_sm2g4c13b sm2g4c13b D_433_qm2g4c13b qm2g4c13b D_434_sm1g4c13b sm1g4c13b D_435_pm1g4c13b pm1g4c13b D_436_qm1g4c13b qm1g4c13b D_437_cm1g4c13b cm1g4c13b D_438_ch2g6c13b ch2g6c13b D_439_sh4g6c13b sh4g6c13b D_440_ph2g6c13b ph2g6c13b D_441_qh3g6c13b qh3g6c13b D_442_sh3g6c13b sh3g6c13b D_443_qh2g6c13b qh2g6c13b D_444_ch1g6c13b ch1g6c13b D_445_qh1g6c13b qh1g6c13b D_446_ph1g6c13b ph1g6c13b D_447_sh1g6c13b sh1g6c13b D_448_sh1g2c14a sh1g2c14a D_449_ph1g2c14a ph1g2c14a D_450_qh1g2c14a qh1g2c14a D_451_ch1g2c14a ch1g2c14a sqhhg2c14a D_453_qh2g2c14a qh2g2c14a D_454_sh3g2c14a sh3g2c14a D_455_qh3g2c14a qh3g2c14a D_456_ph2g2c14a ph2g2c14a D_457_sh4g2c14a sh4g2c14a D_458_ch2g2c14a ch2g2c14a D_459_cm1g4c14a cm1g4c14a D_460_qm1g4c14a qm1g4c14a D_461_sm1g4c14a sm1g4c14a D_462_pm1g4c14a pm1g4c14a D_463_qm2g4c14a qm2g4c14a D_464_sm2g4c14b sm2g4c14b D_465_qm2g4c14b qm2g4c14b D_466_sm1g4c14b sm1g4c14b D_467_pm1g4c14b pm1g4c14b D_468_qm1g4c14b qm1g4c14b D_469_cm1g4c14b cm1g4c14b D_470_ql3g6c14b ql3g6c14b D_471_pl2g6c14b pl2g6c14b D_472_sl3g6c14b sl3g6c14b D_473_cl2g6c14b cl2g6c14b D_474_ql2g6c14b ql2g6c14b D_475_sl2g6c14b sl2g6c14b D_476_cl1g6c14b cl1g6c14b D_477_ql1g6c14b ql1g6c14b D_478_pl1g6c14b pl1g6c14b D_479_sl1g6c14b sl1g6c14b D_480_sl1g2c15a sl1g2c15a D_481_pl1g2c15a pl1g2c15a D_482_ql1g2c15a ql1g2c15a D_483_cl1g2c15a cl1g2c15a D_484_sl2g2c15a sl2g2c15a D_485_ql2g2c15a ql2g2c15a D_486_cl2g2c15a cl2g2c15a D_487_sl3g2c15a sl3g2c15a D_488_pl2g2c15a pl2g2c15a D_489_ql3g2c15a ql3g2c15a D_490_cm1g4c15a cm1g4c15a sqmhg4c15a D_492_qm1g4c15a qm1g4c15a D_493_sm1g4c15a sm1g4c15a D_494_pm1g4c15a pm1g4c15a D_495_qm2g4c15a qm2g4c15a D_496_sm2g4c15b sm2g4c15b D_497_qm2g4c15b qm2g4c15b D_498_sm1g4c15b sm1g4c15b D_499_pm1g4c15b pm1g4c15b D_500_qm1g4c15b qm1g4c15b D_501_cm1g4c15b cm1g4c15b D_502_ch2g6c15b ch2g6c15b D_503_sh4g6c15b sh4g6c15b D_504_ph2g6c15b ph2g6c15b D_505_qh3g6c15b qh3g6c15b D_506_sh3g6c15b sh3g6c15b D_507_qh2g6c15b qh2g6c15b D_508_ch1g6c15b ch1g6c15b D_509_qh1g6c15b qh1g6c15b D_510_ph1g6c15b ph1g6c15b D_511_sh1g6c15b sh1g6c15b D_512_sh1g2c16a sh1g2c16a D_513_ph1g2c16a ph1g2c16a D_514_qh1g2c16a qh1g2c16a D_515_ch1g2c16a ch1g2c16a sqhhg2c16a D_517_qh2g2c16a qh2g2c16a D_518_sh3g2c16a sh3g2c16a D_519_qh3g2c16a qh3g2c16a D_520_ph2g2c16a ph2g2c16a D_521_sh4g2c16a sh4g2c16a D_522_ch2g2c16a ch2g2c16a D_523_cm1g4c16a cm1g4c16a D_524_qm1g4c16a qm1g4c16a D_525_sm1g4c16a sm1g4c16a D_526_pm1g4c16a pm1g4c16a D_527_qm2g4c16a qm2g4c16a D_528_sm2g4c16b sm2g4c16b D_529_qm2g4c16b qm2g4c16b D_530_sm1g4c16b sm1g4c16b D_531_pm1g4c16b pm1g4c16b D_532_qm1g4c16b qm1g4c16b D_533_cm1g4c16b cm1g4c16b D_534_ql3g6c16b ql3g6c16b D_535_pl2g6c16b pl2g6c16b D_536_sl3g6c16b sl3g6c16b D_537_cl2g6c16b cl2g6c16b D_538_ql2g6c16b ql2g6c16b D_539_sl2g6c16b sl2g6c16b D_540_cl1g6c16b cl1g6c16b D_541_ql1g6c16b ql1g6c16b D_542_pl1g6c16b pl1g6c16b D_543_sl1g6c16b sl1g6c16b D_544_sl1g2c17a sl1g2c17a D_545_pl1g2c17a pl1g2c17a D_546_ql1g2c17a ql1g2c17a D_547_cl1g2c17a cl1g2c17a D_548_sl2g2c17a sl2g2c17a D_549_ql2g2c17a ql2g2c17a D_550_cl2g2c17a cl2g2c17a D_551_sl3g2c17a sl3g2c17a D_552_pl2g2c17a pl2g2c17a D_553_ql3g2c17a ql3g2c17a D_554_cm1g4c17a cm1g4c17a sqmhg4c17a D_556_qm1g4c17a qm1g4c17a D_557_sm1g4c17a sm1g4c17a D_558_pm1g4c17a pm1g4c17a D_559_qm2g4c17a qm2g4c17a D_560_sm2g4c17b sm2g4c17b D_561_qm2g4c17b qm2g4c17b D_562_sm1g4c17b sm1g4c17b D_563_pm1g4c17b pm1g4c17b D_564_qm1g4c17b qm1g4c17b D_565_cm1g4c17b cm1g4c17b D_566_ch2g6c17b ch2g6c17b D_567_sh4g6c17b sh4g6c17b D_568_ph2g6c17b ph2g6c17b D_569_qh3g6c17b qh3g6c17b D_570_sh3g6c17b sh3g6c17b D_571_qh2g6c17b qh2g6c17b D_572_ch1g6c17b ch1g6c17b D_573_qh1g6c17b qh1g6c17b D_574_ph1g6c17b ph1g6c17b D_575_sh1g6c17b sh1g6c17b D_576_sh1g2c18a sh1g2c18a D_577_ph1g2c18a ph1g2c18a D_578_qh1g2c18a qh1g2c18a D_579_ch1g2c18a ch1g2c18a sqhhg2c18a D_581_qh2g2c18a qh2g2c18a D_582_sh3g2c18a sh3g2c18a D_583_qh3g2c18a qh3g2c18a D_584_ph2g2c18a ph2g2c18a D_585_sh4g2c18a sh4g2c18a D_586_ch2g2c18a ch2g2c18a D_587_cm1g4c18a cm1g4c18a D_588_qm1g4c18a qm1g4c18a D_589_sm1g4c18a sm1g4c18a D_590_pm1g4c18a pm1g4c18a D_591_qm2g4c18a qm2g4c18a D_592_sm2g4c18b sm2g4c18b D_593_qm2g4c18b qm2g4c18b D_594_sm1g4c18b sm1g4c18b D_595_pm1g4c18b pm1g4c18b D_596_qm1g4c18b qm1g4c18b D_597_cm1g4c18b cm1g4c18b D_598_ql3g6c18b ql3g6c18b D_599_pl2g6c18b pl2g6c18b D_600_sl3g6c18b sl3g6c18b D_601_cl2g6c18b cl2g6c18b D_602_ql2g6c18b ql2g6c18b D_603_sl2g6c18b sl2g6c18b D_604_cl1g6c18b cl1g6c18b D_605_ql1g6c18b ql1g6c18b D_606_pl1g6c18b pl1g6c18b D_607_sl1g6c18b sl1g6c18b D_608_sl1g2c19a sl1g2c19a D_609_pl1g2c19a pl1g2c19a D_610_ql1g2c19a ql1g2c19a D_611_cl1g2c19a cl1g2c19a D_612_sl2g2c19a sl2g2c19a D_613_ql2g2c19a ql2g2c19a D_614_cl2g2c19a cl2g2c19a D_615_sl3g2c19a sl3g2c19a D_616_pl2g2c19a pl2g2c19a D_617_ql3g2c19a ql3g2c19a D_618_cm1g4c19a cm1g4c19a sqmhg4c19a D_620_qm1g4c19a qm1g4c19a D_621_sm1g4c19a sm1g4c19a D_622_pm1g4c19a pm1g4c19a D_623_qm2g4c19a qm2g4c19a D_624_sm2g4c19b sm2g4c19b D_625_qm2g4c19b qm2g4c19b D_626_sm1g4c19b sm1g4c19b D_627_pm1g4c19b pm1g4c19b D_628_qm1g4c19b qm1g4c19b D_629_cm1g4c19b cm1g4c19b D_630_ch2g6c19b ch2g6c19b D_631_sh4g6c19b sh4g6c19b D_632_ph2g6c19b ph2g6c19b D_633_qh3g6c19b qh3g6c19b D_634_sh3g6c19b sh3g6c19b D_635_qh2g6c19b qh2g6c19b D_636_ch1g6c19b ch1g6c19b D_637_qh1g6c19b qh1g6c19b D_638_ph1g6c19b ph1g6c19b D_639_sh1g6c19b sh1g6c19b D_640_sh1g2c20a sh1g2c20a D_641_ph1g2c20a ph1g2c20a D_642_qh1g2c20a qh1g2c20a D_643_ch1g2c20a ch1g2c20a sqhhg2c20a D_645_qh2g2c20a qh2g2c20a D_646_sh3g2c20a sh3g2c20a D_647_qh3g2c20a qh3g2c20a D_648_ph2g2c20a ph2g2c20a D_649_sh4g2c20a sh4g2c20a D_650_ch2g2c20a ch2g2c20a D_651_cm1g4c20a cm1g4c20a D_652_qm1g4c20a qm1g4c20a D_653_sm1g4c20a sm1g4c20a D_654_pm1g4c20a pm1g4c20a D_655_qm2g4c20a qm2g4c20a D_656_sm2g4c20b sm2g4c20b D_657_qm2g4c20b qm2g4c20b D_658_sm1g4c20b sm1g4c20b D_659_pm1g4c20b pm1g4c20b D_660_qm1g4c20b qm1g4c20b D_661_cm1g4c20b cm1g4c20b D_662_ql3g6c20b ql3g6c20b D_663_pl2g6c20b pl2g6c20b D_664_sl3g6c20b sl3g6c20b D_665_cl2g6c20b cl2g6c20b D_666_ql2g6c20b ql2g6c20b D_667_sl2g6c20b sl2g6c20b D_668_cl1g6c20b cl1g6c20b D_669_ql1g6c20b ql1g6c20b D_670_pl1g6c20b pl1g6c20b D_671_sl1g6c20b sl1g6c20b D_672_sl1g2c21a sl1g2c21a D_673_pl1g2c21a pl1g2c21a D_674_ql1g2c21a ql1g2c21a D_675_cl1g2c21a cl1g2c21a D_676_sl2g2c21a sl2g2c21a D_677_ql2g2c21a ql2g2c21a D_678_cl2g2c21a cl2g2c21a D_679_sl3g2c21a sl3g2c21a D_680_pl2g2c21a pl2g2c21a D_681_ql3g2c21a ql3g2c21a D_682_cm1g4c21a cm1g4c21a sqmhg4c21a D_684_qm1g4c21a qm1g4c21a D_685_sm1g4c21a sm1g4c21a D_686_pm1g4c21a pm1g4c21a D_687_qm2g4c21a qm2g4c21a D_688_sm2g4c21b sm2g4c21b D_689_qm2g4c21b qm2g4c21b D_690_sm1g4c21b sm1g4c21b D_691_pm1g4c21b pm1g4c21b D_692_qm1g4c21b qm1g4c21b D_693_cm1g4c21b cm1g4c21b D_694_ch2g6c21b ch2g6c21b D_695_sh4g6c21b sh4g6c21b D_696_ph2g6c21b ph2g6c21b D_697_qh3g6c21b qh3g6c21b D_698_sh3g6c21b sh3g6c21b D_699_qh2g6c21b qh2g6c21b D_700_ch1g6c21b ch1g6c21b D_701_qh1g6c21b qh1g6c21b D_702_ph1g6c21b ph1g6c21b D_703_sh1g6c21b sh1g6c21b D_704_sh1g2c22a sh1g2c22a D_705_ph1g2c22a ph1g2c22a D_706_qh1g2c22a qh1g2c22a D_707_ch1g2c22a ch1g2c22a sqhhg2c22a D_709_qh2g2c22a qh2g2c22a D_710_sh3g2c22a sh3g2c22a D_711_qh3g2c22a qh3g2c22a D_712_ph2g2c22a ph2g2c22a D_713_sh4g2c22a sh4g2c22a D_714_ch2g2c22a ch2g2c22a D_715_cm1g4c22a cm1g4c22a D_716_qm1g4c22a qm1g4c22a D_717_sm1g4c22a sm1g4c22a D_718_pm1g4c22a pm1g4c22a D_719_qm2g4c22a qm2g4c22a D_720_sm2g4c22b sm2g4c22b D_721_qm2g4c22b qm2g4c22b D_722_sm1g4c22b sm1g4c22b D_723_pm1g4c22b pm1g4c22b D_724_qm1g4c22b qm1g4c22b D_725_cm1g4c22b cm1g4c22b D_726_ql3g6c22b ql3g6c22b D_727_pl2g6c22b pl2g6c22b D_728_sl3g6c22b sl3g6c22b D_729_cl2g6c22b cl2g6c22b D_730_ql2g6c22b ql2g6c22b D_731_sl2g6c22b sl2g6c22b D_732_cl1g6c22b cl1g6c22b D_733_ql1g6c22b ql1g6c22b D_734_pl1g6c22b pl1g6c22b D_735_sl1g6c22b sl1g6c22b D_736_sl1g2c23a sl1g2c23a D_737_pl1g2c23a pl1g2c23a D_738_ql1g2c23a ql1g2c23a D_739_cl1g2c23a cl1g2c23a D_740_sl2g2c23a sl2g2c23a D_741_ql2g2c23a ql2g2c23a D_742_cl2g2c23a cl2g2c23a D_743_sl3g2c23a sl3g2c23a D_744_pl2g2c23a pl2g2c23a D_745_ql3g2c23a ql3g2c23a D_746_cm1g4c23a cm1g4c23a sqmhg4c23a D_748_qm1g4c23a qm1g4c23a D_749_sm1g4c23a sm1g4c23a D_750_pm1g4c23a pm1g4c23a D_751_qm2g4c23a qm2g4c23a D_752_sm2g4c23b sm2g4c23b D_753_qm2g4c23b qm2g4c23b D_754_sm1g4c23b sm1g4c23b D_755_pm1g4c23b pm1g4c23b D_756_qm1g4c23b qm1g4c23b D_757_cm1g4c23b cm1g4c23b D_758_ch2g6c23b ch2g6c23b D_759_sh4g6c23b sh4g6c23b D_760_ph2g6c23b ph2g6c23b D_761_qh3g6c23b qh3g6c23b D_762_sh3g6c23b sh3g6c23b D_763_qh2g6c23b qh2g6c23b D_764_ch1g6c23b ch1g6c23b D_765_qh1g6c23b qh1g6c23b D_766_ph1g6c23b ph1g6c23b D_767_sh1g6c23b sh1g6c23b D_768_sh1g2c24a sh1g2c24a D_769_ph1g2c24a ph1g2c24a D_770_qh1g2c24a qh1g2c24a D_771_ch1g2c24a ch1g2c24a sqhhg2c24a D_773_qh2g2c24a qh2g2c24a D_774_sh3g2c24a sh3g2c24a D_775_qh3g2c24a qh3g2c24a D_776_ph2g2c24a ph2g2c24a D_777_sh4g2c24a sh4g2c24a D_778_ch2g2c24a ch2g2c24a D_779_cm1g4c24a cm1g4c24a D_780_qm1g4c24a qm1g4c24a D_781_sm1g4c24a sm1g4c24a D_782_pm1g4c24a pm1g4c24a D_783_qm2g4c24a qm2g4c24a D_784_sm2g4c24b sm2g4c24b D_785_qm2g4c24b qm2g4c24b D_786_sm1g4c24b sm1g4c24b D_787_pm1g4c24b pm1g4c24b D_788_qm1g4c24b qm1g4c24b D_789_cm1g4c24b cm1g4c24b D_790_ql3g6c24b ql3g6c24b D_791_pl2g6c24b pl2g6c24b D_792_sl3g6c24b sl3g6c24b D_793_cl2g6c24b cl2g6c24b D_794_ql2g6c24b ql2g6c24b D_795_sl2g6c24b sl2g6c24b D_796_cl1g6c24b cl1g6c24b D_797_ql1g6c24b ql1g6c24b D_798_pl1g6c24b pl1g6c24b D_799_sl1g6c24b sl1g6c24b D_800_sl1g2c25a sl1g2c25a D_801_pl1g2c25a pl1g2c25a D_802_ql1g2c25a ql1g2c25a D_803_cl1g2c25a cl1g2c25a D_804_sl2g2c25a sl2g2c25a D_805_ql2g2c25a ql2g2c25a D_806_cl2g2c25a cl2g2c25a D_807_sl3g2c25a sl3g2c25a D_808_pl2g2c25a pl2g2c25a D_809_ql3g2c25a ql3g2c25a D_810_cm1g4c25a cm1g4c25a sqmhg4c25a D_812_qm1g4c25a qm1g4c25a D_813_sm1g4c25a sm1g4c25a D_814_pm1g4c25a pm1g4c25a D_815_qm2g4c25a qm2g4c25a D_816_sm2g4c25b sm2g4c25b D_817_qm2g4c25b qm2g4c25b D_818_sm1g4c25b sm1g4c25b D_819_pm1g4c25b pm1g4c25b D_820_qm1g4c25b qm1g4c25b D_821_cm1g4c25b cm1g4c25b D_822_ch2g6c25b ch2g6c25b D_823_sh4g6c25b sh4g6c25b D_824_ph2g6c25b ph2g6c25b D_825_qh3g6c25b qh3g6c25b D_826_sh3g6c25b sh3g6c25b D_827_qh2g6c25b qh2g6c25b D_828_ch1g6c25b ch1g6c25b D_829_qh1g6c25b qh1g6c25b D_830_ph1g6c25b ph1g6c25b D_831_sh1g6c25b sh1g6c25b D_832_sh1g2c26a sh1g2c26a D_833_ph1g2c26a ph1g2c26a D_834_qh1g2c26a qh1g2c26a D_835_ch1g2c26a ch1g2c26a sqhhg2c26a D_837_qh2g2c26a qh2g2c26a D_838_sh3g2c26a sh3g2c26a D_839_qh3g2c26a qh3g2c26a D_840_ph2g2c26a ph2g2c26a D_841_sh4g2c26a sh4g2c26a D_842_ch2g2c26a ch2g2c26a D_843_cm1g4c26a cm1g4c26a D_844_qm1g4c26a qm1g4c26a D_845_sm1g4c26a sm1g4c26a D_846_pm1g4c26a pm1g4c26a D_847_qm2g4c26a qm2g4c26a D_848_sm2g4c26b sm2g4c26b D_849_qm2g4c26b qm2g4c26b D_850_sm1g4c26b sm1g4c26b D_851_pm1g4c26b pm1g4c26b D_852_qm1g4c26b qm1g4c26b D_853_cm1g4c26b cm1g4c26b D_854_ql3g6c26b ql3g6c26b D_855_pl2g6c26b pl2g6c26b D_856_sl3g6c26b sl3g6c26b D_857_cl2g6c26b cl2g6c26b D_858_ql2g6c26b ql2g6c26b D_859_sl2g6c26b sl2g6c26b D_860_cl1g6c26b cl1g6c26b D_861_ql1g6c26b ql1g6c26b D_862_pl1g6c26b pl1g6c26b D_863_sl1g6c26b sl1g6c26b D_864_sl1g2c27a sl1g2c27a D_865_pl1g2c27a pl1g2c27a D_866_ql1g2c27a ql1g2c27a D_867_cl1g2c27a cl1g2c27a D_868_sl2g2c27a sl2g2c27a D_869_ql2g2c27a ql2g2c27a D_870_cl2g2c27a cl2g2c27a D_871_sl3g2c27a sl3g2c27a D_872_pl2g2c27a pl2g2c27a D_873_ql3g2c27a ql3g2c27a D_874_cm1g4c27a cm1g4c27a sqmhg4c27a D_876_qm1g4c27a qm1g4c27a D_877_sm1g4c27a sm1g4c27a D_878_pm1g4c27a pm1g4c27a D_879_qm2g4c27a qm2g4c27a D_880_sm2g4c27b sm2g4c27b D_881_qm2g4c27b qm2g4c27b D_882_sm1g4c27b sm1g4c27b D_883_pm1g4c27b pm1g4c27b D_884_qm1g4c27b qm1g4c27b D_885_cm1g4c27b cm1g4c27b D_886_ch2g6c27b ch2g6c27b D_887_sh4g6c27b sh4g6c27b D_888_ph2g6c27b ph2g6c27b D_889_qh3g6c27b qh3g6c27b D_890_sh3g6c27b sh3g6c27b D_891_qh2g6c27b qh2g6c27b D_892_ch1g6c27b ch1g6c27b D_893_qh1g6c27b qh1g6c27b D_894_ph1g6c27b ph1g6c27b D_895_sh1g6c27b sh1g6c27b D_896_sh1g2c28a sh1g2c28a D_897_ph1g2c28a ph1g2c28a D_898_qh1g2c28a qh1g2c28a D_899_ch1g2c28a ch1g2c28a sqhhg2c28a D_901_qh2g2c28a qh2g2c28a D_902_sh3g2c28a sh3g2c28a D_903_qh3g2c28a qh3g2c28a D_904_ph2g2c28a ph2g2c28a D_905_sh4g2c28a sh4g2c28a D_906_ch2g2c28a ch2g2c28a D_907_cm1g4c28a cm1g4c28a D_908_qm1g4c28a qm1g4c28a D_909_sm1g4c28a sm1g4c28a D_910_pm1g4c28a pm1g4c28a D_911_qm2g4c28a qm2g4c28a D_912_sm2g4c28b sm2g4c28b D_913_qm2g4c28b qm2g4c28b D_914_sm1g4c28b sm1g4c28b D_915_pm1g4c28b pm1g4c28b D_916_qm1g4c28b qm1g4c28b D_917_cm1g4c28b cm1g4c28b D_918_ql3g6c28b ql3g6c28b D_919_pl2g6c28b pl2g6c28b D_920_sl3g6c28b sl3g6c28b D_921_cl2g6c28b cl2g6c28b D_922_ql2g6c28b ql2g6c28b D_923_sl2g6c28b sl2g6c28b D_924_cl1g6c28b cl1g6c28b D_925_ql1g6c28b ql1g6c28b D_926_pl1g6c28b pl1g6c28b D_927_sl1g6c28b sl1g6c28b D_928_sl1g2c29a sl1g2c29a D_929_pl1g2c29a pl1g2c29a D_930_ql1g2c29a ql1g2c29a D_931_cl1g2c29a cl1g2c29a D_932_sl2g2c29a sl2g2c29a D_933_ql2g2c29a ql2g2c29a D_934_cl2g2c29a cl2g2c29a D_935_sl3g2c29a sl3g2c29a D_936_pl2g2c29a pl2g2c29a D_937_ql3g2c29a ql3g2c29a D_938_cm1g4c29a cm1g4c29a sqmhg4c29a D_940_qm1g4c29a qm1g4c29a D_941_sm1g4c29a sm1g4c29a D_942_pm1g4c29a pm1g4c29a D_943_qm2g4c29a qm2g4c29a D_944_sm2g4c29b sm2g4c29b D_945_qm2g4c29b qm2g4c29b D_946_sm1g4c29b sm1g4c29b D_947_pm1g4c29b pm1g4c29b D_948_qm1g4c29b qm1g4c29b D_949_cm1g4c29b cm1g4c29b D_950_ch2g6c29b ch2g6c29b D_951_sh4g6c29b sh4g6c29b D_952_ph2g6c29b ph2g6c29b D_953_qh3g6c29b qh3g6c29b D_954_sh3g6c29b sh3g6c29b D_955_qh2g6c29b qh2g6c29b D_956_ch1g6c29b ch1g6c29b D_957_qh1g6c29b qh1g6c29b D_958_ph1g6c29b ph1g6c29b D_959_sh1g6c29b sh1g6c29b ];


% END of BODY

buildlat(LV2SR);
THERING = setcellstruct(THERING, 'Energy', 1:length(THERING), Energy);

%for i=1:length(THERING),
%    s = findspos(THERING, i+1);
%  fprintf('%s L=%f, s=%f\n', THERING{i}.FamName, THERING{i}.Length, s);
%end

L0 = findspos(THERING, length(THERING)+1);
fprintf('   Total Length = %.6f meters  \n', L0)

