function varargout = v1ltd1lattice(varargin)

global THERING 

if nargin >=1
   Energy = varargin{1};
else
  Energy = 200e6;
end



%BEG_ = marker('BEG', 'IdentityPass');

D_0_DHF_p1 = drift('DRIFT', 0.098044, 'DriftPass');
DHF_p1 = drift('HALFD', 0.08, 'DriftPass'); %s= 0.098044
p1 = marker('BPM', 'IdentityPass'); %s= 0.178044
DHF_p1 = drift('HALFD', 0.08, 'DriftPass'); %s= 0.178044
D_3_vf1 = drift('DRIFT', 0.104795, 'DriftPass');
vf1 = marker('SCREEN', 'IdentityPass'); %s= 0.362839
D_4_c1 = drift('DRIFT', 0.129253, 'DriftPass');
c1 = corrector('HVCM', 0.15, [0 0], 'CorrectorPass'); %s= 0.492092
D_5_q1 = drift('DRIFT', 0.04727, 'DriftPass');
q1 = quadrupole('QUAD', 0.15, -12.3810302907, 'StrMPoleSymplectic4Pass'); %s= 0.689362
D_6_ict1 = drift('DRIFT', 0.120638, 'DriftPass');
ict1 = marker('ICT', 'IdentityPass'); %s= 0.96
D_7_q2 = drift('DRIFT', 0.123562, 'DriftPass');
q2 = quadrupole('QUAD', 0.15, 13.0562504452, 'StrMPoleSymplectic4Pass'); %s= 1.083562
D_8_q3 = drift('DRIFT', 0.243936, 'DriftPass');
q3 = quadrupole('QUAD', 0.15, -4.291155182, 'StrMPoleSymplectic4Pass'); %s= 1.477498
D_9_c2 = drift('DRIFT', 0.041102, 'DriftPass');
c2 = corrector('HVCM', 0.15, [0 0], 'CorrectorPass'); %s= 1.6686
D_10_c1bd1 = drift('DRIFT', 1.714298, 'DriftPass');
c1bd1 = corrector('HVCM', 0.15, [0 0], 'CorrectorPass'); %s= 3.532898
D_11_q1bd1 = drift('DRIFT', 0.871902, 'DriftPass');
q1bd1 = quadrupole('QUAD', 0.15, -8.98441188582, 'StrMPoleSymplectic4Pass'); %s= 4.5548
D_12_q2bd1 = drift('DRIFT', 0.314027, 'DriftPass');
q2bd1 = quadrupole('QUAD', 0.15, 7.98520609273, 'StrMPoleSymplectic4Pass'); %s= 5.018827
D_13_c2bd1 = drift('DRIFT', 0.11578, 'DriftPass');
c2bd1 = corrector('HVCM', 0.15, [0 0], 'CorrectorPass'); %s= 5.284607
D_14_vf1bd1 = drift('DRIFT', 0.235393, 'DriftPass');
vf1bd1 = marker('SCREEN', 'IdentityPass'); %s= 5.67
D_15_vf2bd1 = drift('DRIFT', 1.08, 'DriftPass');
vf2bd1 = marker('SCREEN', 'IdentityPass'); %s= 6.75
D_16_vf3bd1 = drift('DRIFT', 1.01, 'DriftPass');
vf3bd1 = marker('SCREEN', 'IdentityPass'); %s= 7.76
LV1LTD1= [D_0_DHF_p1 DHF_p1 p1 DHF_p1 D_3_vf1 vf1 D_4_c1 c1 D_5_q1 q1 D_6_ict1 ict1 D_7_q2 q2 D_8_q3 q3 D_9_c2 c2 D_10_c1bd1 c1bd1 D_11_q1bd1 q1bd1 D_12_q2bd1 q2bd1 D_13_c2bd1 c2bd1 D_14_vf1bd1 vf1bd1 D_15_vf2bd1 vf2bd1 D_16_vf3bd1 vf3bd1];

buildlat(LV1LTD1);
THERING = setcellstruct(THERING, 'Energy', 1:length(THERING), Energy);

for i=1:length(THERING),
    s = findspos(THERING, i+1);
  fprintf('%s L=%f, s=%f\n', THERING{i}.FamName, THERING{i}.Length, s);
end

L0 = findspos(THERING, length(THERING)+1);
fprintf('   Total Length = %.6f meters  \n', L0)
