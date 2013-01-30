function v2srinit(varargin)

if nargin < 1
   OperationalMode = 1;
end

setao([]);

% BPM

% BPM
AO.BPMx.FamilyName  = 'BPMx';
AO.BPMx.MemberOf    = {'BPM'; 'BPMx';};
AO.BPMx.DeviceList  = [ 30 1; 30 2; 30 3; 30 4; 30 5; 30 6; 1 1; 1 2; 1 3; 1 4; 1 5; 1 6; 2 1; 2 2; 2 3; 2 4; 2 5; 2 6; 3 1; 3 2; 3 3; 3 4; 3 5; 3 6; 4 1; 4 2; 4 3; 4 4; 4 5; 4 6; 5 1; 5 2; 5 3; 5 4; 5 5; 5 6; 6 1; 6 2; 6 3; 6 4; 6 5; 6 6; 7 1; 7 2; 7 3; 7 4; 7 5; 7 6; 8 1; 8 2; 8 3; 8 4; 8 5; 8 6; 9 1; 9 2; 9 3; 9 4; 9 5; 9 6; 10 1; 10 2; 10 3; 10 4; 10 5; 10 6; 11 1; 11 2; 11 3; 11 4; 11 5; 11 6; 12 1; 12 2; 12 3; 12 4; 12 5; 12 6; 13 1; 13 2; 13 3; 13 4; 13 5; 13 6; 14 1; 14 2; 14 3; 14 4; 14 5; 14 6; 15 1; 15 2; 15 3; 15 4; 15 5; 15 6; 16 1; 16 2; 16 3; 16 4; 16 5; 16 6; 17 1; 17 2; 17 3; 17 4; 17 5; 17 6; 18 1; 18 2; 18 3; 18 4; 18 5; 18 6; 19 1; 19 2; 19 3; 19 4; 19 5; 19 6; 20 1; 20 2; 20 3; 20 4; 20 5; 20 6; 21 1; 21 2; 21 3; 21 4; 21 5; 21 6; 22 1; 22 2; 22 3; 22 4; 22 5; 22 6; 23 1; 23 2; 23 3; 23 4; 23 5; 23 6; 24 1; 24 2; 24 3; 24 4; 24 5; 24 6; 25 1; 25 2; 25 3; 25 4; 25 5; 25 6; 26 1; 26 2; 26 3; 26 4; 26 5; 26 6; 27 1; 27 2; 27 3; 27 4; 27 5; 27 6; 28 1; 28 2; 28 3; 28 4; 28 5; 28 6; 29 1; 29 2; 29 3; 29 4; 29 5; 29 6 ];
AO.BPMx.ElementList = (1:size(AO.BPMx.DeviceList,1))';
AO.BPMx.Status      = ones(size(AO.BPMx.DeviceList,1),1);
AO.BPMx.Position    = [];
AO.BPMx.CommonNames = [ 'ph1g2c30a'; 'ph2g2c30a'; 'pm1g4c30a'; 'pm1g4c30b'; 'pl2g6c30b'; 'pl1g6c30b'; 'pl1g2c01a'; 'pl2g2c01a'; 'pm1g4c01a'; 'pm1g4c01b'; 'ph2g6c01b'; 'ph1g6c01b'; 'ph1g2c02a'; 'ph2g2c02a'; 'pm1g4c02a'; 'pm1g4c02b'; 'pl2g6c02b'; 'pl1g6c02b'; 'pl1g2c03a'; 'pl2g2c03a'; 'pm1g4c03a'; 'pm1g4c03b'; 'ph2g6c03b'; 'ph1g6c03b'; 'ph1g2c04a'; 'ph2g2c04a'; 'pm1g4c04a'; 'pm1g4c04b'; 'pl2g6c04b'; 'pl1g6c04b'; 'pl1g2c05a'; 'pl2g2c05a'; 'pm1g4c05a'; 'pm1g4c05b'; 'ph2g6c05b'; 'ph1g6c05b'; 'ph1g2c06a'; 'ph2g2c06a'; 'pm1g4c06a'; 'pm1g4c06b'; 'pl2g6c06b'; 'pl1g6c06b'; 'pl1g2c07a'; 'pl2g2c07a'; 'pm1g4c07a'; 'pm1g4c07b'; 'ph2g6c07b'; 'ph1g6c07b'; 'ph1g2c08a'; 'ph2g2c08a'; 'pm1g4c08a'; 'pm1g4c08b'; 'pl2g6c08b'; 'pl1g6c08b'; 'pl1g2c09a'; 'pl2g2c09a'; 'pm1g4c09a'; 'pm1g4c09b'; 'ph2g6c09b'; 'ph1g6c09b'; 'ph1g2c10a'; 'ph2g2c10a'; 'pm1g4c10a'; 'pm1g4c10b'; 'pl2g6c10b'; 'pl1g6c10b'; 'pl1g2c11a'; 'pl2g2c11a'; 'pm1g4c11a'; 'pm1g4c11b'; 'ph2g6c11b'; 'ph1g6c11b'; 'ph1g2c12a'; 'ph2g2c12a'; 'pm1g4c12a'; 'pm1g4c12b'; 'pl2g6c12b'; 'pl1g6c12b'; 'pl1g2c13a'; 'pl2g2c13a'; 'pm1g4c13a'; 'pm1g4c13b'; 'ph2g6c13b'; 'ph1g6c13b'; 'ph1g2c14a'; 'ph2g2c14a'; 'pm1g4c14a'; 'pm1g4c14b'; 'pl2g6c14b'; 'pl1g6c14b'; 'pl1g2c15a'; 'pl2g2c15a'; 'pm1g4c15a'; 'pm1g4c15b'; 'ph2g6c15b'; 'ph1g6c15b'; 'ph1g2c16a'; 'ph2g2c16a'; 'pm1g4c16a'; 'pm1g4c16b'; 'pl2g6c16b'; 'pl1g6c16b'; 'pl1g2c17a'; 'pl2g2c17a'; 'pm1g4c17a'; 'pm1g4c17b'; 'ph2g6c17b'; 'ph1g6c17b'; 'ph1g2c18a'; 'ph2g2c18a'; 'pm1g4c18a'; 'pm1g4c18b'; 'pl2g6c18b'; 'pl1g6c18b'; 'pl1g2c19a'; 'pl2g2c19a'; 'pm1g4c19a'; 'pm1g4c19b'; 'ph2g6c19b'; 'ph1g6c19b'; 'ph1g2c20a'; 'ph2g2c20a'; 'pm1g4c20a'; 'pm1g4c20b'; 'pl2g6c20b'; 'pl1g6c20b'; 'pl1g2c21a'; 'pl2g2c21a'; 'pm1g4c21a'; 'pm1g4c21b'; 'ph2g6c21b'; 'ph1g6c21b'; 'ph1g2c22a'; 'ph2g2c22a'; 'pm1g4c22a'; 'pm1g4c22b'; 'pl2g6c22b'; 'pl1g6c22b'; 'pl1g2c23a'; 'pl2g2c23a'; 'pm1g4c23a'; 'pm1g4c23b'; 'ph2g6c23b'; 'ph1g6c23b'; 'ph1g2c24a'; 'ph2g2c24a'; 'pm1g4c24a'; 'pm1g4c24b'; 'pl2g6c24b'; 'pl1g6c24b'; 'pl1g2c25a'; 'pl2g2c25a'; 'pm1g4c25a'; 'pm1g4c25b'; 'ph2g6c25b'; 'ph1g6c25b'; 'ph1g2c26a'; 'ph2g2c26a'; 'pm1g4c26a'; 'pm1g4c26b'; 'pl2g6c26b'; 'pl1g6c26b'; 'pl1g2c27a'; 'pl2g2c27a'; 'pm1g4c27a'; 'pm1g4c27b'; 'ph2g6c27b'; 'ph1g6c27b'; 'ph1g2c28a'; 'ph2g2c28a'; 'pm1g4c28a'; 'pm1g4c28b'; 'pl2g6c28b'; 'pl1g6c28b'; 'pl1g2c29a'; 'pl2g2c29a'; 'pm1g4c29a'; 'pm1g4c29b'; 'ph2g6c29b'; 'ph1g6c29b' ];

AO.BPMx.Monitor.MemberOf = {'PlotFamily'; 'BPM'; 'BPMx'; 'Monitor'; 'Save';};
AO.BPMx.Monitor.Mode = 'Simulator';
AO.BPMx.Monitor.DataType = 'Scalar';
AO.BPMx.Monitor.ChannelNames = { 'V:2-SR:C30-BI:G2{PH1:11}SA:X';'V:2-SR:C30-BI:G2{PH2:26}SA:X';'V:2-SR:C30-BI:G4{PM1:55}SA:X';'V:2-SR:C30-BI:G4{PM1:65}SA:X';'V:2-SR:C30-BI:G6{PL2:85}SA:X';'V:2-SR:C30-BI:G6{PL1:105}SA:X';'V:2-SR:C01-BI:G2{PL1:130}SA:X';'V:2-SR:C01-BI:G2{PL2:150}SA:X';'V:2-SR:C01-BI:G4{PM1:175}SA:X';'V:2-SR:C01-BI:G4{PM1:185}SA:X';'V:2-SR:C01-BI:G6{PH2:209}SA:X';'V:2-SR:C01-BI:G6{PH1:224}SA:X';'V:2-SR:C02-BI:G2{PH1:245}SA:X';'V:2-SR:C02-BI:G2{PH2:260}SA:X';'V:2-SR:C02-BI:G4{PM1:289}SA:X';'V:2-SR:C02-BI:G4{PM1:299}SA:X';'V:2-SR:C02-BI:G6{PL2:319}SA:X';'V:2-SR:C02-BI:G6{PL1:339}SA:X';'V:2-SR:C03-BI:G2{PL1:377}SA:X';'V:2-SR:C03-BI:G2{PL2:397}SA:X';'V:2-SR:C03-BI:G4{PM1:422}SA:X';'V:2-SR:C03-BI:G4{PM1:432}SA:X';'V:2-SR:C03-BI:G6{PH2:456}SA:X';'V:2-SR:C03-BI:G6{PH1:471}SA:X';'V:2-SR:C04-BI:G2{PH1:492}SA:X';'V:2-SR:C04-BI:G2{PH2:507}SA:X';'V:2-SR:C04-BI:G4{PM1:536}SA:X';'V:2-SR:C04-BI:G4{PM1:546}SA:X';'V:2-SR:C04-BI:G6{PL2:566}SA:X';'V:2-SR:C04-BI:G6{PL1:586}SA:X';'V:2-SR:C05-BI:G2{PL1:625}SA:X';'V:2-SR:C05-BI:G2{PL2:645}SA:X';'V:2-SR:C05-BI:G4{PM1:670}SA:X';'V:2-SR:C05-BI:G4{PM1:680}SA:X';'V:2-SR:C05-BI:G6{PH2:704}SA:X';'V:2-SR:C05-BI:G6{PH1:719}SA:X';'V:2-SR:C06-BI:G2{PH1:740}SA:X';'V:2-SR:C06-BI:G2{PH2:755}SA:X';'V:2-SR:C06-BI:G4{PM1:784}SA:X';'V:2-SR:C06-BI:G4{PM1:794}SA:X';'V:2-SR:C06-BI:G6{PL2:814}SA:X';'V:2-SR:C06-BI:G6{PL1:834}SA:X';'V:2-SR:C07-BI:G2{PL1:859}SA:X';'V:2-SR:C07-BI:G2{PL2:879}SA:X';'V:2-SR:C07-BI:G4{PM1:904}SA:X';'V:2-SR:C07-BI:G4{PM1:914}SA:X';'V:2-SR:C07-BI:G6{PH2:938}SA:X';'V:2-SR:C07-BI:G6{PH1:953}SA:X';'V:2-SR:C08-BI:G2{PH1:998}SA:X';'V:2-SR:C08-BI:G2{PH2:1013}SA:X';'V:2-SR:C08-BI:G4{PM1:1042}SA:X';'V:2-SR:C08-BI:G4{PM1:1052}SA:X';'V:2-SR:C08-BI:G6{PL2:1072}SA:X';'V:2-SR:C08-BI:G6{PL1:1092}SA:X';'V:2-SR:C09-BI:G2{PL1:1117}SA:X';'V:2-SR:C09-BI:G2{PL2:1137}SA:X';'V:2-SR:C09-BI:G4{PM1:1162}SA:X';'V:2-SR:C09-BI:G4{PM1:1172}SA:X';'V:2-SR:C09-BI:G6{PH2:1196}SA:X';'V:2-SR:C09-BI:G6{PH1:1211}SA:X';'V:2-SR:C10-BI:G2{PH1:1245}SA:X';'V:2-SR:C10-BI:G2{PH2:1260}SA:X';'V:2-SR:C10-BI:G4{PM1:1289}SA:X';'V:2-SR:C10-BI:G4{PM1:1299}SA:X';'V:2-SR:C10-BI:G6{PL2:1319}SA:X';'V:2-SR:C10-BI:G6{PL1:1339}SA:X';'V:2-SR:C11-BI:G2{PL1:1377}SA:X';'V:2-SR:C11-BI:G2{PL2:1397}SA:X';'V:2-SR:C11-BI:G4{PM1:1422}SA:X';'V:2-SR:C11-BI:G4{PM1:1432}SA:X';'V:2-SR:C11-BI:G6{PH2:1456}SA:X';'V:2-SR:C11-BI:G6{PH1:1471}SA:X';'V:2-SR:C12-BI:G2{PH1:1492}SA:X';'V:2-SR:C12-BI:G2{PH2:1507}SA:X';'V:2-SR:C12-BI:G4{PM1:1536}SA:X';'V:2-SR:C12-BI:G4{PM1:1546}SA:X';'V:2-SR:C12-BI:G6{PL2:1566}SA:X';'V:2-SR:C12-BI:G6{PL1:1586}SA:X';'V:2-SR:C13-BI:G2{PL1:1611}SA:X';'V:2-SR:C13-BI:G2{PL2:1631}SA:X';'V:2-SR:C13-BI:G4{PM1:1656}SA:X';'V:2-SR:C13-BI:G4{PM1:1666}SA:X';'V:2-SR:C13-BI:G6{PH2:1690}SA:X';'V:2-SR:C13-BI:G6{PH1:1705}SA:X';'V:2-SR:C14-BI:G2{PH1:1726}SA:X';'V:2-SR:C14-BI:G2{PH2:1741}SA:X';'V:2-SR:C14-BI:G4{PM1:1770}SA:X';'V:2-SR:C14-BI:G4{PM1:1780}SA:X';'V:2-SR:C14-BI:G6{PL2:1800}SA:X';'V:2-SR:C14-BI:G6{PL1:1820}SA:X';'V:2-SR:C15-BI:G2{PL1:1845}SA:X';'V:2-SR:C15-BI:G2{PL2:1865}SA:X';'V:2-SR:C15-BI:G4{PM1:1890}SA:X';'V:2-SR:C15-BI:G4{PM1:1900}SA:X';'V:2-SR:C15-BI:G6{PH2:1924}SA:X';'V:2-SR:C15-BI:G6{PH1:1939}SA:X';'V:2-SR:C16-BI:G2{PH1:1960}SA:X';'V:2-SR:C16-BI:G2{PH2:1975}SA:X';'V:2-SR:C16-BI:G4{PM1:2004}SA:X';'V:2-SR:C16-BI:G4{PM1:2014}SA:X';'V:2-SR:C16-BI:G6{PL2:2034}SA:X';'V:2-SR:C16-BI:G6{PL1:2054}SA:X';'V:2-SR:C17-BI:G2{PL1:2079}SA:X';'V:2-SR:C17-BI:G2{PL2:2099}SA:X';'V:2-SR:C17-BI:G4{PM1:2124}SA:X';'V:2-SR:C17-BI:G4{PM1:2134}SA:X';'V:2-SR:C17-BI:G6{PH2:2158}SA:X';'V:2-SR:C17-BI:G6{PH1:2173}SA:X';'V:2-SR:C18-BI:G2{PH1:2218}SA:X';'V:2-SR:C18-BI:G2{PH2:2233}SA:X';'V:2-SR:C18-BI:G4{PM1:2262}SA:X';'V:2-SR:C18-BI:G4{PM1:2272}SA:X';'V:2-SR:C18-BI:G6{PL2:2292}SA:X';'V:2-SR:C18-BI:G6{PL1:2312}SA:X';'V:2-SR:C19-BI:G2{PL1:2337}SA:X';'V:2-SR:C19-BI:G2{PL2:2357}SA:X';'V:2-SR:C19-BI:G4{PM1:2382}SA:X';'V:2-SR:C19-BI:G4{PM1:2392}SA:X';'V:2-SR:C19-BI:G6{PH2:2416}SA:X';'V:2-SR:C19-BI:G6{PH1:2431}SA:X';'V:2-SR:C20-BI:G2{PH1:2452}SA:X';'V:2-SR:C20-BI:G2{PH2:2467}SA:X';'V:2-SR:C20-BI:G4{PM1:2496}SA:X';'V:2-SR:C20-BI:G4{PM1:2506}SA:X';'V:2-SR:C20-BI:G6{PL2:2526}SA:X';'V:2-SR:C20-BI:G6{PL1:2546}SA:X';'V:2-SR:C21-BI:G2{PL1:2571}SA:X';'V:2-SR:C21-BI:G2{PL2:2591}SA:X';'V:2-SR:C21-BI:G4{PM1:2616}SA:X';'V:2-SR:C21-BI:G4{PM1:2626}SA:X';'V:2-SR:C21-BI:G6{PH2:2650}SA:X';'V:2-SR:C21-BI:G6{PH1:2665}SA:X';'V:2-SR:C22-BI:G2{PH1:2686}SA:X';'V:2-SR:C22-BI:G2{PH2:2701}SA:X';'V:2-SR:C22-BI:G4{PM1:2730}SA:X';'V:2-SR:C22-BI:G4{PM1:2740}SA:X';'V:2-SR:C22-BI:G6{PL2:2760}SA:X';'V:2-SR:C22-BI:G6{PL1:2780}SA:X';'V:2-SR:C23-BI:G2{PL1:2825}SA:X';'V:2-SR:C23-BI:G2{PL2:2845}SA:X';'V:2-SR:C23-BI:G4{PM1:2870}SA:X';'V:2-SR:C23-BI:G4{PM1:2880}SA:X';'V:2-SR:C23-BI:G6{PH2:2904}SA:X';'V:2-SR:C23-BI:G6{PH1:2919}SA:X';'V:2-SR:C24-BI:G2{PH1:2940}SA:X';'V:2-SR:C24-BI:G2{PH2:2955}SA:X';'V:2-SR:C24-BI:G4{PM1:2984}SA:X';'V:2-SR:C24-BI:G4{PM1:2994}SA:X';'V:2-SR:C24-BI:G6{PL2:3014}SA:X';'V:2-SR:C24-BI:G6{PL1:3034}SA:X';'V:2-SR:C25-BI:G2{PL1:3059}SA:X';'V:2-SR:C25-BI:G2{PL2:3079}SA:X';'V:2-SR:C25-BI:G4{PM1:3104}SA:X';'V:2-SR:C25-BI:G4{PM1:3114}SA:X';'V:2-SR:C25-BI:G6{PH2:3138}SA:X';'V:2-SR:C25-BI:G6{PH1:3153}SA:X';'V:2-SR:C26-BI:G2{PH1:3174}SA:X';'V:2-SR:C26-BI:G2{PH2:3189}SA:X';'V:2-SR:C26-BI:G4{PM1:3218}SA:X';'V:2-SR:C26-BI:G4{PM1:3228}SA:X';'V:2-SR:C26-BI:G6{PL2:3248}SA:X';'V:2-SR:C26-BI:G6{PL1:3268}SA:X';'V:2-SR:C27-BI:G2{PL1:3293}SA:X';'V:2-SR:C27-BI:G2{PL2:3313}SA:X';'V:2-SR:C27-BI:G4{PM1:3338}SA:X';'V:2-SR:C27-BI:G4{PM1:3348}SA:X';'V:2-SR:C27-BI:G6{PH2:3372}SA:X';'V:2-SR:C27-BI:G6{PH1:3387}SA:X';'V:2-SR:C28-BI:G2{PH1:3432}SA:X';'V:2-SR:C28-BI:G2{PH2:3447}SA:X';'V:2-SR:C28-BI:G4{PM1:3476}SA:X';'V:2-SR:C28-BI:G4{PM1:3486}SA:X';'V:2-SR:C28-BI:G6{PL2:3506}SA:X';'V:2-SR:C28-BI:G6{PL1:3526}SA:X';'V:2-SR:C29-BI:G2{PL1:3551}SA:X';'V:2-SR:C29-BI:G2{PL2:3571}SA:X';'V:2-SR:C29-BI:G4{PM1:3596}SA:X';'V:2-SR:C29-BI:G4{PM1:3606}SA:X';'V:2-SR:C29-BI:G6{PH2:3630}SA:X';'V:2-SR:C29-BI:G6{PH1:3645}SA:X' };

AO.BPMx.Monitor.HW2PhysicsParams = 1e-3;  % HW [mm], Simulator [Meters]
AO.BPMx.Monitor.Physics2HWParams = 1000;
AO.BPMx.Monitor.Units            = 'Hardware';
AO.BPMx.Monitor.HWUnits          = 'mm';
AO.BPMx.Monitor.PhysicsUnits     = 'Meter';
%AO.BPMx.Monitor.SpecialFunctionGet = @getx_ltb;

AO.BPMx.Sum.MemberOf = {'PlotFamily'; 'BPM'; 'BPMx'; 'Monitor'; 'Sum';};
AO.BPMx.Sum.Mode = 'Simulator';
AO.BPMx.Sum.DataType = 'Scalar';
AO.BPMx.Sum.ChannelNames = { 'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1' };

AO.BPMx.Sum.HW2PhysicsParams = 1;  % HW [Volts], Simulator [Volts]
AO.BPMx.Sum.Physics2HWParams = 1;
AO.BPMx.Sum.Units            = 'Hardware';
AO.BPMx.Sum.HWUnits          = '';
AO.BPMx.Sum.PhysicsUnits     = '';

AO.BPMy.FamilyName  = 'BPMy';
AO.BPMy.MemberOf    = {'BPM'; 'BPMy';};
AO.BPMy.DeviceList  = AO.BPMx.DeviceList;
AO.BPMy.ElementList = AO.BPMx.ElementList;
AO.BPMy.Status      = AO.BPMx.Status;
AO.BPMy.Position    = [];
AO.BPMy.CommonNames = [ 'ph1g2c30a'; 'ph2g2c30a'; 'pm1g4c30a'; 'pm1g4c30b'; 'pl2g6c30b'; 'pl1g6c30b'; 'pl1g2c01a'; 'pl2g2c01a'; 'pm1g4c01a'; 'pm1g4c01b'; 'ph2g6c01b'; 'ph1g6c01b'; 'ph1g2c02a'; 'ph2g2c02a'; 'pm1g4c02a'; 'pm1g4c02b'; 'pl2g6c02b'; 'pl1g6c02b'; 'pl1g2c03a'; 'pl2g2c03a'; 'pm1g4c03a'; 'pm1g4c03b'; 'ph2g6c03b'; 'ph1g6c03b'; 'ph1g2c04a'; 'ph2g2c04a'; 'pm1g4c04a'; 'pm1g4c04b'; 'pl2g6c04b'; 'pl1g6c04b'; 'pl1g2c05a'; 'pl2g2c05a'; 'pm1g4c05a'; 'pm1g4c05b'; 'ph2g6c05b'; 'ph1g6c05b'; 'ph1g2c06a'; 'ph2g2c06a'; 'pm1g4c06a'; 'pm1g4c06b'; 'pl2g6c06b'; 'pl1g6c06b'; 'pl1g2c07a'; 'pl2g2c07a'; 'pm1g4c07a'; 'pm1g4c07b'; 'ph2g6c07b'; 'ph1g6c07b'; 'ph1g2c08a'; 'ph2g2c08a'; 'pm1g4c08a'; 'pm1g4c08b'; 'pl2g6c08b'; 'pl1g6c08b'; 'pl1g2c09a'; 'pl2g2c09a'; 'pm1g4c09a'; 'pm1g4c09b'; 'ph2g6c09b'; 'ph1g6c09b'; 'ph1g2c10a'; 'ph2g2c10a'; 'pm1g4c10a'; 'pm1g4c10b'; 'pl2g6c10b'; 'pl1g6c10b'; 'pl1g2c11a'; 'pl2g2c11a'; 'pm1g4c11a'; 'pm1g4c11b'; 'ph2g6c11b'; 'ph1g6c11b'; 'ph1g2c12a'; 'ph2g2c12a'; 'pm1g4c12a'; 'pm1g4c12b'; 'pl2g6c12b'; 'pl1g6c12b'; 'pl1g2c13a'; 'pl2g2c13a'; 'pm1g4c13a'; 'pm1g4c13b'; 'ph2g6c13b'; 'ph1g6c13b'; 'ph1g2c14a'; 'ph2g2c14a'; 'pm1g4c14a'; 'pm1g4c14b'; 'pl2g6c14b'; 'pl1g6c14b'; 'pl1g2c15a'; 'pl2g2c15a'; 'pm1g4c15a'; 'pm1g4c15b'; 'ph2g6c15b'; 'ph1g6c15b'; 'ph1g2c16a'; 'ph2g2c16a'; 'pm1g4c16a'; 'pm1g4c16b'; 'pl2g6c16b'; 'pl1g6c16b'; 'pl1g2c17a'; 'pl2g2c17a'; 'pm1g4c17a'; 'pm1g4c17b'; 'ph2g6c17b'; 'ph1g6c17b'; 'ph1g2c18a'; 'ph2g2c18a'; 'pm1g4c18a'; 'pm1g4c18b'; 'pl2g6c18b'; 'pl1g6c18b'; 'pl1g2c19a'; 'pl2g2c19a'; 'pm1g4c19a'; 'pm1g4c19b'; 'ph2g6c19b'; 'ph1g6c19b'; 'ph1g2c20a'; 'ph2g2c20a'; 'pm1g4c20a'; 'pm1g4c20b'; 'pl2g6c20b'; 'pl1g6c20b'; 'pl1g2c21a'; 'pl2g2c21a'; 'pm1g4c21a'; 'pm1g4c21b'; 'ph2g6c21b'; 'ph1g6c21b'; 'ph1g2c22a'; 'ph2g2c22a'; 'pm1g4c22a'; 'pm1g4c22b'; 'pl2g6c22b'; 'pl1g6c22b'; 'pl1g2c23a'; 'pl2g2c23a'; 'pm1g4c23a'; 'pm1g4c23b'; 'ph2g6c23b'; 'ph1g6c23b'; 'ph1g2c24a'; 'ph2g2c24a'; 'pm1g4c24a'; 'pm1g4c24b'; 'pl2g6c24b'; 'pl1g6c24b'; 'pl1g2c25a'; 'pl2g2c25a'; 'pm1g4c25a'; 'pm1g4c25b'; 'ph2g6c25b'; 'ph1g6c25b'; 'ph1g2c26a'; 'ph2g2c26a'; 'pm1g4c26a'; 'pm1g4c26b'; 'pl2g6c26b'; 'pl1g6c26b'; 'pl1g2c27a'; 'pl2g2c27a'; 'pm1g4c27a'; 'pm1g4c27b'; 'ph2g6c27b'; 'ph1g6c27b'; 'ph1g2c28a'; 'ph2g2c28a'; 'pm1g4c28a'; 'pm1g4c28b'; 'pl2g6c28b'; 'pl1g6c28b'; 'pl1g2c29a'; 'pl2g2c29a'; 'pm1g4c29a'; 'pm1g4c29b'; 'ph2g6c29b'; 'ph1g6c29b' ];

AO.BPMy.Monitor.MemberOf = {'PlotFamily'; 'BPM'; 'BPMy'; 'Monitor'; 'Save';};
AO.BPMy.Monitor.Mode = 'Simulator';
AO.BPMy.Monitor.DataType = 'Scalar';
AO.BPMy.Monitor.ChannelNames = { 'V:2-SR:C30-BI:G2{PH1:11}SA:X';'V:2-SR:C30-BI:G2{PH2:26}SA:X';'V:2-SR:C30-BI:G4{PM1:55}SA:X';'V:2-SR:C30-BI:G4{PM1:65}SA:X';'V:2-SR:C30-BI:G6{PL2:85}SA:X';'V:2-SR:C30-BI:G6{PL1:105}SA:X';'V:2-SR:C01-BI:G2{PL1:130}SA:X';'V:2-SR:C01-BI:G2{PL2:150}SA:X';'V:2-SR:C01-BI:G4{PM1:175}SA:X';'V:2-SR:C01-BI:G4{PM1:185}SA:X';'V:2-SR:C01-BI:G6{PH2:209}SA:X';'V:2-SR:C01-BI:G6{PH1:224}SA:X';'V:2-SR:C02-BI:G2{PH1:245}SA:X';'V:2-SR:C02-BI:G2{PH2:260}SA:X';'V:2-SR:C02-BI:G4{PM1:289}SA:X';'V:2-SR:C02-BI:G4{PM1:299}SA:X';'V:2-SR:C02-BI:G6{PL2:319}SA:X';'V:2-SR:C02-BI:G6{PL1:339}SA:X';'V:2-SR:C03-BI:G2{PL1:377}SA:X';'V:2-SR:C03-BI:G2{PL2:397}SA:X';'V:2-SR:C03-BI:G4{PM1:422}SA:X';'V:2-SR:C03-BI:G4{PM1:432}SA:X';'V:2-SR:C03-BI:G6{PH2:456}SA:X';'V:2-SR:C03-BI:G6{PH1:471}SA:X';'V:2-SR:C04-BI:G2{PH1:492}SA:X';'V:2-SR:C04-BI:G2{PH2:507}SA:X';'V:2-SR:C04-BI:G4{PM1:536}SA:X';'V:2-SR:C04-BI:G4{PM1:546}SA:X';'V:2-SR:C04-BI:G6{PL2:566}SA:X';'V:2-SR:C04-BI:G6{PL1:586}SA:X';'V:2-SR:C05-BI:G2{PL1:625}SA:X';'V:2-SR:C05-BI:G2{PL2:645}SA:X';'V:2-SR:C05-BI:G4{PM1:670}SA:X';'V:2-SR:C05-BI:G4{PM1:680}SA:X';'V:2-SR:C05-BI:G6{PH2:704}SA:X';'V:2-SR:C05-BI:G6{PH1:719}SA:X';'V:2-SR:C06-BI:G2{PH1:740}SA:X';'V:2-SR:C06-BI:G2{PH2:755}SA:X';'V:2-SR:C06-BI:G4{PM1:784}SA:X';'V:2-SR:C06-BI:G4{PM1:794}SA:X';'V:2-SR:C06-BI:G6{PL2:814}SA:X';'V:2-SR:C06-BI:G6{PL1:834}SA:X';'V:2-SR:C07-BI:G2{PL1:859}SA:X';'V:2-SR:C07-BI:G2{PL2:879}SA:X';'V:2-SR:C07-BI:G4{PM1:904}SA:X';'V:2-SR:C07-BI:G4{PM1:914}SA:X';'V:2-SR:C07-BI:G6{PH2:938}SA:X';'V:2-SR:C07-BI:G6{PH1:953}SA:X';'V:2-SR:C08-BI:G2{PH1:998}SA:X';'V:2-SR:C08-BI:G2{PH2:1013}SA:X';'V:2-SR:C08-BI:G4{PM1:1042}SA:X';'V:2-SR:C08-BI:G4{PM1:1052}SA:X';'V:2-SR:C08-BI:G6{PL2:1072}SA:X';'V:2-SR:C08-BI:G6{PL1:1092}SA:X';'V:2-SR:C09-BI:G2{PL1:1117}SA:X';'V:2-SR:C09-BI:G2{PL2:1137}SA:X';'V:2-SR:C09-BI:G4{PM1:1162}SA:X';'V:2-SR:C09-BI:G4{PM1:1172}SA:X';'V:2-SR:C09-BI:G6{PH2:1196}SA:X';'V:2-SR:C09-BI:G6{PH1:1211}SA:X';'V:2-SR:C10-BI:G2{PH1:1245}SA:X';'V:2-SR:C10-BI:G2{PH2:1260}SA:X';'V:2-SR:C10-BI:G4{PM1:1289}SA:X';'V:2-SR:C10-BI:G4{PM1:1299}SA:X';'V:2-SR:C10-BI:G6{PL2:1319}SA:X';'V:2-SR:C10-BI:G6{PL1:1339}SA:X';'V:2-SR:C11-BI:G2{PL1:1377}SA:X';'V:2-SR:C11-BI:G2{PL2:1397}SA:X';'V:2-SR:C11-BI:G4{PM1:1422}SA:X';'V:2-SR:C11-BI:G4{PM1:1432}SA:X';'V:2-SR:C11-BI:G6{PH2:1456}SA:X';'V:2-SR:C11-BI:G6{PH1:1471}SA:X';'V:2-SR:C12-BI:G2{PH1:1492}SA:X';'V:2-SR:C12-BI:G2{PH2:1507}SA:X';'V:2-SR:C12-BI:G4{PM1:1536}SA:X';'V:2-SR:C12-BI:G4{PM1:1546}SA:X';'V:2-SR:C12-BI:G6{PL2:1566}SA:X';'V:2-SR:C12-BI:G6{PL1:1586}SA:X';'V:2-SR:C13-BI:G2{PL1:1611}SA:X';'V:2-SR:C13-BI:G2{PL2:1631}SA:X';'V:2-SR:C13-BI:G4{PM1:1656}SA:X';'V:2-SR:C13-BI:G4{PM1:1666}SA:X';'V:2-SR:C13-BI:G6{PH2:1690}SA:X';'V:2-SR:C13-BI:G6{PH1:1705}SA:X';'V:2-SR:C14-BI:G2{PH1:1726}SA:X';'V:2-SR:C14-BI:G2{PH2:1741}SA:X';'V:2-SR:C14-BI:G4{PM1:1770}SA:X';'V:2-SR:C14-BI:G4{PM1:1780}SA:X';'V:2-SR:C14-BI:G6{PL2:1800}SA:X';'V:2-SR:C14-BI:G6{PL1:1820}SA:X';'V:2-SR:C15-BI:G2{PL1:1845}SA:X';'V:2-SR:C15-BI:G2{PL2:1865}SA:X';'V:2-SR:C15-BI:G4{PM1:1890}SA:X';'V:2-SR:C15-BI:G4{PM1:1900}SA:X';'V:2-SR:C15-BI:G6{PH2:1924}SA:X';'V:2-SR:C15-BI:G6{PH1:1939}SA:X';'V:2-SR:C16-BI:G2{PH1:1960}SA:X';'V:2-SR:C16-BI:G2{PH2:1975}SA:X';'V:2-SR:C16-BI:G4{PM1:2004}SA:X';'V:2-SR:C16-BI:G4{PM1:2014}SA:X';'V:2-SR:C16-BI:G6{PL2:2034}SA:X';'V:2-SR:C16-BI:G6{PL1:2054}SA:X';'V:2-SR:C17-BI:G2{PL1:2079}SA:X';'V:2-SR:C17-BI:G2{PL2:2099}SA:X';'V:2-SR:C17-BI:G4{PM1:2124}SA:X';'V:2-SR:C17-BI:G4{PM1:2134}SA:X';'V:2-SR:C17-BI:G6{PH2:2158}SA:X';'V:2-SR:C17-BI:G6{PH1:2173}SA:X';'V:2-SR:C18-BI:G2{PH1:2218}SA:X';'V:2-SR:C18-BI:G2{PH2:2233}SA:X';'V:2-SR:C18-BI:G4{PM1:2262}SA:X';'V:2-SR:C18-BI:G4{PM1:2272}SA:X';'V:2-SR:C18-BI:G6{PL2:2292}SA:X';'V:2-SR:C18-BI:G6{PL1:2312}SA:X';'V:2-SR:C19-BI:G2{PL1:2337}SA:X';'V:2-SR:C19-BI:G2{PL2:2357}SA:X';'V:2-SR:C19-BI:G4{PM1:2382}SA:X';'V:2-SR:C19-BI:G4{PM1:2392}SA:X';'V:2-SR:C19-BI:G6{PH2:2416}SA:X';'V:2-SR:C19-BI:G6{PH1:2431}SA:X';'V:2-SR:C20-BI:G2{PH1:2452}SA:X';'V:2-SR:C20-BI:G2{PH2:2467}SA:X';'V:2-SR:C20-BI:G4{PM1:2496}SA:X';'V:2-SR:C20-BI:G4{PM1:2506}SA:X';'V:2-SR:C20-BI:G6{PL2:2526}SA:X';'V:2-SR:C20-BI:G6{PL1:2546}SA:X';'V:2-SR:C21-BI:G2{PL1:2571}SA:X';'V:2-SR:C21-BI:G2{PL2:2591}SA:X';'V:2-SR:C21-BI:G4{PM1:2616}SA:X';'V:2-SR:C21-BI:G4{PM1:2626}SA:X';'V:2-SR:C21-BI:G6{PH2:2650}SA:X';'V:2-SR:C21-BI:G6{PH1:2665}SA:X';'V:2-SR:C22-BI:G2{PH1:2686}SA:X';'V:2-SR:C22-BI:G2{PH2:2701}SA:X';'V:2-SR:C22-BI:G4{PM1:2730}SA:X';'V:2-SR:C22-BI:G4{PM1:2740}SA:X';'V:2-SR:C22-BI:G6{PL2:2760}SA:X';'V:2-SR:C22-BI:G6{PL1:2780}SA:X';'V:2-SR:C23-BI:G2{PL1:2825}SA:X';'V:2-SR:C23-BI:G2{PL2:2845}SA:X';'V:2-SR:C23-BI:G4{PM1:2870}SA:X';'V:2-SR:C23-BI:G4{PM1:2880}SA:X';'V:2-SR:C23-BI:G6{PH2:2904}SA:X';'V:2-SR:C23-BI:G6{PH1:2919}SA:X';'V:2-SR:C24-BI:G2{PH1:2940}SA:X';'V:2-SR:C24-BI:G2{PH2:2955}SA:X';'V:2-SR:C24-BI:G4{PM1:2984}SA:X';'V:2-SR:C24-BI:G4{PM1:2994}SA:X';'V:2-SR:C24-BI:G6{PL2:3014}SA:X';'V:2-SR:C24-BI:G6{PL1:3034}SA:X';'V:2-SR:C25-BI:G2{PL1:3059}SA:X';'V:2-SR:C25-BI:G2{PL2:3079}SA:X';'V:2-SR:C25-BI:G4{PM1:3104}SA:X';'V:2-SR:C25-BI:G4{PM1:3114}SA:X';'V:2-SR:C25-BI:G6{PH2:3138}SA:X';'V:2-SR:C25-BI:G6{PH1:3153}SA:X';'V:2-SR:C26-BI:G2{PH1:3174}SA:X';'V:2-SR:C26-BI:G2{PH2:3189}SA:X';'V:2-SR:C26-BI:G4{PM1:3218}SA:X';'V:2-SR:C26-BI:G4{PM1:3228}SA:X';'V:2-SR:C26-BI:G6{PL2:3248}SA:X';'V:2-SR:C26-BI:G6{PL1:3268}SA:X';'V:2-SR:C27-BI:G2{PL1:3293}SA:X';'V:2-SR:C27-BI:G2{PL2:3313}SA:X';'V:2-SR:C27-BI:G4{PM1:3338}SA:X';'V:2-SR:C27-BI:G4{PM1:3348}SA:X';'V:2-SR:C27-BI:G6{PH2:3372}SA:X';'V:2-SR:C27-BI:G6{PH1:3387}SA:X';'V:2-SR:C28-BI:G2{PH1:3432}SA:X';'V:2-SR:C28-BI:G2{PH2:3447}SA:X';'V:2-SR:C28-BI:G4{PM1:3476}SA:X';'V:2-SR:C28-BI:G4{PM1:3486}SA:X';'V:2-SR:C28-BI:G6{PL2:3506}SA:X';'V:2-SR:C28-BI:G6{PL1:3526}SA:X';'V:2-SR:C29-BI:G2{PL1:3551}SA:X';'V:2-SR:C29-BI:G2{PL2:3571}SA:X';'V:2-SR:C29-BI:G4{PM1:3596}SA:X';'V:2-SR:C29-BI:G4{PM1:3606}SA:X';'V:2-SR:C29-BI:G6{PH2:3630}SA:X';'V:2-SR:C29-BI:G6{PH1:3645}SA:X' };

AO.BPMy.Monitor.HW2PhysicsParams = 1e-3;  % HW [mm], Simulator [Meters]
AO.BPMy.Monitor.Physics2HWParams = 1000;
AO.BPMy.Monitor.Units            = 'Hardware';
AO.BPMy.Monitor.HWUnits          = 'mm';
AO.BPMy.Monitor.PhysicsUnits     = 'Meter';

AO.BPMy.Sum.MemberOf = {'PlotFamily'; 'BPM'; 'BPMy'; 'Monitor'; 'Sum';};
AO.BPMy.Sum.Mode = 'Simulator';
AO.BPMy.Sum.DataType = 'Scalar';
AO.BPMy.Sum.ChannelNames = { 'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1';'pv1' };

AO.BPMy.Sum.HW2PhysicsParams = 1;  % HW [Volts], Simulator [Volts]
AO.BPMy.Sum.Physics2HWParams = 1;
AO.BPMy.Sum.Units            = 'Hardware';
AO.BPMy.Sum.HWUnits          = '';
AO.BPMy.Sum.PhysicsUnits     = '';




% HCM and VCM

% HCM
AO.HCM.FamilyName  = 'HCM';
AO.HCM.MemberOf    = {'HCM'; 'Magnet'; 'COR';};
AO.HCM.DeviceList  = [ 30 1; 30 2; 30 3; 30 4; 30 5; 30 6; 1 1; 1 2; 1 3; 1 4; 1 5; 1 6; 2 1; 2 2; 2 3; 2 4; 2 5; 2 6; 3 1; 3 2; 3 3; 3 4; 3 5; 3 6; 4 1; 4 2; 4 3; 4 4; 4 5; 4 6; 5 1; 5 2; 5 3; 5 4; 5 5; 5 6; 6 1; 6 2; 6 3; 6 4; 6 5; 6 6; 7 1; 7 2; 7 3; 7 4; 7 5; 7 6; 8 1; 8 2; 8 3; 8 4; 8 5; 8 6; 9 1; 9 2; 9 3; 9 4; 9 5; 9 6; 10 1; 10 2; 10 3; 10 4; 10 5; 10 6; 11 1; 11 2; 11 3; 11 4; 11 5; 11 6; 12 1; 12 2; 12 3; 12 4; 12 5; 12 6; 13 1; 13 2; 13 3; 13 4; 13 5; 13 6; 14 1; 14 2; 14 3; 14 4; 14 5; 14 6; 15 1; 15 2; 15 3; 15 4; 15 5; 15 6; 16 1; 16 2; 16 3; 16 4; 16 5; 16 6; 17 1; 17 2; 17 3; 17 4; 17 5; 17 6; 18 1; 18 2; 18 3; 18 4; 18 5; 18 6; 19 1; 19 2; 19 3; 19 4; 19 5; 19 6; 20 1; 20 2; 20 3; 20 4; 20 5; 20 6; 21 1; 21 2; 21 3; 21 4; 21 5; 21 6; 22 1; 22 2; 22 3; 22 4; 22 5; 22 6; 23 1; 23 2; 23 3; 23 4; 23 5; 23 6; 24 1; 24 2; 24 3; 24 4; 24 5; 24 6; 25 1; 25 2; 25 3; 25 4; 25 5; 25 6; 26 1; 26 2; 26 3; 26 4; 26 5; 26 6; 27 1; 27 2; 27 3; 27 4; 27 5; 27 6; 28 1; 28 2; 28 3; 28 4; 28 5; 28 6; 29 1; 29 2; 29 3; 29 4; 29 5; 29 6 ];
AO.HCM.ElementList = (1:size(AO.HCM.DeviceList,1))';
AO.HCM.Status      = ones(size(AO.HCM.DeviceList,1),1);
AO.HCM.Position    = [];
AO.HCM.CommonNames = { 'ch1g2c30a';'ch2g2c30a';'cm1g4c30a';'cm1g4c30b';'cl2g6c30b';'cl1g6c30b';'cl1g2c01a';'cl2g2c01a';'cm1g4c01a';'cm1g4c01b';'ch2g6c01b';'ch1g6c01b';'ch1g2c02a';'ch2g2c02a';'cm1g4c02a';'cm1g4c02b';'cl2g6c02b';'cl1g6c02b';'cl1g2c03a';'cl2g2c03a';'cm1g4c03a';'cm1g4c03b';'ch2g6c03b';'ch1g6c03b';'ch1g2c04a';'ch2g2c04a';'cm1g4c04a';'cm1g4c04b';'cl2g6c04b';'cl1g6c04b';'cl1g2c05a';'cl2g2c05a';'cm1g4c05a';'cm1g4c05b';'ch2g6c05b';'ch1g6c05b';'ch1g2c06a';'ch2g2c06a';'cm1g4c06a';'cm1g4c06b';'cl2g6c06b';'cl1g6c06b';'cl1g2c07a';'cl2g2c07a';'cm1g4c07a';'cm1g4c07b';'ch2g6c07b';'ch1g6c07b';'ch1g2c08a';'ch2g2c08a';'cm1g4c08a';'cm1g4c08b';'cl2g6c08b';'cl1g6c08b';'cl1g2c09a';'cl2g2c09a';'cm1g4c09a';'cm1g4c09b';'ch2g6c09b';'ch1g6c09b';'ch1g2c10a';'ch2g2c10a';'cm1g4c10a';'cm1g4c10b';'cl2g6c10b';'cl1g6c10b';'cl1g2c11a';'cl2g2c11a';'cm1g4c11a';'cm1g4c11b';'ch2g6c11b';'ch1g6c11b';'ch1g2c12a';'ch2g2c12a';'cm1g4c12a';'cm1g4c12b';'cl2g6c12b';'cl1g6c12b';'cl1g2c13a';'cl2g2c13a';'cm1g4c13a';'cm1g4c13b';'ch2g6c13b';'ch1g6c13b';'ch1g2c14a';'ch2g2c14a';'cm1g4c14a';'cm1g4c14b';'cl2g6c14b';'cl1g6c14b';'cl1g2c15a';'cl2g2c15a';'cm1g4c15a';'cm1g4c15b';'ch2g6c15b';'ch1g6c15b';'ch1g2c16a';'ch2g2c16a';'cm1g4c16a';'cm1g4c16b';'cl2g6c16b';'cl1g6c16b';'cl1g2c17a';'cl2g2c17a';'cm1g4c17a';'cm1g4c17b';'ch2g6c17b';'ch1g6c17b';'ch1g2c18a';'ch2g2c18a';'cm1g4c18a';'cm1g4c18b';'cl2g6c18b';'cl1g6c18b';'cl1g2c19a';'cl2g2c19a';'cm1g4c19a';'cm1g4c19b';'ch2g6c19b';'ch1g6c19b';'ch1g2c20a';'ch2g2c20a';'cm1g4c20a';'cm1g4c20b';'cl2g6c20b';'cl1g6c20b';'cl1g2c21a';'cl2g2c21a';'cm1g4c21a';'cm1g4c21b';'ch2g6c21b';'ch1g6c21b';'ch1g2c22a';'ch2g2c22a';'cm1g4c22a';'cm1g4c22b';'cl2g6c22b';'cl1g6c22b';'cl1g2c23a';'cl2g2c23a';'cm1g4c23a';'cm1g4c23b';'ch2g6c23b';'ch1g6c23b';'ch1g2c24a';'ch2g2c24a';'cm1g4c24a';'cm1g4c24b';'cl2g6c24b';'cl1g6c24b';'cl1g2c25a';'cl2g2c25a';'cm1g4c25a';'cm1g4c25b';'ch2g6c25b';'ch1g6c25b';'ch1g2c26a';'ch2g2c26a';'cm1g4c26a';'cm1g4c26b';'cl2g6c26b';'cl1g6c26b';'cl1g2c27a';'cl2g2c27a';'cm1g4c27a';'cm1g4c27b';'ch2g6c27b';'ch1g6c27b';'ch1g2c28a';'ch2g2c28a';'cm1g4c28a';'cm1g4c28b';'cl2g6c28b';'cl1g6c28b';'cl1g2c29a';'cl2g2c29a';'cm1g4c29a';'cm1g4c29b';'ch2g6c29b';'ch1g6c29b' };

AO.HCM.Monitor.MemberOf = {'HCM'; 'Magnet'; 'COR'; 'Monitor'; 'PlotFamily'; 'Save';};
AO.HCM.Monitor.Mode = 'Simulator';
AO.HCM.Monitor.DataType = 'Scalar';
AO.HCM.Monitor.ChannelNames = { 'V:2-SR:C30-MG:G2{CXH1:16}Fld:I';'V:2-SR:C30-MG:G2{CXH2:31}Fld:I';'V:2-SR:C30-MG:G4{CXM1:42}Fld:I';'V:2-SR:C30-MG:G4{CXM1:70}Fld:I';'V:2-SR:C30-MG:G6{CXL2:90}Fld:I';'V:2-SR:C30-MG:G6{CXL1:99}Fld:I';'V:2-SR:C01-MG:G2{CXL1:135}Fld:I';'V:2-SR:C01-MG:G2{CXL2:144}Fld:I';'V:2-SR:C01-MG:G4{CXM1:162}Fld:I';'V:2-SR:C01-MG:G4{CXM1:190}Fld:I';'V:2-SR:C01-MG:G6{CXH2:203}Fld:I';'V:2-SR:C01-MG:G6{CXH1:218}Fld:I';'V:2-SR:C02-MG:G2{CXH1:250}Fld:I';'V:2-SR:C02-MG:G2{CXH2:265}Fld:I';'V:2-SR:C02-MG:G4{CXM1:276}Fld:I';'V:2-SR:C02-MG:G4{CXM1:304}Fld:I';'V:2-SR:C02-MG:G6{CXL2:324}Fld:I';'V:2-SR:C02-MG:G6{CXL1:333}Fld:I';'V:2-SR:C03-MG:G2{CXL1:382}Fld:I';'V:2-SR:C03-MG:G2{CXL2:391}Fld:I';'V:2-SR:C03-MG:G4{CXM1:409}Fld:I';'V:2-SR:C03-MG:G4{CXM1:437}Fld:I';'V:2-SR:C03-MG:G6{CXH2:450}Fld:I';'V:2-SR:C03-MG:G6{CXH1:465}Fld:I';'V:2-SR:C04-MG:G2{CXH1:497}Fld:I';'V:2-SR:C04-MG:G2{CXH2:512}Fld:I';'V:2-SR:C04-MG:G4{CXM1:523}Fld:I';'V:2-SR:C04-MG:G4{CXM1:551}Fld:I';'V:2-SR:C04-MG:G6{CXL2:571}Fld:I';'V:2-SR:C04-MG:G6{CXL1:580}Fld:I';'V:2-SR:C05-MG:G2{CXL1:630}Fld:I';'V:2-SR:C05-MG:G2{CXL2:639}Fld:I';'V:2-SR:C05-MG:G4{CXM1:657}Fld:I';'V:2-SR:C05-MG:G4{CXM1:685}Fld:I';'V:2-SR:C05-MG:G6{CXH2:698}Fld:I';'V:2-SR:C05-MG:G6{CXH1:713}Fld:I';'V:2-SR:C06-MG:G2{CXH1:745}Fld:I';'V:2-SR:C06-MG:G2{CXH2:760}Fld:I';'V:2-SR:C06-MG:G4{CXM1:771}Fld:I';'V:2-SR:C06-MG:G4{CXM1:799}Fld:I';'V:2-SR:C06-MG:G6{CXL2:819}Fld:I';'V:2-SR:C06-MG:G6{CXL1:828}Fld:I';'V:2-SR:C07-MG:G2{CXL1:864}Fld:I';'V:2-SR:C07-MG:G2{CXL2:873}Fld:I';'V:2-SR:C07-MG:G4{CXM1:891}Fld:I';'V:2-SR:C07-MG:G4{CXM1:919}Fld:I';'V:2-SR:C07-MG:G6{CXH2:932}Fld:I';'V:2-SR:C07-MG:G6{CXH1:947}Fld:I';'V:2-SR:C08-MG:G2{CXH1:1003}Fld:I';'V:2-SR:C08-MG:G2{CXH2:1018}Fld:I';'V:2-SR:C08-MG:G4{CXM1:1029}Fld:I';'V:2-SR:C08-MG:G4{CXM1:1057}Fld:I';'V:2-SR:C08-MG:G6{CXL2:1077}Fld:I';'V:2-SR:C08-MG:G6{CXL1:1086}Fld:I';'V:2-SR:C09-MG:G2{CXL1:1122}Fld:I';'V:2-SR:C09-MG:G2{CXL2:1131}Fld:I';'V:2-SR:C09-MG:G4{CXM1:1149}Fld:I';'V:2-SR:C09-MG:G4{CXM1:1177}Fld:I';'V:2-SR:C09-MG:G6{CXH2:1190}Fld:I';'V:2-SR:C09-MG:G6{CXH1:1205}Fld:I';'V:2-SR:C10-MG:G2{CXH1:1250}Fld:I';'V:2-SR:C10-MG:G2{CXH2:1265}Fld:I';'V:2-SR:C10-MG:G4{CXM1:1276}Fld:I';'V:2-SR:C10-MG:G4{CXM1:1304}Fld:I';'V:2-SR:C10-MG:G6{CXL2:1324}Fld:I';'V:2-SR:C10-MG:G6{CXL1:1333}Fld:I';'V:2-SR:C11-MG:G2{CXL1:1382}Fld:I';'V:2-SR:C11-MG:G2{CXL2:1391}Fld:I';'V:2-SR:C11-MG:G4{CXM1:1409}Fld:I';'V:2-SR:C11-MG:G4{CXM1:1437}Fld:I';'V:2-SR:C11-MG:G6{CXH2:1450}Fld:I';'V:2-SR:C11-MG:G6{CXH1:1465}Fld:I';'V:2-SR:C12-MG:G2{CXH1:1497}Fld:I';'V:2-SR:C12-MG:G2{CXH2:1512}Fld:I';'V:2-SR:C12-MG:G4{CXM1:1523}Fld:I';'V:2-SR:C12-MG:G4{CXM1:1551}Fld:I';'V:2-SR:C12-MG:G6{CXL2:1571}Fld:I';'V:2-SR:C12-MG:G6{CXL1:1580}Fld:I';'V:2-SR:C13-MG:G2{CXL1:1616}Fld:I';'V:2-SR:C13-MG:G2{CXL2:1625}Fld:I';'V:2-SR:C13-MG:G4{CXM1:1643}Fld:I';'V:2-SR:C13-MG:G4{CXM1:1671}Fld:I';'V:2-SR:C13-MG:G6{CXH2:1684}Fld:I';'V:2-SR:C13-MG:G6{CXH1:1699}Fld:I';'V:2-SR:C14-MG:G2{CXH1:1731}Fld:I';'V:2-SR:C14-MG:G2{CXH2:1746}Fld:I';'V:2-SR:C14-MG:G4{CXM1:1757}Fld:I';'V:2-SR:C14-MG:G4{CXM1:1785}Fld:I';'V:2-SR:C14-MG:G6{CXL2:1805}Fld:I';'V:2-SR:C14-MG:G6{CXL1:1814}Fld:I';'V:2-SR:C15-MG:G2{CXL1:1850}Fld:I';'V:2-SR:C15-MG:G2{CXL2:1859}Fld:I';'V:2-SR:C15-MG:G4{CXM1:1877}Fld:I';'V:2-SR:C15-MG:G4{CXM1:1905}Fld:I';'V:2-SR:C15-MG:G6{CXH2:1918}Fld:I';'V:2-SR:C15-MG:G6{CXH1:1933}Fld:I';'V:2-SR:C16-MG:G2{CXH1:1965}Fld:I';'V:2-SR:C16-MG:G2{CXH2:1980}Fld:I';'V:2-SR:C16-MG:G4{CXM1:1991}Fld:I';'V:2-SR:C16-MG:G4{CXM1:2019}Fld:I';'V:2-SR:C16-MG:G6{CXL2:2039}Fld:I';'V:2-SR:C16-MG:G6{CXL1:2048}Fld:I';'V:2-SR:C17-MG:G2{CXL1:2084}Fld:I';'V:2-SR:C17-MG:G2{CXL2:2093}Fld:I';'V:2-SR:C17-MG:G4{CXM1:2111}Fld:I';'V:2-SR:C17-MG:G4{CXM1:2139}Fld:I';'V:2-SR:C17-MG:G6{CXH2:2152}Fld:I';'V:2-SR:C17-MG:G6{CXH1:2167}Fld:I';'V:2-SR:C18-MG:G2{CXH1:2223}Fld:I';'V:2-SR:C18-MG:G2{CXH2:2238}Fld:I';'V:2-SR:C18-MG:G4{CXM1:2249}Fld:I';'V:2-SR:C18-MG:G4{CXM1:2277}Fld:I';'V:2-SR:C18-MG:G6{CXL2:2297}Fld:I';'V:2-SR:C18-MG:G6{CXL1:2306}Fld:I';'V:2-SR:C19-MG:G2{CXL1:2342}Fld:I';'V:2-SR:C19-MG:G2{CXL2:2351}Fld:I';'V:2-SR:C19-MG:G4{CXM1:2369}Fld:I';'V:2-SR:C19-MG:G4{CXM1:2397}Fld:I';'V:2-SR:C19-MG:G6{CXH2:2410}Fld:I';'V:2-SR:C19-MG:G6{CXH1:2425}Fld:I';'V:2-SR:C20-MG:G2{CXH1:2457}Fld:I';'V:2-SR:C20-MG:G2{CXH2:2472}Fld:I';'V:2-SR:C20-MG:G4{CXM1:2483}Fld:I';'V:2-SR:C20-MG:G4{CXM1:2511}Fld:I';'V:2-SR:C20-MG:G6{CXL2:2531}Fld:I';'V:2-SR:C20-MG:G6{CXL1:2540}Fld:I';'V:2-SR:C21-MG:G2{CXL1:2576}Fld:I';'V:2-SR:C21-MG:G2{CXL2:2585}Fld:I';'V:2-SR:C21-MG:G4{CXM1:2603}Fld:I';'V:2-SR:C21-MG:G4{CXM1:2631}Fld:I';'V:2-SR:C21-MG:G6{CXH2:2644}Fld:I';'V:2-SR:C21-MG:G6{CXH1:2659}Fld:I';'V:2-SR:C22-MG:G2{CXH1:2691}Fld:I';'V:2-SR:C22-MG:G2{CXH2:2706}Fld:I';'V:2-SR:C22-MG:G4{CXM1:2717}Fld:I';'V:2-SR:C22-MG:G4{CXM1:2745}Fld:I';'V:2-SR:C22-MG:G6{CXL2:2765}Fld:I';'V:2-SR:C22-MG:G6{CXL1:2774}Fld:I';'V:2-SR:C23-MG:G2{CXL1:2830}Fld:I';'V:2-SR:C23-MG:G2{CXL2:2839}Fld:I';'V:2-SR:C23-MG:G4{CXM1:2857}Fld:I';'V:2-SR:C23-MG:G4{CXM1:2885}Fld:I';'V:2-SR:C23-MG:G6{CXH2:2898}Fld:I';'V:2-SR:C23-MG:G6{CXH1:2913}Fld:I';'V:2-SR:C24-MG:G2{CXH1:2945}Fld:I';'V:2-SR:C24-MG:G2{CXH2:2960}Fld:I';'V:2-SR:C24-MG:G4{CXM1:2971}Fld:I';'V:2-SR:C24-MG:G4{CXM1:2999}Fld:I';'V:2-SR:C24-MG:G6{CXL2:3019}Fld:I';'V:2-SR:C24-MG:G6{CXL1:3028}Fld:I';'V:2-SR:C25-MG:G2{CXL1:3064}Fld:I';'V:2-SR:C25-MG:G2{CXL2:3073}Fld:I';'V:2-SR:C25-MG:G4{CXM1:3091}Fld:I';'V:2-SR:C25-MG:G4{CXM1:3119}Fld:I';'V:2-SR:C25-MG:G6{CXH2:3132}Fld:I';'V:2-SR:C25-MG:G6{CXH1:3147}Fld:I';'V:2-SR:C26-MG:G2{CXH1:3179}Fld:I';'V:2-SR:C26-MG:G2{CXH2:3194}Fld:I';'V:2-SR:C26-MG:G4{CXM1:3205}Fld:I';'V:2-SR:C26-MG:G4{CXM1:3233}Fld:I';'V:2-SR:C26-MG:G6{CXL2:3253}Fld:I';'V:2-SR:C26-MG:G6{CXL1:3262}Fld:I';'V:2-SR:C27-MG:G2{CXL1:3298}Fld:I';'V:2-SR:C27-MG:G2{CXL2:3307}Fld:I';'V:2-SR:C27-MG:G4{CXM1:3325}Fld:I';'V:2-SR:C27-MG:G4{CXM1:3353}Fld:I';'V:2-SR:C27-MG:G6{CXH2:3366}Fld:I';'V:2-SR:C27-MG:G6{CXH1:3381}Fld:I';'V:2-SR:C28-MG:G2{CXH1:3437}Fld:I';'V:2-SR:C28-MG:G2{CXH2:3452}Fld:I';'V:2-SR:C28-MG:G4{CXM1:3463}Fld:I';'V:2-SR:C28-MG:G4{CXM1:3491}Fld:I';'V:2-SR:C28-MG:G6{CXL2:3511}Fld:I';'V:2-SR:C28-MG:G6{CXL1:3520}Fld:I';'V:2-SR:C29-MG:G2{CXL1:3556}Fld:I';'V:2-SR:C29-MG:G2{CXL2:3565}Fld:I';'V:2-SR:C29-MG:G4{CXM1:3583}Fld:I';'V:2-SR:C29-MG:G4{CXM1:3611}Fld:I';'V:2-SR:C29-MG:G6{CXH2:3624}Fld:I';'V:2-SR:C29-MG:G6{CXH1:3639}Fld:I' };
AO.HCM.Monitor.HW2PhysicsFcn = @hw2at;
AO.HCM.Monitor.Physics2HWFcn = @at2hw;
AO.HCM.Monitor.Units        = 'Hardware';
AO.HCM.Monitor.HWUnits      = 'Ampere';
AO.HCM.Monitor.PhysicsUnits = 'Radian';
%AO.HCM.Monitor.Real2RawFcn = @real2raw_ltb;
%AO.HCM.Monitor.Raw2RealFcn = @raw2real_ltb;

AO.HCM.Setpoint.MemberOf = {'HCM'; 'Magnet'; 'COR'; 'Save/Restore'; 'Setpoint'};
AO.HCM.Setpoint.Mode = 'Simulator';
AO.HCM.Setpoint.DataType = 'Scalar';
AO.HCM.Setpoint.ChannelNames = { 'V:2-SR:C30-MG:G2{CXH1:16}Fld:SP';'V:2-SR:C30-MG:G2{CXH2:31}Fld:SP';'V:2-SR:C30-MG:G4{CXM1:42}Fld:SP';'V:2-SR:C30-MG:G4{CXM1:70}Fld:SP';'V:2-SR:C30-MG:G6{CXL2:90}Fld:SP';'V:2-SR:C30-MG:G6{CXL1:99}Fld:SP';'V:2-SR:C01-MG:G2{CXL1:135}Fld:SP';'V:2-SR:C01-MG:G2{CXL2:144}Fld:SP';'V:2-SR:C01-MG:G4{CXM1:162}Fld:SP';'V:2-SR:C01-MG:G4{CXM1:190}Fld:SP';'V:2-SR:C01-MG:G6{CXH2:203}Fld:SP';'V:2-SR:C01-MG:G6{CXH1:218}Fld:SP';'V:2-SR:C02-MG:G2{CXH1:250}Fld:SP';'V:2-SR:C02-MG:G2{CXH2:265}Fld:SP';'V:2-SR:C02-MG:G4{CXM1:276}Fld:SP';'V:2-SR:C02-MG:G4{CXM1:304}Fld:SP';'V:2-SR:C02-MG:G6{CXL2:324}Fld:SP';'V:2-SR:C02-MG:G6{CXL1:333}Fld:SP';'V:2-SR:C03-MG:G2{CXL1:382}Fld:SP';'V:2-SR:C03-MG:G2{CXL2:391}Fld:SP';'V:2-SR:C03-MG:G4{CXM1:409}Fld:SP';'V:2-SR:C03-MG:G4{CXM1:437}Fld:SP';'V:2-SR:C03-MG:G6{CXH2:450}Fld:SP';'V:2-SR:C03-MG:G6{CXH1:465}Fld:SP';'V:2-SR:C04-MG:G2{CXH1:497}Fld:SP';'V:2-SR:C04-MG:G2{CXH2:512}Fld:SP';'V:2-SR:C04-MG:G4{CXM1:523}Fld:SP';'V:2-SR:C04-MG:G4{CXM1:551}Fld:SP';'V:2-SR:C04-MG:G6{CXL2:571}Fld:SP';'V:2-SR:C04-MG:G6{CXL1:580}Fld:SP';'V:2-SR:C05-MG:G2{CXL1:630}Fld:SP';'V:2-SR:C05-MG:G2{CXL2:639}Fld:SP';'V:2-SR:C05-MG:G4{CXM1:657}Fld:SP';'V:2-SR:C05-MG:G4{CXM1:685}Fld:SP';'V:2-SR:C05-MG:G6{CXH2:698}Fld:SP';'V:2-SR:C05-MG:G6{CXH1:713}Fld:SP';'V:2-SR:C06-MG:G2{CXH1:745}Fld:SP';'V:2-SR:C06-MG:G2{CXH2:760}Fld:SP';'V:2-SR:C06-MG:G4{CXM1:771}Fld:SP';'V:2-SR:C06-MG:G4{CXM1:799}Fld:SP';'V:2-SR:C06-MG:G6{CXL2:819}Fld:SP';'V:2-SR:C06-MG:G6{CXL1:828}Fld:SP';'V:2-SR:C07-MG:G2{CXL1:864}Fld:SP';'V:2-SR:C07-MG:G2{CXL2:873}Fld:SP';'V:2-SR:C07-MG:G4{CXM1:891}Fld:SP';'V:2-SR:C07-MG:G4{CXM1:919}Fld:SP';'V:2-SR:C07-MG:G6{CXH2:932}Fld:SP';'V:2-SR:C07-MG:G6{CXH1:947}Fld:SP';'V:2-SR:C08-MG:G2{CXH1:1003}Fld:SP';'V:2-SR:C08-MG:G2{CXH2:1018}Fld:SP';'V:2-SR:C08-MG:G4{CXM1:1029}Fld:SP';'V:2-SR:C08-MG:G4{CXM1:1057}Fld:SP';'V:2-SR:C08-MG:G6{CXL2:1077}Fld:SP';'V:2-SR:C08-MG:G6{CXL1:1086}Fld:SP';'V:2-SR:C09-MG:G2{CXL1:1122}Fld:SP';'V:2-SR:C09-MG:G2{CXL2:1131}Fld:SP';'V:2-SR:C09-MG:G4{CXM1:1149}Fld:SP';'V:2-SR:C09-MG:G4{CXM1:1177}Fld:SP';'V:2-SR:C09-MG:G6{CXH2:1190}Fld:SP';'V:2-SR:C09-MG:G6{CXH1:1205}Fld:SP';'V:2-SR:C10-MG:G2{CXH1:1250}Fld:SP';'V:2-SR:C10-MG:G2{CXH2:1265}Fld:SP';'V:2-SR:C10-MG:G4{CXM1:1276}Fld:SP';'V:2-SR:C10-MG:G4{CXM1:1304}Fld:SP';'V:2-SR:C10-MG:G6{CXL2:1324}Fld:SP';'V:2-SR:C10-MG:G6{CXL1:1333}Fld:SP';'V:2-SR:C11-MG:G2{CXL1:1382}Fld:SP';'V:2-SR:C11-MG:G2{CXL2:1391}Fld:SP';'V:2-SR:C11-MG:G4{CXM1:1409}Fld:SP';'V:2-SR:C11-MG:G4{CXM1:1437}Fld:SP';'V:2-SR:C11-MG:G6{CXH2:1450}Fld:SP';'V:2-SR:C11-MG:G6{CXH1:1465}Fld:SP';'V:2-SR:C12-MG:G2{CXH1:1497}Fld:SP';'V:2-SR:C12-MG:G2{CXH2:1512}Fld:SP';'V:2-SR:C12-MG:G4{CXM1:1523}Fld:SP';'V:2-SR:C12-MG:G4{CXM1:1551}Fld:SP';'V:2-SR:C12-MG:G6{CXL2:1571}Fld:SP';'V:2-SR:C12-MG:G6{CXL1:1580}Fld:SP';'V:2-SR:C13-MG:G2{CXL1:1616}Fld:SP';'V:2-SR:C13-MG:G2{CXL2:1625}Fld:SP';'V:2-SR:C13-MG:G4{CXM1:1643}Fld:SP';'V:2-SR:C13-MG:G4{CXM1:1671}Fld:SP';'V:2-SR:C13-MG:G6{CXH2:1684}Fld:SP';'V:2-SR:C13-MG:G6{CXH1:1699}Fld:SP';'V:2-SR:C14-MG:G2{CXH1:1731}Fld:SP';'V:2-SR:C14-MG:G2{CXH2:1746}Fld:SP';'V:2-SR:C14-MG:G4{CXM1:1757}Fld:SP';'V:2-SR:C14-MG:G4{CXM1:1785}Fld:SP';'V:2-SR:C14-MG:G6{CXL2:1805}Fld:SP';'V:2-SR:C14-MG:G6{CXL1:1814}Fld:SP';'V:2-SR:C15-MG:G2{CXL1:1850}Fld:SP';'V:2-SR:C15-MG:G2{CXL2:1859}Fld:SP';'V:2-SR:C15-MG:G4{CXM1:1877}Fld:SP';'V:2-SR:C15-MG:G4{CXM1:1905}Fld:SP';'V:2-SR:C15-MG:G6{CXH2:1918}Fld:SP';'V:2-SR:C15-MG:G6{CXH1:1933}Fld:SP';'V:2-SR:C16-MG:G2{CXH1:1965}Fld:SP';'V:2-SR:C16-MG:G2{CXH2:1980}Fld:SP';'V:2-SR:C16-MG:G4{CXM1:1991}Fld:SP';'V:2-SR:C16-MG:G4{CXM1:2019}Fld:SP';'V:2-SR:C16-MG:G6{CXL2:2039}Fld:SP';'V:2-SR:C16-MG:G6{CXL1:2048}Fld:SP';'V:2-SR:C17-MG:G2{CXL1:2084}Fld:SP';'V:2-SR:C17-MG:G2{CXL2:2093}Fld:SP';'V:2-SR:C17-MG:G4{CXM1:2111}Fld:SP';'V:2-SR:C17-MG:G4{CXM1:2139}Fld:SP';'V:2-SR:C17-MG:G6{CXH2:2152}Fld:SP';'V:2-SR:C17-MG:G6{CXH1:2167}Fld:SP';'V:2-SR:C18-MG:G2{CXH1:2223}Fld:SP';'V:2-SR:C18-MG:G2{CXH2:2238}Fld:SP';'V:2-SR:C18-MG:G4{CXM1:2249}Fld:SP';'V:2-SR:C18-MG:G4{CXM1:2277}Fld:SP';'V:2-SR:C18-MG:G6{CXL2:2297}Fld:SP';'V:2-SR:C18-MG:G6{CXL1:2306}Fld:SP';'V:2-SR:C19-MG:G2{CXL1:2342}Fld:SP';'V:2-SR:C19-MG:G2{CXL2:2351}Fld:SP';'V:2-SR:C19-MG:G4{CXM1:2369}Fld:SP';'V:2-SR:C19-MG:G4{CXM1:2397}Fld:SP';'V:2-SR:C19-MG:G6{CXH2:2410}Fld:SP';'V:2-SR:C19-MG:G6{CXH1:2425}Fld:SP';'V:2-SR:C20-MG:G2{CXH1:2457}Fld:SP';'V:2-SR:C20-MG:G2{CXH2:2472}Fld:SP';'V:2-SR:C20-MG:G4{CXM1:2483}Fld:SP';'V:2-SR:C20-MG:G4{CXM1:2511}Fld:SP';'V:2-SR:C20-MG:G6{CXL2:2531}Fld:SP';'V:2-SR:C20-MG:G6{CXL1:2540}Fld:SP';'V:2-SR:C21-MG:G2{CXL1:2576}Fld:SP';'V:2-SR:C21-MG:G2{CXL2:2585}Fld:SP';'V:2-SR:C21-MG:G4{CXM1:2603}Fld:SP';'V:2-SR:C21-MG:G4{CXM1:2631}Fld:SP';'V:2-SR:C21-MG:G6{CXH2:2644}Fld:SP';'V:2-SR:C21-MG:G6{CXH1:2659}Fld:SP';'V:2-SR:C22-MG:G2{CXH1:2691}Fld:SP';'V:2-SR:C22-MG:G2{CXH2:2706}Fld:SP';'V:2-SR:C22-MG:G4{CXM1:2717}Fld:SP';'V:2-SR:C22-MG:G4{CXM1:2745}Fld:SP';'V:2-SR:C22-MG:G6{CXL2:2765}Fld:SP';'V:2-SR:C22-MG:G6{CXL1:2774}Fld:SP';'V:2-SR:C23-MG:G2{CXL1:2830}Fld:SP';'V:2-SR:C23-MG:G2{CXL2:2839}Fld:SP';'V:2-SR:C23-MG:G4{CXM1:2857}Fld:SP';'V:2-SR:C23-MG:G4{CXM1:2885}Fld:SP';'V:2-SR:C23-MG:G6{CXH2:2898}Fld:SP';'V:2-SR:C23-MG:G6{CXH1:2913}Fld:SP';'V:2-SR:C24-MG:G2{CXH1:2945}Fld:SP';'V:2-SR:C24-MG:G2{CXH2:2960}Fld:SP';'V:2-SR:C24-MG:G4{CXM1:2971}Fld:SP';'V:2-SR:C24-MG:G4{CXM1:2999}Fld:SP';'V:2-SR:C24-MG:G6{CXL2:3019}Fld:SP';'V:2-SR:C24-MG:G6{CXL1:3028}Fld:SP';'V:2-SR:C25-MG:G2{CXL1:3064}Fld:SP';'V:2-SR:C25-MG:G2{CXL2:3073}Fld:SP';'V:2-SR:C25-MG:G4{CXM1:3091}Fld:SP';'V:2-SR:C25-MG:G4{CXM1:3119}Fld:SP';'V:2-SR:C25-MG:G6{CXH2:3132}Fld:SP';'V:2-SR:C25-MG:G6{CXH1:3147}Fld:SP';'V:2-SR:C26-MG:G2{CXH1:3179}Fld:SP';'V:2-SR:C26-MG:G2{CXH2:3194}Fld:SP';'V:2-SR:C26-MG:G4{CXM1:3205}Fld:SP';'V:2-SR:C26-MG:G4{CXM1:3233}Fld:SP';'V:2-SR:C26-MG:G6{CXL2:3253}Fld:SP';'V:2-SR:C26-MG:G6{CXL1:3262}Fld:SP';'V:2-SR:C27-MG:G2{CXL1:3298}Fld:SP';'V:2-SR:C27-MG:G2{CXL2:3307}Fld:SP';'V:2-SR:C27-MG:G4{CXM1:3325}Fld:SP';'V:2-SR:C27-MG:G4{CXM1:3353}Fld:SP';'V:2-SR:C27-MG:G6{CXH2:3366}Fld:SP';'V:2-SR:C27-MG:G6{CXH1:3381}Fld:SP';'V:2-SR:C28-MG:G2{CXH1:3437}Fld:SP';'V:2-SR:C28-MG:G2{CXH2:3452}Fld:SP';'V:2-SR:C28-MG:G4{CXM1:3463}Fld:SP';'V:2-SR:C28-MG:G4{CXM1:3491}Fld:SP';'V:2-SR:C28-MG:G6{CXL2:3511}Fld:SP';'V:2-SR:C28-MG:G6{CXL1:3520}Fld:SP';'V:2-SR:C29-MG:G2{CXL1:3556}Fld:SP';'V:2-SR:C29-MG:G2{CXL2:3565}Fld:SP';'V:2-SR:C29-MG:G4{CXM1:3583}Fld:SP';'V:2-SR:C29-MG:G4{CXM1:3611}Fld:SP';'V:2-SR:C29-MG:G6{CXH2:3624}Fld:SP';'V:2-SR:C29-MG:G6{CXH1:3639}Fld:SP' };
AO.HCM.Setpoint.HW2PhysicsFcn = @hw2at;
AO.HCM.Setpoint.Physics2HWFcn = @at2hw;
AO.HCM.Setpoint.Units        = 'Hardware';
AO.HCM.Setpoint.HWUnits      = 'Ampere';
AO.HCM.Setpoint.PhysicsUnits = 'Radian';
AO.HCM.Setpoint.Range = [-3 3];
AO.HCM.Setpoint.Tolerance  = .1 * ones(length(AO.HCM.ElementList), 1);  % Hardware units
AO.HCM.Setpoint.DeltaRespMat = 1;
% AO.HCM.Setpoint.RampRate = 1;
% AO.HCM.Setpoint.RunFlagFcn = @getrunflag_ltb;
% AO.HCM.RampRate.MemberOf = {'HCM'; 'Magnet'; 'COR'; 'PlotFamily'; 'Save/Restore';};
% AO.HCM.RampRate.Mode = 'Simulator';
% AO.HCM.RampRate.DataType = 'Scalar';
% AO.HCM.RampRate.ChannelNames = getname_ltb(AO.HCM.FamilyName, 'RampRate');
% AO.HCM.RampRate.HW2PhysicsParams = 1;
% AO.HCM.RampRate.Physics2HWParams = 1;
% AO.HCM.RampRate.Units        = 'Hardware';
% AO.HCM.RampRate.HWUnits      = 'Ampere/Second';
% AO.HCM.RampRate.PhysicsUnits = 'Ampere/Second';

AO.HCM.OnControl.MemberOf = {'HCM'; 'Magnet'; 'COR'; 'PlotFamily'; 'Boolean Control';};
AO.HCM.OnControl.Mode = 'Simulator';
AO.HCM.OnControl.DataType = 'Scalar';
AO.HCM.OnControl.ChannelNames = { 'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv' };

AO.HCM.OnControl.HW2PhysicsParams = 1;
AO.HCM.OnControl.Physics2HWParams = 1;

AO.HCM.OnControl.Units        = 'Hardware';
AO.HCM.OnControl.HWUnits      = '';
AO.HCM.OnControl.PhysicsUnits = '';
AO.HCM.OnControl.Range = [0 1];
%AO.HCM.OnControl.SpecialFunctionSet = @setsp_OnControlMagnet;

% AO.HCM.On.MemberOf = {'HCM'; 'Magnet'; 'COR'; 'PlotFamily'; 'Boolean Monitor';};
% AO.HCM.On.Mode = 'Simulator';
% AO.HCM.On.DataType = 'Scalar';
% AO.HCM.On.ChannelNames = getname_ltb(AO.HCM.FamilyName, 'On');
% AO.HCM.On.HW2PhysicsParams = 1;
% AO.HCM.On.Physics2HWParams = 1;
% AO.HCM.On.Units        = 'Hardware';
% AO.HCM.On.HWUnits      = '';
% AO.HCM.On.PhysicsUnits = '';

AO.HCM.Fault.MemberOf = {'HCM'; 'Magnet'; 'COR'; 'PlotFamily'; 'Boolean Monitor';};
AO.HCM.Fault.Mode = 'Simulator';
AO.HCM.Fault.DataType = 'Scalar';
AO.HCM.Fault.ChannelNames = { 'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv' };

AO.HCM.Fault.HW2PhysicsParams = 1;
AO.HCM.Fault.Physics2HWParams = 1;
AO.HCM.Fault.Units        = 'Hardware';
AO.HCM.Fault.HWUnits      = '';
AO.HCM.Fault.PhysicsUnits = '';


% VCM
AO.VCM.FamilyName  = 'VCM';
AO.VCM.MemberOf    = {'VCM'; 'Magnet'; 'COR';};
AO.VCM.DeviceList  = AO.HCM.DeviceList;
AO.VCM.ElementList = (1:size(AO.VCM.DeviceList,1))';
AO.VCM.Status      = ones(size(AO.VCM.DeviceList,1),1);
AO.VCM.Position    = [];
AO.VCM.CommonNames = { 'ch1g2c30a';'ch2g2c30a';'cm1g4c30a';'cm1g4c30b';'cl2g6c30b';'cl1g6c30b';'cl1g2c01a';'cl2g2c01a';'cm1g4c01a';'cm1g4c01b';'ch2g6c01b';'ch1g6c01b';'ch1g2c02a';'ch2g2c02a';'cm1g4c02a';'cm1g4c02b';'cl2g6c02b';'cl1g6c02b';'cl1g2c03a';'cl2g2c03a';'cm1g4c03a';'cm1g4c03b';'ch2g6c03b';'ch1g6c03b';'ch1g2c04a';'ch2g2c04a';'cm1g4c04a';'cm1g4c04b';'cl2g6c04b';'cl1g6c04b';'cl1g2c05a';'cl2g2c05a';'cm1g4c05a';'cm1g4c05b';'ch2g6c05b';'ch1g6c05b';'ch1g2c06a';'ch2g2c06a';'cm1g4c06a';'cm1g4c06b';'cl2g6c06b';'cl1g6c06b';'cl1g2c07a';'cl2g2c07a';'cm1g4c07a';'cm1g4c07b';'ch2g6c07b';'ch1g6c07b';'ch1g2c08a';'ch2g2c08a';'cm1g4c08a';'cm1g4c08b';'cl2g6c08b';'cl1g6c08b';'cl1g2c09a';'cl2g2c09a';'cm1g4c09a';'cm1g4c09b';'ch2g6c09b';'ch1g6c09b';'ch1g2c10a';'ch2g2c10a';'cm1g4c10a';'cm1g4c10b';'cl2g6c10b';'cl1g6c10b';'cl1g2c11a';'cl2g2c11a';'cm1g4c11a';'cm1g4c11b';'ch2g6c11b';'ch1g6c11b';'ch1g2c12a';'ch2g2c12a';'cm1g4c12a';'cm1g4c12b';'cl2g6c12b';'cl1g6c12b';'cl1g2c13a';'cl2g2c13a';'cm1g4c13a';'cm1g4c13b';'ch2g6c13b';'ch1g6c13b';'ch1g2c14a';'ch2g2c14a';'cm1g4c14a';'cm1g4c14b';'cl2g6c14b';'cl1g6c14b';'cl1g2c15a';'cl2g2c15a';'cm1g4c15a';'cm1g4c15b';'ch2g6c15b';'ch1g6c15b';'ch1g2c16a';'ch2g2c16a';'cm1g4c16a';'cm1g4c16b';'cl2g6c16b';'cl1g6c16b';'cl1g2c17a';'cl2g2c17a';'cm1g4c17a';'cm1g4c17b';'ch2g6c17b';'ch1g6c17b';'ch1g2c18a';'ch2g2c18a';'cm1g4c18a';'cm1g4c18b';'cl2g6c18b';'cl1g6c18b';'cl1g2c19a';'cl2g2c19a';'cm1g4c19a';'cm1g4c19b';'ch2g6c19b';'ch1g6c19b';'ch1g2c20a';'ch2g2c20a';'cm1g4c20a';'cm1g4c20b';'cl2g6c20b';'cl1g6c20b';'cl1g2c21a';'cl2g2c21a';'cm1g4c21a';'cm1g4c21b';'ch2g6c21b';'ch1g6c21b';'ch1g2c22a';'ch2g2c22a';'cm1g4c22a';'cm1g4c22b';'cl2g6c22b';'cl1g6c22b';'cl1g2c23a';'cl2g2c23a';'cm1g4c23a';'cm1g4c23b';'ch2g6c23b';'ch1g6c23b';'ch1g2c24a';'ch2g2c24a';'cm1g4c24a';'cm1g4c24b';'cl2g6c24b';'cl1g6c24b';'cl1g2c25a';'cl2g2c25a';'cm1g4c25a';'cm1g4c25b';'ch2g6c25b';'ch1g6c25b';'ch1g2c26a';'ch2g2c26a';'cm1g4c26a';'cm1g4c26b';'cl2g6c26b';'cl1g6c26b';'cl1g2c27a';'cl2g2c27a';'cm1g4c27a';'cm1g4c27b';'ch2g6c27b';'ch1g6c27b';'ch1g2c28a';'ch2g2c28a';'cm1g4c28a';'cm1g4c28b';'cl2g6c28b';'cl1g6c28b';'cl1g2c29a';'cl2g2c29a';'cm1g4c29a';'cm1g4c29b';'ch2g6c29b';'ch1g6c29b' };

AO.VCM.Monitor.MemberOf = {'VCM'; 'Magnet'; 'COR'; 'Monitor'; 'PlotFamily'; 'Save';};
AO.VCM.Monitor.Mode = 'Simulator';
AO.VCM.Monitor.DataType = 'Scalar';
AO.VCM.Monitor.ChannelNames = { 'V:2-SR:C30-MG:G2{CYH1:17}Fld:I  ';'V:2-SR:C30-MG:G2{CYH2:32}Fld:I  ';'V:2-SR:C30-MG:G4{CYM1:43}Fld:I  ';'V:2-SR:C30-MG:G4{CYM1:71}Fld:I  ';'V:2-SR:C30-MG:G6{CYL2:91}Fld:I  ';'V:2-SR:C30-MG:G6{CYL1:100}Fld:I ';'V:2-SR:C01-MG:G2{CYL1:136}Fld:I ';'V:2-SR:C01-MG:G2{CYL2:145}Fld:I ';'V:2-SR:C01-MG:G4{CYM1:163}Fld:I ';'V:2-SR:C01-MG:G4{CYM1:191}Fld:I ';'V:2-SR:C01-MG:G6{CYH2:204}Fld:I ';'V:2-SR:C01-MG:G6{CYH1:219}Fld:I ';'V:2-SR:C02-MG:G2{CYH1:251}Fld:I ';'V:2-SR:C02-MG:G2{CYH2:266}Fld:I ';'V:2-SR:C02-MG:G4{CYM1:277}Fld:I ';'V:2-SR:C02-MG:G4{CYM1:305}Fld:I ';'V:2-SR:C02-MG:G6{CYL2:325}Fld:I ';'V:2-SR:C02-MG:G6{CYL1:334}Fld:I ';'V:2-SR:C03-MG:G2{CYL1:383}Fld:I ';'V:2-SR:C03-MG:G2{CYL2:392}Fld:I ';'V:2-SR:C03-MG:G4{CYM1:410}Fld:I ';'V:2-SR:C03-MG:G4{CYM1:438}Fld:I ';'V:2-SR:C03-MG:G6{CYH2:451}Fld:I ';'V:2-SR:C03-MG:G6{CYH1:466}Fld:I ';'V:2-SR:C04-MG:G2{CYH1:498}Fld:I ';'V:2-SR:C04-MG:G2{CYH2:513}Fld:I ';'V:2-SR:C04-MG:G4{CYM1:524}Fld:I ';'V:2-SR:C04-MG:G4{CYM1:552}Fld:I ';'V:2-SR:C04-MG:G6{CYL2:572}Fld:I ';'V:2-SR:C04-MG:G6{CYL1:581}Fld:I ';'V:2-SR:C05-MG:G2{CYL1:631}Fld:I ';'V:2-SR:C05-MG:G2{CYL2:640}Fld:I ';'V:2-SR:C05-MG:G4{CYM1:658}Fld:I ';'V:2-SR:C05-MG:G4{CYM1:686}Fld:I ';'V:2-SR:C05-MG:G6{CYH2:699}Fld:I ';'V:2-SR:C05-MG:G6{CYH1:714}Fld:I ';'V:2-SR:C06-MG:G2{CYH1:746}Fld:I ';'V:2-SR:C06-MG:G2{CYH2:761}Fld:I ';'V:2-SR:C06-MG:G4{CYM1:772}Fld:I ';'V:2-SR:C06-MG:G4{CYM1:800}Fld:I ';'V:2-SR:C06-MG:G6{CYL2:820}Fld:I ';'V:2-SR:C06-MG:G6{CYL1:829}Fld:I ';'V:2-SR:C07-MG:G2{CYL1:865}Fld:I ';'V:2-SR:C07-MG:G2{CYL2:874}Fld:I ';'V:2-SR:C07-MG:G4{CYM1:892}Fld:I ';'V:2-SR:C07-MG:G4{CYM1:920}Fld:I ';'V:2-SR:C07-MG:G6{CYH2:933}Fld:I ';'V:2-SR:C07-MG:G6{CYH1:948}Fld:I ';'V:2-SR:C08-MG:G2{CYH1:1004}Fld:I';'V:2-SR:C08-MG:G2{CYH2:1019}Fld:I';'V:2-SR:C08-MG:G4{CYM1:1030}Fld:I';'V:2-SR:C08-MG:G4{CYM1:1058}Fld:I';'V:2-SR:C08-MG:G6{CYL2:1078}Fld:I';'V:2-SR:C08-MG:G6{CYL1:1087}Fld:I';'V:2-SR:C09-MG:G2{CYL1:1123}Fld:I';'V:2-SR:C09-MG:G2{CYL2:1132}Fld:I';'V:2-SR:C09-MG:G4{CYM1:1150}Fld:I';'V:2-SR:C09-MG:G4{CYM1:1178}Fld:I';'V:2-SR:C09-MG:G6{CYH2:1191}Fld:I';'V:2-SR:C09-MG:G6{CYH1:1206}Fld:I';'V:2-SR:C10-MG:G2{CYH1:1251}Fld:I';'V:2-SR:C10-MG:G2{CYH2:1266}Fld:I';'V:2-SR:C10-MG:G4{CYM1:1277}Fld:I';'V:2-SR:C10-MG:G4{CYM1:1305}Fld:I';'V:2-SR:C10-MG:G6{CYL2:1325}Fld:I';'V:2-SR:C10-MG:G6{CYL1:1334}Fld:I';'V:2-SR:C11-MG:G2{CYL1:1383}Fld:I';'V:2-SR:C11-MG:G2{CYL2:1392}Fld:I';'V:2-SR:C11-MG:G4{CYM1:1410}Fld:I';'V:2-SR:C11-MG:G4{CYM1:1438}Fld:I';'V:2-SR:C11-MG:G6{CYH2:1451}Fld:I';'V:2-SR:C11-MG:G6{CYH1:1466}Fld:I';'V:2-SR:C12-MG:G2{CYH1:1498}Fld:I';'V:2-SR:C12-MG:G2{CYH2:1513}Fld:I';'V:2-SR:C12-MG:G4{CYM1:1524}Fld:I';'V:2-SR:C12-MG:G4{CYM1:1552}Fld:I';'V:2-SR:C12-MG:G6{CYL2:1572}Fld:I';'V:2-SR:C12-MG:G6{CYL1:1581}Fld:I';'V:2-SR:C13-MG:G2{CYL1:1617}Fld:I';'V:2-SR:C13-MG:G2{CYL2:1626}Fld:I';'V:2-SR:C13-MG:G4{CYM1:1644}Fld:I';'V:2-SR:C13-MG:G4{CYM1:1672}Fld:I';'V:2-SR:C13-MG:G6{CYH2:1685}Fld:I';'V:2-SR:C13-MG:G6{CYH1:1700}Fld:I';'V:2-SR:C14-MG:G2{CYH1:1732}Fld:I';'V:2-SR:C14-MG:G2{CYH2:1747}Fld:I';'V:2-SR:C14-MG:G4{CYM1:1758}Fld:I';'V:2-SR:C14-MG:G4{CYM1:1786}Fld:I';'V:2-SR:C14-MG:G6{CYL2:1806}Fld:I';'V:2-SR:C14-MG:G6{CYL1:1815}Fld:I';'V:2-SR:C15-MG:G2{CYL1:1851}Fld:I';'V:2-SR:C15-MG:G2{CYL2:1860}Fld:I';'V:2-SR:C15-MG:G4{CYM1:1878}Fld:I';'V:2-SR:C15-MG:G4{CYM1:1906}Fld:I';'V:2-SR:C15-MG:G6{CYH2:1919}Fld:I';'V:2-SR:C15-MG:G6{CYH1:1934}Fld:I';'V:2-SR:C16-MG:G2{CYH1:1966}Fld:I';'V:2-SR:C16-MG:G2{CYH2:1981}Fld:I';'V:2-SR:C16-MG:G4{CYM1:1992}Fld:I';'V:2-SR:C16-MG:G4{CYM1:2020}Fld:I';'V:2-SR:C16-MG:G6{CYL2:2040}Fld:I';'V:2-SR:C16-MG:G6{CYL1:2049}Fld:I';'V:2-SR:C17-MG:G2{CYL1:2085}Fld:I';'V:2-SR:C17-MG:G2{CYL2:2094}Fld:I';'V:2-SR:C17-MG:G4{CYM1:2112}Fld:I';'V:2-SR:C17-MG:G4{CYM1:2140}Fld:I';'V:2-SR:C17-MG:G6{CYH2:2153}Fld:I';'V:2-SR:C17-MG:G6{CYH1:2168}Fld:I';'V:2-SR:C18-MG:G2{CYH1:2224}Fld:I';'V:2-SR:C18-MG:G2{CYH2:2239}Fld:I';'V:2-SR:C18-MG:G4{CYM1:2250}Fld:I';'V:2-SR:C18-MG:G4{CYM1:2278}Fld:I';'V:2-SR:C18-MG:G6{CYL2:2298}Fld:I';'V:2-SR:C18-MG:G6{CYL1:2307}Fld:I';'V:2-SR:C19-MG:G2{CYL1:2343}Fld:I';'V:2-SR:C19-MG:G2{CYL2:2352}Fld:I';'V:2-SR:C19-MG:G4{CYM1:2370}Fld:I';'V:2-SR:C19-MG:G4{CYM1:2398}Fld:I';'V:2-SR:C19-MG:G6{CYH2:2411}Fld:I';'V:2-SR:C19-MG:G6{CYH1:2426}Fld:I';'V:2-SR:C20-MG:G2{CYH1:2458}Fld:I';'V:2-SR:C20-MG:G2{CYH2:2473}Fld:I';'V:2-SR:C20-MG:G4{CYM1:2484}Fld:I';'V:2-SR:C20-MG:G4{CYM1:2512}Fld:I';'V:2-SR:C20-MG:G6{CYL2:2532}Fld:I';'V:2-SR:C20-MG:G6{CYL1:2541}Fld:I';'V:2-SR:C21-MG:G2{CYL1:2577}Fld:I';'V:2-SR:C21-MG:G2{CYL2:2586}Fld:I';'V:2-SR:C21-MG:G4{CYM1:2604}Fld:I';'V:2-SR:C21-MG:G4{CYM1:2632}Fld:I';'V:2-SR:C21-MG:G6{CYH2:2645}Fld:I';'V:2-SR:C21-MG:G6{CYH1:2660}Fld:I';'V:2-SR:C22-MG:G2{CYH1:2692}Fld:I';'V:2-SR:C22-MG:G2{CYH2:2707}Fld:I';'V:2-SR:C22-MG:G4{CYM1:2718}Fld:I';'V:2-SR:C22-MG:G4{CYM1:2746}Fld:I';'V:2-SR:C22-MG:G6{CYL2:2766}Fld:I';'V:2-SR:C22-MG:G6{CYL1:2775}Fld:I';'V:2-SR:C23-MG:G2{CYL1:2831}Fld:I';'V:2-SR:C23-MG:G2{CYL2:2840}Fld:I';'V:2-SR:C23-MG:G4{CYM1:2858}Fld:I';'V:2-SR:C23-MG:G4{CYM1:2886}Fld:I';'V:2-SR:C23-MG:G6{CYH2:2899}Fld:I';'V:2-SR:C23-MG:G6{CYH1:2914}Fld:I';'V:2-SR:C24-MG:G2{CYH1:2946}Fld:I';'V:2-SR:C24-MG:G2{CYH2:2961}Fld:I';'V:2-SR:C24-MG:G4{CYM1:2972}Fld:I';'V:2-SR:C24-MG:G4{CYM1:3000}Fld:I';'V:2-SR:C24-MG:G6{CYL2:3020}Fld:I';'V:2-SR:C24-MG:G6{CYL1:3029}Fld:I';'V:2-SR:C25-MG:G2{CYL1:3065}Fld:I';'V:2-SR:C25-MG:G2{CYL2:3074}Fld:I';'V:2-SR:C25-MG:G4{CYM1:3092}Fld:I';'V:2-SR:C25-MG:G4{CYM1:3120}Fld:I';'V:2-SR:C25-MG:G6{CYH2:3133}Fld:I';'V:2-SR:C25-MG:G6{CYH1:3148}Fld:I';'V:2-SR:C26-MG:G2{CYH1:3180}Fld:I';'V:2-SR:C26-MG:G2{CYH2:3195}Fld:I';'V:2-SR:C26-MG:G4{CYM1:3206}Fld:I';'V:2-SR:C26-MG:G4{CYM1:3234}Fld:I';'V:2-SR:C26-MG:G6{CYL2:3254}Fld:I';'V:2-SR:C26-MG:G6{CYL1:3263}Fld:I';'V:2-SR:C27-MG:G2{CYL1:3299}Fld:I';'V:2-SR:C27-MG:G2{CYL2:3308}Fld:I';'V:2-SR:C27-MG:G4{CYM1:3326}Fld:I';'V:2-SR:C27-MG:G4{CYM1:3354}Fld:I';'V:2-SR:C27-MG:G6{CYH2:3367}Fld:I';'V:2-SR:C27-MG:G6{CYH1:3382}Fld:I';'V:2-SR:C28-MG:G2{CYH1:3438}Fld:I';'V:2-SR:C28-MG:G2{CYH2:3453}Fld:I';'V:2-SR:C28-MG:G4{CYM1:3464}Fld:I';'V:2-SR:C28-MG:G4{CYM1:3492}Fld:I';'V:2-SR:C28-MG:G6{CYL2:3512}Fld:I';'V:2-SR:C28-MG:G6{CYL1:3521}Fld:I';'V:2-SR:C29-MG:G2{CYL1:3557}Fld:I';'V:2-SR:C29-MG:G2{CYL2:3566}Fld:I';'V:2-SR:C29-MG:G4{CYM1:3584}Fld:I';'V:2-SR:C29-MG:G4{CYM1:3612}Fld:I';'V:2-SR:C29-MG:G6{CYH2:3625}Fld:I';'V:2-SR:C29-MG:G6{CYH1:3640}Fld:I' };

AO.VCM.Monitor.HW2PhysicsFcn = @hw2at;
AO.VCM.Monitor.Physics2HWFcn = @at2hw;
AO.VCM.Monitor.Units        = 'Hardware';
AO.VCM.Monitor.HWUnits      = 'Ampere';
AO.VCM.Monitor.PhysicsUnits = 'Radian';
%AO.VCM.Monitor.Real2RawFcn = @real2raw_ltb;
%AO.VCM.Monitor.Raw2RealFcn = @raw2real_ltb;

AO.VCM.Setpoint.MemberOf = {'VCM'; 'Magnet'; 'COR'; 'Save/Restore'; 'Setpoint'};
AO.VCM.Setpoint.Mode = 'Simulator';
AO.VCM.Setpoint.DataType = 'Scalar';
AO.VCM.Setpoint.ChannelNames = { 'V:2-SR:C30-MG:G2{CYH1:17}Fld:SP  ';'V:2-SR:C30-MG:G2{CYH2:32}Fld:SP  ';'V:2-SR:C30-MG:G4{CYM1:43}Fld:SP  ';'V:2-SR:C30-MG:G4{CYM1:71}Fld:SP  ';'V:2-SR:C30-MG:G6{CYL2:91}Fld:SP  ';'V:2-SR:C30-MG:G6{CYL1:100}Fld:SP ';'V:2-SR:C01-MG:G2{CYL1:136}Fld:SP ';'V:2-SR:C01-MG:G2{CYL2:145}Fld:SP ';'V:2-SR:C01-MG:G4{CYM1:163}Fld:SP ';'V:2-SR:C01-MG:G4{CYM1:191}Fld:SP ';'V:2-SR:C01-MG:G6{CYH2:204}Fld:SP ';'V:2-SR:C01-MG:G6{CYH1:219}Fld:SP ';'V:2-SR:C02-MG:G2{CYH1:251}Fld:SP ';'V:2-SR:C02-MG:G2{CYH2:266}Fld:SP ';'V:2-SR:C02-MG:G4{CYM1:277}Fld:SP ';'V:2-SR:C02-MG:G4{CYM1:305}Fld:SP ';'V:2-SR:C02-MG:G6{CYL2:325}Fld:SP ';'V:2-SR:C02-MG:G6{CYL1:334}Fld:SP ';'V:2-SR:C03-MG:G2{CYL1:383}Fld:SP ';'V:2-SR:C03-MG:G2{CYL2:392}Fld:SP ';'V:2-SR:C03-MG:G4{CYM1:410}Fld:SP ';'V:2-SR:C03-MG:G4{CYM1:438}Fld:SP ';'V:2-SR:C03-MG:G6{CYH2:451}Fld:SP ';'V:2-SR:C03-MG:G6{CYH1:466}Fld:SP ';'V:2-SR:C04-MG:G2{CYH1:498}Fld:SP ';'V:2-SR:C04-MG:G2{CYH2:513}Fld:SP ';'V:2-SR:C04-MG:G4{CYM1:524}Fld:SP ';'V:2-SR:C04-MG:G4{CYM1:552}Fld:SP ';'V:2-SR:C04-MG:G6{CYL2:572}Fld:SP ';'V:2-SR:C04-MG:G6{CYL1:581}Fld:SP ';'V:2-SR:C05-MG:G2{CYL1:631}Fld:SP ';'V:2-SR:C05-MG:G2{CYL2:640}Fld:SP ';'V:2-SR:C05-MG:G4{CYM1:658}Fld:SP ';'V:2-SR:C05-MG:G4{CYM1:686}Fld:SP ';'V:2-SR:C05-MG:G6{CYH2:699}Fld:SP ';'V:2-SR:C05-MG:G6{CYH1:714}Fld:SP ';'V:2-SR:C06-MG:G2{CYH1:746}Fld:SP ';'V:2-SR:C06-MG:G2{CYH2:761}Fld:SP ';'V:2-SR:C06-MG:G4{CYM1:772}Fld:SP ';'V:2-SR:C06-MG:G4{CYM1:800}Fld:SP ';'V:2-SR:C06-MG:G6{CYL2:820}Fld:SP ';'V:2-SR:C06-MG:G6{CYL1:829}Fld:SP ';'V:2-SR:C07-MG:G2{CYL1:865}Fld:SP ';'V:2-SR:C07-MG:G2{CYL2:874}Fld:SP ';'V:2-SR:C07-MG:G4{CYM1:892}Fld:SP ';'V:2-SR:C07-MG:G4{CYM1:920}Fld:SP ';'V:2-SR:C07-MG:G6{CYH2:933}Fld:SP ';'V:2-SR:C07-MG:G6{CYH1:948}Fld:SP ';'V:2-SR:C08-MG:G2{CYH1:1004}Fld:SP';'V:2-SR:C08-MG:G2{CYH2:1019}Fld:SP';'V:2-SR:C08-MG:G4{CYM1:1030}Fld:SP';'V:2-SR:C08-MG:G4{CYM1:1058}Fld:SP';'V:2-SR:C08-MG:G6{CYL2:1078}Fld:SP';'V:2-SR:C08-MG:G6{CYL1:1087}Fld:SP';'V:2-SR:C09-MG:G2{CYL1:1123}Fld:SP';'V:2-SR:C09-MG:G2{CYL2:1132}Fld:SP';'V:2-SR:C09-MG:G4{CYM1:1150}Fld:SP';'V:2-SR:C09-MG:G4{CYM1:1178}Fld:SP';'V:2-SR:C09-MG:G6{CYH2:1191}Fld:SP';'V:2-SR:C09-MG:G6{CYH1:1206}Fld:SP';'V:2-SR:C10-MG:G2{CYH1:1251}Fld:SP';'V:2-SR:C10-MG:G2{CYH2:1266}Fld:SP';'V:2-SR:C10-MG:G4{CYM1:1277}Fld:SP';'V:2-SR:C10-MG:G4{CYM1:1305}Fld:SP';'V:2-SR:C10-MG:G6{CYL2:1325}Fld:SP';'V:2-SR:C10-MG:G6{CYL1:1334}Fld:SP';'V:2-SR:C11-MG:G2{CYL1:1383}Fld:SP';'V:2-SR:C11-MG:G2{CYL2:1392}Fld:SP';'V:2-SR:C11-MG:G4{CYM1:1410}Fld:SP';'V:2-SR:C11-MG:G4{CYM1:1438}Fld:SP';'V:2-SR:C11-MG:G6{CYH2:1451}Fld:SP';'V:2-SR:C11-MG:G6{CYH1:1466}Fld:SP';'V:2-SR:C12-MG:G2{CYH1:1498}Fld:SP';'V:2-SR:C12-MG:G2{CYH2:1513}Fld:SP';'V:2-SR:C12-MG:G4{CYM1:1524}Fld:SP';'V:2-SR:C12-MG:G4{CYM1:1552}Fld:SP';'V:2-SR:C12-MG:G6{CYL2:1572}Fld:SP';'V:2-SR:C12-MG:G6{CYL1:1581}Fld:SP';'V:2-SR:C13-MG:G2{CYL1:1617}Fld:SP';'V:2-SR:C13-MG:G2{CYL2:1626}Fld:SP';'V:2-SR:C13-MG:G4{CYM1:1644}Fld:SP';'V:2-SR:C13-MG:G4{CYM1:1672}Fld:SP';'V:2-SR:C13-MG:G6{CYH2:1685}Fld:SP';'V:2-SR:C13-MG:G6{CYH1:1700}Fld:SP';'V:2-SR:C14-MG:G2{CYH1:1732}Fld:SP';'V:2-SR:C14-MG:G2{CYH2:1747}Fld:SP';'V:2-SR:C14-MG:G4{CYM1:1758}Fld:SP';'V:2-SR:C14-MG:G4{CYM1:1786}Fld:SP';'V:2-SR:C14-MG:G6{CYL2:1806}Fld:SP';'V:2-SR:C14-MG:G6{CYL1:1815}Fld:SP';'V:2-SR:C15-MG:G2{CYL1:1851}Fld:SP';'V:2-SR:C15-MG:G2{CYL2:1860}Fld:SP';'V:2-SR:C15-MG:G4{CYM1:1878}Fld:SP';'V:2-SR:C15-MG:G4{CYM1:1906}Fld:SP';'V:2-SR:C15-MG:G6{CYH2:1919}Fld:SP';'V:2-SR:C15-MG:G6{CYH1:1934}Fld:SP';'V:2-SR:C16-MG:G2{CYH1:1966}Fld:SP';'V:2-SR:C16-MG:G2{CYH2:1981}Fld:SP';'V:2-SR:C16-MG:G4{CYM1:1992}Fld:SP';'V:2-SR:C16-MG:G4{CYM1:2020}Fld:SP';'V:2-SR:C16-MG:G6{CYL2:2040}Fld:SP';'V:2-SR:C16-MG:G6{CYL1:2049}Fld:SP';'V:2-SR:C17-MG:G2{CYL1:2085}Fld:SP';'V:2-SR:C17-MG:G2{CYL2:2094}Fld:SP';'V:2-SR:C17-MG:G4{CYM1:2112}Fld:SP';'V:2-SR:C17-MG:G4{CYM1:2140}Fld:SP';'V:2-SR:C17-MG:G6{CYH2:2153}Fld:SP';'V:2-SR:C17-MG:G6{CYH1:2168}Fld:SP';'V:2-SR:C18-MG:G2{CYH1:2224}Fld:SP';'V:2-SR:C18-MG:G2{CYH2:2239}Fld:SP';'V:2-SR:C18-MG:G4{CYM1:2250}Fld:SP';'V:2-SR:C18-MG:G4{CYM1:2278}Fld:SP';'V:2-SR:C18-MG:G6{CYL2:2298}Fld:SP';'V:2-SR:C18-MG:G6{CYL1:2307}Fld:SP';'V:2-SR:C19-MG:G2{CYL1:2343}Fld:SP';'V:2-SR:C19-MG:G2{CYL2:2352}Fld:SP';'V:2-SR:C19-MG:G4{CYM1:2370}Fld:SP';'V:2-SR:C19-MG:G4{CYM1:2398}Fld:SP';'V:2-SR:C19-MG:G6{CYH2:2411}Fld:SP';'V:2-SR:C19-MG:G6{CYH1:2426}Fld:SP';'V:2-SR:C20-MG:G2{CYH1:2458}Fld:SP';'V:2-SR:C20-MG:G2{CYH2:2473}Fld:SP';'V:2-SR:C20-MG:G4{CYM1:2484}Fld:SP';'V:2-SR:C20-MG:G4{CYM1:2512}Fld:SP';'V:2-SR:C20-MG:G6{CYL2:2532}Fld:SP';'V:2-SR:C20-MG:G6{CYL1:2541}Fld:SP';'V:2-SR:C21-MG:G2{CYL1:2577}Fld:SP';'V:2-SR:C21-MG:G2{CYL2:2586}Fld:SP';'V:2-SR:C21-MG:G4{CYM1:2604}Fld:SP';'V:2-SR:C21-MG:G4{CYM1:2632}Fld:SP';'V:2-SR:C21-MG:G6{CYH2:2645}Fld:SP';'V:2-SR:C21-MG:G6{CYH1:2660}Fld:SP';'V:2-SR:C22-MG:G2{CYH1:2692}Fld:SP';'V:2-SR:C22-MG:G2{CYH2:2707}Fld:SP';'V:2-SR:C22-MG:G4{CYM1:2718}Fld:SP';'V:2-SR:C22-MG:G4{CYM1:2746}Fld:SP';'V:2-SR:C22-MG:G6{CYL2:2766}Fld:SP';'V:2-SR:C22-MG:G6{CYL1:2775}Fld:SP';'V:2-SR:C23-MG:G2{CYL1:2831}Fld:SP';'V:2-SR:C23-MG:G2{CYL2:2840}Fld:SP';'V:2-SR:C23-MG:G4{CYM1:2858}Fld:SP';'V:2-SR:C23-MG:G4{CYM1:2886}Fld:SP';'V:2-SR:C23-MG:G6{CYH2:2899}Fld:SP';'V:2-SR:C23-MG:G6{CYH1:2914}Fld:SP';'V:2-SR:C24-MG:G2{CYH1:2946}Fld:SP';'V:2-SR:C24-MG:G2{CYH2:2961}Fld:SP';'V:2-SR:C24-MG:G4{CYM1:2972}Fld:SP';'V:2-SR:C24-MG:G4{CYM1:3000}Fld:SP';'V:2-SR:C24-MG:G6{CYL2:3020}Fld:SP';'V:2-SR:C24-MG:G6{CYL1:3029}Fld:SP';'V:2-SR:C25-MG:G2{CYL1:3065}Fld:SP';'V:2-SR:C25-MG:G2{CYL2:3074}Fld:SP';'V:2-SR:C25-MG:G4{CYM1:3092}Fld:SP';'V:2-SR:C25-MG:G4{CYM1:3120}Fld:SP';'V:2-SR:C25-MG:G6{CYH2:3133}Fld:SP';'V:2-SR:C25-MG:G6{CYH1:3148}Fld:SP';'V:2-SR:C26-MG:G2{CYH1:3180}Fld:SP';'V:2-SR:C26-MG:G2{CYH2:3195}Fld:SP';'V:2-SR:C26-MG:G4{CYM1:3206}Fld:SP';'V:2-SR:C26-MG:G4{CYM1:3234}Fld:SP';'V:2-SR:C26-MG:G6{CYL2:3254}Fld:SP';'V:2-SR:C26-MG:G6{CYL1:3263}Fld:SP';'V:2-SR:C27-MG:G2{CYL1:3299}Fld:SP';'V:2-SR:C27-MG:G2{CYL2:3308}Fld:SP';'V:2-SR:C27-MG:G4{CYM1:3326}Fld:SP';'V:2-SR:C27-MG:G4{CYM1:3354}Fld:SP';'V:2-SR:C27-MG:G6{CYH2:3367}Fld:SP';'V:2-SR:C27-MG:G6{CYH1:3382}Fld:SP';'V:2-SR:C28-MG:G2{CYH1:3438}Fld:SP';'V:2-SR:C28-MG:G2{CYH2:3453}Fld:SP';'V:2-SR:C28-MG:G4{CYM1:3464}Fld:SP';'V:2-SR:C28-MG:G4{CYM1:3492}Fld:SP';'V:2-SR:C28-MG:G6{CYL2:3512}Fld:SP';'V:2-SR:C28-MG:G6{CYL1:3521}Fld:SP';'V:2-SR:C29-MG:G2{CYL1:3557}Fld:SP';'V:2-SR:C29-MG:G2{CYL2:3566}Fld:SP';'V:2-SR:C29-MG:G4{CYM1:3584}Fld:SP';'V:2-SR:C29-MG:G4{CYM1:3612}Fld:SP';'V:2-SR:C29-MG:G6{CYH2:3625}Fld:SP';'V:2-SR:C29-MG:G6{CYH1:3640}Fld:SP' };

AO.VCM.Setpoint.HW2PhysicsFcn = @hw2at;
AO.VCM.Setpoint.Physics2HWFcn = @at2hw;
AO.VCM.Setpoint.Units        = 'Hardware';
AO.VCM.Setpoint.HWUnits      = 'Ampere';
AO.VCM.Setpoint.PhysicsUnits = 'Radian';
AO.VCM.Setpoint.Range = [-3 3];
AO.VCM.Setpoint.Tolerance  = .1;
AO.VCM.Setpoint.DeltaRespMat = 1;
%AO.VCM.Setpoint.RampRate = 1;
%AO.VCM.Setpoint.RunFlagFcn = @getrunflag_ltb;

% AO.VCM.RampRate.MemberOf = {'VCM'; 'Magnet'; 'COR'; 'PlotFamily'; 'Save/Restore';};
% AO.VCM.RampRate.Mode = 'Simulator';
% AO.VCM.RampRate.DataType = 'Scalar';
% AO.VCM.RampRate.ChannelNames = getname_ltb(AO.VCM.FamilyName, 'RampRate');
% AO.VCM.RampRate.HW2PhysicsParams = 1;
% AO.VCM.RampRate.Physics2HWParams = 1;
% AO.VCM.RampRate.Units        = 'Hardware';
% AO.VCM.RampRate.HWUnits      = 'Ampere/Second';
% AO.VCM.RampRate.PhysicsUnits = 'Ampere/Second';

AO.VCM.OnControl.MemberOf = {'VCM'; 'Magnet'; 'COR'; 'PlotFamily'; 'Boolean Control';};
AO.VCM.OnControl.Mode = 'Simulator';
AO.VCM.OnControl.DataType = 'Scalar';
AO.VCM.OnControl.ChannelNames = { 'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv' };

AO.VCM.OnControl.HW2PhysicsParams = 1;
AO.VCM.OnControl.Physics2HWParams = 1;
AO.VCM.OnControl.Units        = 'Hardware';
AO.VCM.OnControl.HWUnits      = '';
AO.VCM.OnControl.PhysicsUnits = '';
AO.VCM.OnControl.Range = [0 1];
%AO.VCM.OnControl.SpecialFunctionSet = @setsp_OnControlMagnet;

% AO.VCM.On.MemberOf = {'VCM'; 'Magnet'; 'COR'; 'PlotFamily'; 'Boolean Monitor';};
% AO.VCM.On.Mode = 'Simulator';
% AO.VCM.On.DataType = 'Scalar';
% AO.VCM.On.ChannelNames = {''}
% AO.VCM.On.HW2PhysicsParams = 1;
% AO.VCM.On.Physics2HWParams = 1;
% AO.VCM.On.Units        = 'Hardware';
% AO.VCM.On.HWUnits      = '';
% AO.VCM.On.PhysicsUnits = '';

% AO.VCM.Reset.MemberOf = {'VCM'; 'Magnet'; 'COR'; 'PlotFamily'; 'Boolean Control';};
% AO.VCM.Reset.Mode = 'Simulator';
% AO.VCM.Reset.DataType = 'Scalar';
% AO.VCM.Reset.ChannelNames = {''}
% AO.VCM.Reset.HW2PhysicsParams = 1;
% AO.VCM.Reset.Physics2HWParams = 1;
% AO.VCM.Reset.Units        = 'Hardware';
% AO.VCM.Reset.HWUnits      = '';
% AO.VCM.Reset.PhysicsUnits = '';
% AO.VCM.Reset.Range = [0 1];

AO.VCM.Fault.MemberOf = {'VCM'; 'Magnet'; 'COR'; 'PlotFamily'; 'Boolean Monitor';};
AO.VCM.Fault.Mode = 'Simulator';
AO.VCM.Fault.DataType = 'Scalar';
AO.VCM.Fault.ChannelNames = { 'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv' };

AO.VCM.Fault.HW2PhysicsParams = 1;
AO.VCM.Fault.Physics2HWParams = 1;
AO.VCM.Fault.Units        = 'Hardware';
AO.VCM.Fault.HWUnits      = 'Second';
AO.VCM.Fault.PhysicsUnits = 'Second';





% Quad

AO.QH1.FamilyName = 'QH1';
AO.QH1.MemberOf   = {'QUAD';  'Magnet';};
AO.QH1.DeviceList = [ 1 1; 1 2; 1 3; 1 4; 1 5; 1 6; 1 7; 1 8; 1 9; 1 10; 1 11; 1 12; 1 13; 1 14; 1 15; 1 16; 1 17; 1 18; 1 19; 1 20; 1 21; 1 22; 1 23; 1 24; 1 25; 1 26; 1 27; 1 28; 1 29; 1 30 ];
AO.QH1.ElementList = (1:size(AO.QH1.DeviceList,1))';
AO.QH1.Status = ones(size(AO.QH1.DeviceList,1),1);
AO.QH1.Position = [];
AO.QH1.CommonNames = [ 'qh1g2c30a';'qh1g6c01b';'qh1g2c02a';'qh1g6c03b';'qh1g2c04a';'qh1g6c05b';'qh1g2c06a';'qh1g6c07b';'qh1g2c08a';'qh1g6c09b';'qh1g2c10a';'qh1g6c11b';'qh1g2c12a';'qh1g6c13b';'qh1g2c14a';'qh1g6c15b';'qh1g2c16a';'qh1g6c17b';'qh1g2c18a';'qh1g6c19b';'qh1g2c20a';'qh1g6c21b';'qh1g2c22a';'qh1g6c23b';'qh1g2c24a';'qh1g6c25b';'qh1g2c26a';'qh1g6c27b';'qh1g2c28a';'qh1g6c29b' ];

AO.QH1.Monitor.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Monitor'; 'Save';};
AO.QH1.Monitor.Mode = 'Simulator';
AO.QH1.Monitor.DataType = 'Scalar';
AO.QH1.Monitor.ChannelNames = { 'V:2-SR:C30-MG:G2{QH1:13}Fld:I';'V:2-SR:C01-MG:G6{QH1:222}Fld:I';'V:2-SR:C02-MG:G2{QH1:247}Fld:I';'V:2-SR:C03-MG:G6{QH1:469}Fld:I';'V:2-SR:C04-MG:G2{QH1:494}Fld:I';'V:2-SR:C05-MG:G6{QH1:717}Fld:I';'V:2-SR:C06-MG:G2{QH1:742}Fld:I';'V:2-SR:C07-MG:G6{QH1:951}Fld:I';'V:2-SR:C08-MG:G2{QH1:1000}Fld:I';'V:2-SR:C09-MG:G6{QH1:1209}Fld:I';'V:2-SR:C10-MG:G2{QH1:1247}Fld:I';'V:2-SR:C11-MG:G6{QH1:1469}Fld:I';'V:2-SR:C12-MG:G2{QH1:1494}Fld:I';'V:2-SR:C13-MG:G6{QH1:1703}Fld:I';'V:2-SR:C14-MG:G2{QH1:1728}Fld:I';'V:2-SR:C15-MG:G6{QH1:1937}Fld:I';'V:2-SR:C16-MG:G2{QH1:1962}Fld:I';'V:2-SR:C17-MG:G6{QH1:2171}Fld:I';'V:2-SR:C18-MG:G2{QH1:2220}Fld:I';'V:2-SR:C19-MG:G6{QH1:2429}Fld:I';'V:2-SR:C20-MG:G2{QH1:2454}Fld:I';'V:2-SR:C21-MG:G6{QH1:2663}Fld:I';'V:2-SR:C22-MG:G2{QH1:2688}Fld:I';'V:2-SR:C23-MG:G6{QH1:2917}Fld:I';'V:2-SR:C24-MG:G2{QH1:2942}Fld:I';'V:2-SR:C25-MG:G6{QH1:3151}Fld:I';'V:2-SR:C26-MG:G2{QH1:3176}Fld:I';'V:2-SR:C27-MG:G6{QH1:3385}Fld:I';'V:2-SR:C28-MG:G2{QH1:3434}Fld:I';'V:2-SR:C29-MG:G6{QH1:3643}Fld:I' };

AO.QH1.Monitor.HW2PhysicsFcn = @hw2at;
AO.QH1.Monitor.Physics2HWFcn = @at2hw;
AO.QH1.Monitor.Units        = 'Hardware';
AO.QH1.Monitor.HWUnits      = 'Ampere';
AO.QH1.Monitor.PhysicsUnits = '1/Meter^2';
%AO.QH1.Monitor.Real2RawFcn = @real2raw_ltb;
%AO.QH1.Monitor.Raw2RealFcn = @raw2real_ltb;

AO.QH1.Setpoint.MemberOf = {'QUAD'; 'Magnet'; 'Save/Restore'; 'Setpoint';};
AO.QH1.Setpoint.Mode = 'Simulator';
AO.QH1.Setpoint.DataType = 'Scalar';
AO.QH1.Setpoint.ChannelNames = { 'V:2-SR:C30-MG:G2{QH1:13}Fld:SP';'V:2-SR:C01-MG:G6{QH1:222}Fld:SP';'V:2-SR:C02-MG:G2{QH1:247}Fld:SP';'V:2-SR:C03-MG:G6{QH1:469}Fld:SP';'V:2-SR:C04-MG:G2{QH1:494}Fld:SP';'V:2-SR:C05-MG:G6{QH1:717}Fld:SP';'V:2-SR:C06-MG:G2{QH1:742}Fld:SP';'V:2-SR:C07-MG:G6{QH1:951}Fld:SP';'V:2-SR:C08-MG:G2{QH1:1000}Fld:SP';'V:2-SR:C09-MG:G6{QH1:1209}Fld:SP';'V:2-SR:C10-MG:G2{QH1:1247}Fld:SP';'V:2-SR:C11-MG:G6{QH1:1469}Fld:SP';'V:2-SR:C12-MG:G2{QH1:1494}Fld:SP';'V:2-SR:C13-MG:G6{QH1:1703}Fld:SP';'V:2-SR:C14-MG:G2{QH1:1728}Fld:SP';'V:2-SR:C15-MG:G6{QH1:1937}Fld:SP';'V:2-SR:C16-MG:G2{QH1:1962}Fld:SP';'V:2-SR:C17-MG:G6{QH1:2171}Fld:SP';'V:2-SR:C18-MG:G2{QH1:2220}Fld:SP';'V:2-SR:C19-MG:G6{QH1:2429}Fld:SP';'V:2-SR:C20-MG:G2{QH1:2454}Fld:SP';'V:2-SR:C21-MG:G6{QH1:2663}Fld:SP';'V:2-SR:C22-MG:G2{QH1:2688}Fld:SP';'V:2-SR:C23-MG:G6{QH1:2917}Fld:SP';'V:2-SR:C24-MG:G2{QH1:2942}Fld:SP';'V:2-SR:C25-MG:G6{QH1:3151}Fld:SP';'V:2-SR:C26-MG:G2{QH1:3176}Fld:SP';'V:2-SR:C27-MG:G6{QH1:3385}Fld:SP';'V:2-SR:C28-MG:G2{QH1:3434}Fld:SP';'V:2-SR:C29-MG:G6{QH1:3643}Fld:SP' };

AO.QH1.Setpoint.HW2PhysicsFcn = @hw2at;
AO.QH1.Setpoint.Physics2HWFcn = @at2hw;
AO.QH1.Setpoint.Units        = 'Hardware';
AO.QH1.Setpoint.HWUnits      = 'Ampere';
AO.QH1.Setpoint.PhysicsUnits = '1/Meter^2';
AO.QH1.Setpoint.Range = [0 160];
AO.QH1.Setpoint.Tolerance = .1;
AO.QH1.Setpoint.DeltaRespMat = 1;
%AO.QH1.Setpoint.RampRate = .15;
%AO.QH1.Setpoint.RunFlagFcn = @getrunflag_ltb;

% AO.QH1.RampRate.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Save/Restore';};
% AO.QH1.RampRate.Mode = 'Simulator';
% AO.QH1.RampRate.DataType = 'Scalar';
% AO.QH1.RampRate.ChannelNames = getname_ltb('Q', 'RampRate');
% AO.QH1.RampRate.HW2PhysicsFcn = @hw2at;
% AO.QH1.RampRate.Physics2HWFcn = @at2hw;
% AO.QH1.RampRate.Units        = 'Hardware';
% AO.QH1.RampRate.HWUnits      = 'Ampere/Second';
% AO.QH1.RampRate.PhysicsUnits = 'Ampere/Second';
%(what_is1)s

AO.QH1.OnControl.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Control';};
AO.QH1.OnControl.Mode = 'Simulator';
AO.QH1.OnControl.DataType = 'Scalar';
AO.QH1.OnControl.ChannelNames = { 'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv' };

AO.QH1.OnControl.HW2PhysicsParams = 1;
AO.QH1.OnControl.Physics2HWParams = 1;
AO.QH1.OnControl.Units        = 'Hardware';
AO.QH1.OnControl.HWUnits      = '';
AO.QH1.OnControl.PhysicsUnits = '';
AO.QH1.OnControl.Range = [0 1];

% AO.QH1.On.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Monitor';};
% AO.QH1.On.Mode = 'Simulator';
% AO.QH1.On.DataType = 'Scalar';
% AO.QH1.On.ChannelNames = {''};
% AO.QH1.On.HW2PhysicsParams = 1;
% AO.QH1.On.Physics2HWParams = 1;
% AO.QH1.On.Units        = 'Hardware';
% AO.QH1.On.HWUnits      = '';
% AO.QH1.On.PhysicsUnits = '';

% AO.QH1.Reset.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Control';};
% AO.QH1.Reset.Mode = 'Simulator';
% AO.QH1.Reset.DataType = 'Scalar';
% AO.QH1.Reset.ChannelNames = {''};
% AO.QH1.Reset.HW2PhysicsParams = 1;
% AO.QH1.Reset.Physics2HWParams = 1;
% AO.QH1.Reset.Units        = 'Hardware';
% AO.QH1.Reset.HWUnits      = '';
% AO.QH1.Reset.PhysicsUnits = '';
% AO.QH1.Reset.Range = [0 1];

AO.QH1.Fault.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Monitor';};
AO.QH1.Fault.Mode = 'Simulator';
AO.QH1.Fault.DataType = 'Scalar';
AO.QH1.Fault.ChannelNames = { 'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv' };

AO.QH1.Fault.HW2PhysicsParams = 1;
AO.QH1.Fault.Physics2HWParams = 1;
AO.QH1.Fault.Units        = 'Hardware';
AO.QH1.Fault.HWUnits      = '';
AO.QH1.Fault.PhysicsUnits = '';

AO.QH2.FamilyName = 'QH2';
AO.QH2.MemberOf   = {'QUAD';  'Magnet';};
AO.QH2.DeviceList = [ 1 1; 1 2; 1 3; 1 4; 1 5; 1 6; 1 7; 1 8; 1 9; 1 10; 1 11; 1 12; 1 13; 1 14; 1 15; 1 16; 1 17; 1 18; 1 19; 1 20; 1 21; 1 22; 1 23; 1 24; 1 25; 1 26; 1 27; 1 28; 1 29; 1 30 ];
AO.QH2.ElementList = (1:size(AO.QH2.DeviceList,1))';
AO.QH2.Status = ones(size(AO.QH2.DeviceList,1),1);
AO.QH2.Position = [];
AO.QH2.CommonNames = [ 'qh2g2c30a';'qh2g6c01b';'qh2g2c02a';'qh2g6c03b';'qh2g2c04a';'qh2g6c05b';'qh2g2c06a';'qh2g6c07b';'qh2g2c08a';'qh2g6c09b';'qh2g2c10a';'qh2g6c11b';'qh2g2c12a';'qh2g6c13b';'qh2g2c14a';'qh2g6c15b';'qh2g2c16a';'qh2g6c17b';'qh2g2c18a';'qh2g6c19b';'qh2g2c20a';'qh2g6c21b';'qh2g2c22a';'qh2g6c23b';'qh2g2c24a';'qh2g6c25b';'qh2g2c26a';'qh2g6c27b';'qh2g2c28a';'qh2g6c29b' ];

AO.QH2.Monitor.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Monitor'; 'Save';};
AO.QH2.Monitor.Mode = 'Simulator';
AO.QH2.Monitor.DataType = 'Scalar';
AO.QH2.Monitor.ChannelNames = { 'V:2-SR:C30-MG:G2{QH2:20}Fld:I';'V:2-SR:C01-MG:G6{QH2:215}Fld:I';'V:2-SR:C02-MG:G2{QH2:254}Fld:I';'V:2-SR:C03-MG:G6{QH2:462}Fld:I';'V:2-SR:C04-MG:G2{QH2:501}Fld:I';'V:2-SR:C05-MG:G6{QH2:710}Fld:I';'V:2-SR:C06-MG:G2{QH2:749}Fld:I';'V:2-SR:C07-MG:G6{QH2:944}Fld:I';'V:2-SR:C08-MG:G2{QH2:1007}Fld:I';'V:2-SR:C09-MG:G6{QH2:1202}Fld:I';'V:2-SR:C10-MG:G2{QH2:1254}Fld:I';'V:2-SR:C11-MG:G6{QH2:1462}Fld:I';'V:2-SR:C12-MG:G2{QH2:1501}Fld:I';'V:2-SR:C13-MG:G6{QH2:1696}Fld:I';'V:2-SR:C14-MG:G2{QH2:1735}Fld:I';'V:2-SR:C15-MG:G6{QH2:1930}Fld:I';'V:2-SR:C16-MG:G2{QH2:1969}Fld:I';'V:2-SR:C17-MG:G6{QH2:2164}Fld:I';'V:2-SR:C18-MG:G2{QH2:2227}Fld:I';'V:2-SR:C19-MG:G6{QH2:2422}Fld:I';'V:2-SR:C20-MG:G2{QH2:2461}Fld:I';'V:2-SR:C21-MG:G6{QH2:2656}Fld:I';'V:2-SR:C22-MG:G2{QH2:2695}Fld:I';'V:2-SR:C23-MG:G6{QH2:2910}Fld:I';'V:2-SR:C24-MG:G2{QH2:2949}Fld:I';'V:2-SR:C25-MG:G6{QH2:3144}Fld:I';'V:2-SR:C26-MG:G2{QH2:3183}Fld:I';'V:2-SR:C27-MG:G6{QH2:3378}Fld:I';'V:2-SR:C28-MG:G2{QH2:3441}Fld:I';'V:2-SR:C29-MG:G6{QH2:3636}Fld:I' };

AO.QH2.Monitor.HW2PhysicsFcn = @hw2at;
AO.QH2.Monitor.Physics2HWFcn = @at2hw;
AO.QH2.Monitor.Units        = 'Hardware';
AO.QH2.Monitor.HWUnits      = 'Ampere';
AO.QH2.Monitor.PhysicsUnits = '1/Meter^2';
%AO.QH2.Monitor.Real2RawFcn = @real2raw_ltb;
%AO.QH2.Monitor.Raw2RealFcn = @raw2real_ltb;

AO.QH2.Setpoint.MemberOf = {'QUAD'; 'Magnet'; 'Save/Restore'; 'Setpoint';};
AO.QH2.Setpoint.Mode = 'Simulator';
AO.QH2.Setpoint.DataType = 'Scalar';
AO.QH2.Setpoint.ChannelNames = { 'V:2-SR:C30-MG:G2{QH2:20}Fld:SP';'V:2-SR:C01-MG:G6{QH2:215}Fld:SP';'V:2-SR:C02-MG:G2{QH2:254}Fld:SP';'V:2-SR:C03-MG:G6{QH2:462}Fld:SP';'V:2-SR:C04-MG:G2{QH2:501}Fld:SP';'V:2-SR:C05-MG:G6{QH2:710}Fld:SP';'V:2-SR:C06-MG:G2{QH2:749}Fld:SP';'V:2-SR:C07-MG:G6{QH2:944}Fld:SP';'V:2-SR:C08-MG:G2{QH2:1007}Fld:SP';'V:2-SR:C09-MG:G6{QH2:1202}Fld:SP';'V:2-SR:C10-MG:G2{QH2:1254}Fld:SP';'V:2-SR:C11-MG:G6{QH2:1462}Fld:SP';'V:2-SR:C12-MG:G2{QH2:1501}Fld:SP';'V:2-SR:C13-MG:G6{QH2:1696}Fld:SP';'V:2-SR:C14-MG:G2{QH2:1735}Fld:SP';'V:2-SR:C15-MG:G6{QH2:1930}Fld:SP';'V:2-SR:C16-MG:G2{QH2:1969}Fld:SP';'V:2-SR:C17-MG:G6{QH2:2164}Fld:SP';'V:2-SR:C18-MG:G2{QH2:2227}Fld:SP';'V:2-SR:C19-MG:G6{QH2:2422}Fld:SP';'V:2-SR:C20-MG:G2{QH2:2461}Fld:SP';'V:2-SR:C21-MG:G6{QH2:2656}Fld:SP';'V:2-SR:C22-MG:G2{QH2:2695}Fld:SP';'V:2-SR:C23-MG:G6{QH2:2910}Fld:SP';'V:2-SR:C24-MG:G2{QH2:2949}Fld:SP';'V:2-SR:C25-MG:G6{QH2:3144}Fld:SP';'V:2-SR:C26-MG:G2{QH2:3183}Fld:SP';'V:2-SR:C27-MG:G6{QH2:3378}Fld:SP';'V:2-SR:C28-MG:G2{QH2:3441}Fld:SP';'V:2-SR:C29-MG:G6{QH2:3636}Fld:SP' };

AO.QH2.Setpoint.HW2PhysicsFcn = @hw2at;
AO.QH2.Setpoint.Physics2HWFcn = @at2hw;
AO.QH2.Setpoint.Units        = 'Hardware';
AO.QH2.Setpoint.HWUnits      = 'Ampere';
AO.QH2.Setpoint.PhysicsUnits = '1/Meter^2';
AO.QH2.Setpoint.Range = [0 160];
AO.QH2.Setpoint.Tolerance = .1;
AO.QH2.Setpoint.DeltaRespMat = 1;
%AO.QH2.Setpoint.RampRate = .15;
%AO.QH2.Setpoint.RunFlagFcn = @getrunflag_ltb;

% AO.QH2.RampRate.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Save/Restore';};
% AO.QH2.RampRate.Mode = 'Simulator';
% AO.QH2.RampRate.DataType = 'Scalar';
% AO.QH2.RampRate.ChannelNames = getname_ltb('Q', 'RampRate');
% AO.QH2.RampRate.HW2PhysicsFcn = @hw2at;
% AO.QH2.RampRate.Physics2HWFcn = @at2hw;
% AO.QH2.RampRate.Units        = 'Hardware';
% AO.QH2.RampRate.HWUnits      = 'Ampere/Second';
% AO.QH2.RampRate.PhysicsUnits = 'Ampere/Second';
%(what_is1)s

AO.QH2.OnControl.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Control';};
AO.QH2.OnControl.Mode = 'Simulator';
AO.QH2.OnControl.DataType = 'Scalar';
AO.QH2.OnControl.ChannelNames = { 'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv' };

AO.QH2.OnControl.HW2PhysicsParams = 1;
AO.QH2.OnControl.Physics2HWParams = 1;
AO.QH2.OnControl.Units        = 'Hardware';
AO.QH2.OnControl.HWUnits      = '';
AO.QH2.OnControl.PhysicsUnits = '';
AO.QH2.OnControl.Range = [0 1];

% AO.QH2.On.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Monitor';};
% AO.QH2.On.Mode = 'Simulator';
% AO.QH2.On.DataType = 'Scalar';
% AO.QH2.On.ChannelNames = {''};
% AO.QH2.On.HW2PhysicsParams = 1;
% AO.QH2.On.Physics2HWParams = 1;
% AO.QH2.On.Units        = 'Hardware';
% AO.QH2.On.HWUnits      = '';
% AO.QH2.On.PhysicsUnits = '';

% AO.QH2.Reset.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Control';};
% AO.QH2.Reset.Mode = 'Simulator';
% AO.QH2.Reset.DataType = 'Scalar';
% AO.QH2.Reset.ChannelNames = {''};
% AO.QH2.Reset.HW2PhysicsParams = 1;
% AO.QH2.Reset.Physics2HWParams = 1;
% AO.QH2.Reset.Units        = 'Hardware';
% AO.QH2.Reset.HWUnits      = '';
% AO.QH2.Reset.PhysicsUnits = '';
% AO.QH2.Reset.Range = [0 1];

AO.QH2.Fault.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Monitor';};
AO.QH2.Fault.Mode = 'Simulator';
AO.QH2.Fault.DataType = 'Scalar';
AO.QH2.Fault.ChannelNames = { 'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv' };

AO.QH2.Fault.HW2PhysicsParams = 1;
AO.QH2.Fault.Physics2HWParams = 1;
AO.QH2.Fault.Units        = 'Hardware';
AO.QH2.Fault.HWUnits      = '';
AO.QH2.Fault.PhysicsUnits = '';

AO.QH3.FamilyName = 'QH3';
AO.QH3.MemberOf   = {'QUAD';  'Magnet';};
AO.QH3.DeviceList = [ 1 1; 1 2; 1 3; 1 4; 1 5; 1 6; 1 7; 1 8; 1 9; 1 10; 1 11; 1 12; 1 13; 1 14; 1 15; 1 16; 1 17; 1 18; 1 19; 1 20; 1 21; 1 22; 1 23; 1 24; 1 25; 1 26; 1 27; 1 28; 1 29; 1 30 ];
AO.QH3.ElementList = (1:size(AO.QH3.DeviceList,1))';
AO.QH3.Status = ones(size(AO.QH3.DeviceList,1),1);
AO.QH3.Position = [];
AO.QH3.CommonNames = [ 'qh3g2c30a';'qh3g6c01b';'qh3g2c02a';'qh3g6c03b';'qh3g2c04a';'qh3g6c05b';'qh3g2c06a';'qh3g6c07b';'qh3g2c08a';'qh3g6c09b';'qh3g2c10a';'qh3g6c11b';'qh3g2c12a';'qh3g6c13b';'qh3g2c14a';'qh3g6c15b';'qh3g2c16a';'qh3g6c17b';'qh3g2c18a';'qh3g6c19b';'qh3g2c20a';'qh3g6c21b';'qh3g2c22a';'qh3g6c23b';'qh3g2c24a';'qh3g6c25b';'qh3g2c26a';'qh3g6c27b';'qh3g2c28a';'qh3g6c29b' ];

AO.QH3.Monitor.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Monitor'; 'Save';};
AO.QH3.Monitor.Mode = 'Simulator';
AO.QH3.Monitor.DataType = 'Scalar';
AO.QH3.Monitor.ChannelNames = { 'V:2-SR:C30-MG:G2{QH3:24}Fld:I';'V:2-SR:C01-MG:G6{QH3:211}Fld:I';'V:2-SR:C02-MG:G2{QH3:258}Fld:I';'V:2-SR:C03-MG:G6{QH3:458}Fld:I';'V:2-SR:C04-MG:G2{QH3:505}Fld:I';'V:2-SR:C05-MG:G6{QH3:706}Fld:I';'V:2-SR:C06-MG:G2{QH3:753}Fld:I';'V:2-SR:C07-MG:G6{QH3:940}Fld:I';'V:2-SR:C08-MG:G2{QH3:1011}Fld:I';'V:2-SR:C09-MG:G6{QH3:1198}Fld:I';'V:2-SR:C10-MG:G2{QH3:1258}Fld:I';'V:2-SR:C11-MG:G6{QH3:1458}Fld:I';'V:2-SR:C12-MG:G2{QH3:1505}Fld:I';'V:2-SR:C13-MG:G6{QH3:1692}Fld:I';'V:2-SR:C14-MG:G2{QH3:1739}Fld:I';'V:2-SR:C15-MG:G6{QH3:1926}Fld:I';'V:2-SR:C16-MG:G2{QH3:1973}Fld:I';'V:2-SR:C17-MG:G6{QH3:2160}Fld:I';'V:2-SR:C18-MG:G2{QH3:2231}Fld:I';'V:2-SR:C19-MG:G6{QH3:2418}Fld:I';'V:2-SR:C20-MG:G2{QH3:2465}Fld:I';'V:2-SR:C21-MG:G6{QH3:2652}Fld:I';'V:2-SR:C22-MG:G2{QH3:2699}Fld:I';'V:2-SR:C23-MG:G6{QH3:2906}Fld:I';'V:2-SR:C24-MG:G2{QH3:2953}Fld:I';'V:2-SR:C25-MG:G6{QH3:3140}Fld:I';'V:2-SR:C26-MG:G2{QH3:3187}Fld:I';'V:2-SR:C27-MG:G6{QH3:3374}Fld:I';'V:2-SR:C28-MG:G2{QH3:3445}Fld:I';'V:2-SR:C29-MG:G6{QH3:3632}Fld:I' };

AO.QH3.Monitor.HW2PhysicsFcn = @hw2at;
AO.QH3.Monitor.Physics2HWFcn = @at2hw;
AO.QH3.Monitor.Units        = 'Hardware';
AO.QH3.Monitor.HWUnits      = 'Ampere';
AO.QH3.Monitor.PhysicsUnits = '1/Meter^2';
%AO.QH3.Monitor.Real2RawFcn = @real2raw_ltb;
%AO.QH3.Monitor.Raw2RealFcn = @raw2real_ltb;

AO.QH3.Setpoint.MemberOf = {'QUAD'; 'Magnet'; 'Save/Restore'; 'Setpoint';};
AO.QH3.Setpoint.Mode = 'Simulator';
AO.QH3.Setpoint.DataType = 'Scalar';
AO.QH3.Setpoint.ChannelNames = { 'V:2-SR:C30-MG:G2{QH3:24}Fld:SP';'V:2-SR:C01-MG:G6{QH3:211}Fld:SP';'V:2-SR:C02-MG:G2{QH3:258}Fld:SP';'V:2-SR:C03-MG:G6{QH3:458}Fld:SP';'V:2-SR:C04-MG:G2{QH3:505}Fld:SP';'V:2-SR:C05-MG:G6{QH3:706}Fld:SP';'V:2-SR:C06-MG:G2{QH3:753}Fld:SP';'V:2-SR:C07-MG:G6{QH3:940}Fld:SP';'V:2-SR:C08-MG:G2{QH3:1011}Fld:SP';'V:2-SR:C09-MG:G6{QH3:1198}Fld:SP';'V:2-SR:C10-MG:G2{QH3:1258}Fld:SP';'V:2-SR:C11-MG:G6{QH3:1458}Fld:SP';'V:2-SR:C12-MG:G2{QH3:1505}Fld:SP';'V:2-SR:C13-MG:G6{QH3:1692}Fld:SP';'V:2-SR:C14-MG:G2{QH3:1739}Fld:SP';'V:2-SR:C15-MG:G6{QH3:1926}Fld:SP';'V:2-SR:C16-MG:G2{QH3:1973}Fld:SP';'V:2-SR:C17-MG:G6{QH3:2160}Fld:SP';'V:2-SR:C18-MG:G2{QH3:2231}Fld:SP';'V:2-SR:C19-MG:G6{QH3:2418}Fld:SP';'V:2-SR:C20-MG:G2{QH3:2465}Fld:SP';'V:2-SR:C21-MG:G6{QH3:2652}Fld:SP';'V:2-SR:C22-MG:G2{QH3:2699}Fld:SP';'V:2-SR:C23-MG:G6{QH3:2906}Fld:SP';'V:2-SR:C24-MG:G2{QH3:2953}Fld:SP';'V:2-SR:C25-MG:G6{QH3:3140}Fld:SP';'V:2-SR:C26-MG:G2{QH3:3187}Fld:SP';'V:2-SR:C27-MG:G6{QH3:3374}Fld:SP';'V:2-SR:C28-MG:G2{QH3:3445}Fld:SP';'V:2-SR:C29-MG:G6{QH3:3632}Fld:SP' };

AO.QH3.Setpoint.HW2PhysicsFcn = @hw2at;
AO.QH3.Setpoint.Physics2HWFcn = @at2hw;
AO.QH3.Setpoint.Units        = 'Hardware';
AO.QH3.Setpoint.HWUnits      = 'Ampere';
AO.QH3.Setpoint.PhysicsUnits = '1/Meter^2';
AO.QH3.Setpoint.Range = [0 160];
AO.QH3.Setpoint.Tolerance = .1;
AO.QH3.Setpoint.DeltaRespMat = 1;
%AO.QH3.Setpoint.RampRate = .15;
%AO.QH3.Setpoint.RunFlagFcn = @getrunflag_ltb;

% AO.QH3.RampRate.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Save/Restore';};
% AO.QH3.RampRate.Mode = 'Simulator';
% AO.QH3.RampRate.DataType = 'Scalar';
% AO.QH3.RampRate.ChannelNames = getname_ltb('Q', 'RampRate');
% AO.QH3.RampRate.HW2PhysicsFcn = @hw2at;
% AO.QH3.RampRate.Physics2HWFcn = @at2hw;
% AO.QH3.RampRate.Units        = 'Hardware';
% AO.QH3.RampRate.HWUnits      = 'Ampere/Second';
% AO.QH3.RampRate.PhysicsUnits = 'Ampere/Second';
%(what_is1)s

AO.QH3.OnControl.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Control';};
AO.QH3.OnControl.Mode = 'Simulator';
AO.QH3.OnControl.DataType = 'Scalar';
AO.QH3.OnControl.ChannelNames = { 'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv' };

AO.QH3.OnControl.HW2PhysicsParams = 1;
AO.QH3.OnControl.Physics2HWParams = 1;
AO.QH3.OnControl.Units        = 'Hardware';
AO.QH3.OnControl.HWUnits      = '';
AO.QH3.OnControl.PhysicsUnits = '';
AO.QH3.OnControl.Range = [0 1];

% AO.QH3.On.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Monitor';};
% AO.QH3.On.Mode = 'Simulator';
% AO.QH3.On.DataType = 'Scalar';
% AO.QH3.On.ChannelNames = {''};
% AO.QH3.On.HW2PhysicsParams = 1;
% AO.QH3.On.Physics2HWParams = 1;
% AO.QH3.On.Units        = 'Hardware';
% AO.QH3.On.HWUnits      = '';
% AO.QH3.On.PhysicsUnits = '';

% AO.QH3.Reset.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Control';};
% AO.QH3.Reset.Mode = 'Simulator';
% AO.QH3.Reset.DataType = 'Scalar';
% AO.QH3.Reset.ChannelNames = {''};
% AO.QH3.Reset.HW2PhysicsParams = 1;
% AO.QH3.Reset.Physics2HWParams = 1;
% AO.QH3.Reset.Units        = 'Hardware';
% AO.QH3.Reset.HWUnits      = '';
% AO.QH3.Reset.PhysicsUnits = '';
% AO.QH3.Reset.Range = [0 1];

AO.QH3.Fault.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Monitor';};
AO.QH3.Fault.Mode = 'Simulator';
AO.QH3.Fault.DataType = 'Scalar';
AO.QH3.Fault.ChannelNames = { 'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv' };

AO.QH3.Fault.HW2PhysicsParams = 1;
AO.QH3.Fault.Physics2HWParams = 1;
AO.QH3.Fault.Units        = 'Hardware';
AO.QH3.Fault.HWUnits      = '';
AO.QH3.Fault.PhysicsUnits = '';

AO.QL1.FamilyName = 'QL1';
AO.QL1.MemberOf   = {'QUAD';  'Magnet';};
AO.QL1.DeviceList = [ 1 1; 1 2; 1 3; 1 4; 1 5; 1 6; 1 7; 1 8; 1 9; 1 10; 1 11; 1 12; 1 13; 1 14; 1 15; 1 16; 1 17; 1 18; 1 19; 1 20; 1 21; 1 22; 1 23; 1 24; 1 25; 1 26; 1 27; 1 28; 1 29; 1 30 ];
AO.QL1.ElementList = (1:size(AO.QL1.DeviceList,1))';
AO.QL1.Status = ones(size(AO.QL1.DeviceList,1),1);
AO.QL1.Position = [];
AO.QL1.CommonNames = [ 'ql1g6c30b';'ql1g2c01a';'ql1g6c02b';'ql1g2c03a';'ql1g6c04b';'ql1g2c05a';'ql1g6c06b';'ql1g2c07a';'ql1g6c08b';'ql1g2c09a';'ql1g6c10b';'ql1g2c11a';'ql1g6c12b';'ql1g2c13a';'ql1g6c14b';'ql1g2c15a';'ql1g6c16b';'ql1g2c17a';'ql1g6c18b';'ql1g2c19a';'ql1g6c20b';'ql1g2c21a';'ql1g6c22b';'ql1g2c23a';'ql1g6c24b';'ql1g2c25a';'ql1g6c26b';'ql1g2c27a';'ql1g6c28b';'ql1g2c29a' ];

AO.QL1.Monitor.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Monitor'; 'Save';};
AO.QL1.Monitor.Mode = 'Simulator';
AO.QL1.Monitor.DataType = 'Scalar';
AO.QL1.Monitor.ChannelNames = { 'V:2-SR:C30-MG:G6{QL1:103}Fld:I';'V:2-SR:C01-MG:G2{QL1:132}Fld:I';'V:2-SR:C02-MG:G6{QL1:337}Fld:I';'V:2-SR:C03-MG:G2{QL1:379}Fld:I';'V:2-SR:C04-MG:G6{QL1:584}Fld:I';'V:2-SR:C05-MG:G2{QL1:627}Fld:I';'V:2-SR:C06-MG:G6{QL1:832}Fld:I';'V:2-SR:C07-MG:G2{QL1:861}Fld:I';'V:2-SR:C08-MG:G6{QL1:1090}Fld:I';'V:2-SR:C09-MG:G2{QL1:1119}Fld:I';'V:2-SR:C10-MG:G6{QL1:1337}Fld:I';'V:2-SR:C11-MG:G2{QL1:1379}Fld:I';'V:2-SR:C12-MG:G6{QL1:1584}Fld:I';'V:2-SR:C13-MG:G2{QL1:1613}Fld:I';'V:2-SR:C14-MG:G6{QL1:1818}Fld:I';'V:2-SR:C15-MG:G2{QL1:1847}Fld:I';'V:2-SR:C16-MG:G6{QL1:2052}Fld:I';'V:2-SR:C17-MG:G2{QL1:2081}Fld:I';'V:2-SR:C18-MG:G6{QL1:2310}Fld:I';'V:2-SR:C19-MG:G2{QL1:2339}Fld:I';'V:2-SR:C20-MG:G6{QL1:2544}Fld:I';'V:2-SR:C21-MG:G2{QL1:2573}Fld:I';'V:2-SR:C22-MG:G6{QL1:2778}Fld:I';'V:2-SR:C23-MG:G2{QL1:2827}Fld:I';'V:2-SR:C24-MG:G6{QL1:3032}Fld:I';'V:2-SR:C25-MG:G2{QL1:3061}Fld:I';'V:2-SR:C26-MG:G6{QL1:3266}Fld:I';'V:2-SR:C27-MG:G2{QL1:3295}Fld:I';'V:2-SR:C28-MG:G6{QL1:3524}Fld:I';'V:2-SR:C29-MG:G2{QL1:3553}Fld:I' };

AO.QL1.Monitor.HW2PhysicsFcn = @hw2at;
AO.QL1.Monitor.Physics2HWFcn = @at2hw;
AO.QL1.Monitor.Units        = 'Hardware';
AO.QL1.Monitor.HWUnits      = 'Ampere';
AO.QL1.Monitor.PhysicsUnits = '1/Meter^2';
%AO.QL1.Monitor.Real2RawFcn = @real2raw_ltb;
%AO.QL1.Monitor.Raw2RealFcn = @raw2real_ltb;

AO.QL1.Setpoint.MemberOf = {'QUAD'; 'Magnet'; 'Save/Restore'; 'Setpoint';};
AO.QL1.Setpoint.Mode = 'Simulator';
AO.QL1.Setpoint.DataType = 'Scalar';
AO.QL1.Setpoint.ChannelNames = { 'V:2-SR:C30-MG:G6{QL1:103}Fld:SP';'V:2-SR:C01-MG:G2{QL1:132}Fld:SP';'V:2-SR:C02-MG:G6{QL1:337}Fld:SP';'V:2-SR:C03-MG:G2{QL1:379}Fld:SP';'V:2-SR:C04-MG:G6{QL1:584}Fld:SP';'V:2-SR:C05-MG:G2{QL1:627}Fld:SP';'V:2-SR:C06-MG:G6{QL1:832}Fld:SP';'V:2-SR:C07-MG:G2{QL1:861}Fld:SP';'V:2-SR:C08-MG:G6{QL1:1090}Fld:SP';'V:2-SR:C09-MG:G2{QL1:1119}Fld:SP';'V:2-SR:C10-MG:G6{QL1:1337}Fld:SP';'V:2-SR:C11-MG:G2{QL1:1379}Fld:SP';'V:2-SR:C12-MG:G6{QL1:1584}Fld:SP';'V:2-SR:C13-MG:G2{QL1:1613}Fld:SP';'V:2-SR:C14-MG:G6{QL1:1818}Fld:SP';'V:2-SR:C15-MG:G2{QL1:1847}Fld:SP';'V:2-SR:C16-MG:G6{QL1:2052}Fld:SP';'V:2-SR:C17-MG:G2{QL1:2081}Fld:SP';'V:2-SR:C18-MG:G6{QL1:2310}Fld:SP';'V:2-SR:C19-MG:G2{QL1:2339}Fld:SP';'V:2-SR:C20-MG:G6{QL1:2544}Fld:SP';'V:2-SR:C21-MG:G2{QL1:2573}Fld:SP';'V:2-SR:C22-MG:G6{QL1:2778}Fld:SP';'V:2-SR:C23-MG:G2{QL1:2827}Fld:SP';'V:2-SR:C24-MG:G6{QL1:3032}Fld:SP';'V:2-SR:C25-MG:G2{QL1:3061}Fld:SP';'V:2-SR:C26-MG:G6{QL1:3266}Fld:SP';'V:2-SR:C27-MG:G2{QL1:3295}Fld:SP';'V:2-SR:C28-MG:G6{QL1:3524}Fld:SP';'V:2-SR:C29-MG:G2{QL1:3553}Fld:SP' };

AO.QL1.Setpoint.HW2PhysicsFcn = @hw2at;
AO.QL1.Setpoint.Physics2HWFcn = @at2hw;
AO.QL1.Setpoint.Units        = 'Hardware';
AO.QL1.Setpoint.HWUnits      = 'Ampere';
AO.QL1.Setpoint.PhysicsUnits = '1/Meter^2';
AO.QL1.Setpoint.Range = [0 160];
AO.QL1.Setpoint.Tolerance = .1;
AO.QL1.Setpoint.DeltaRespMat = 1;
%AO.QL1.Setpoint.RampRate = .15;
%AO.QL1.Setpoint.RunFlagFcn = @getrunflag_ltb;

% AO.QL1.RampRate.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Save/Restore';};
% AO.QL1.RampRate.Mode = 'Simulator';
% AO.QL1.RampRate.DataType = 'Scalar';
% AO.QL1.RampRate.ChannelNames = getname_ltb('Q', 'RampRate');
% AO.QL1.RampRate.HW2PhysicsFcn = @hw2at;
% AO.QL1.RampRate.Physics2HWFcn = @at2hw;
% AO.QL1.RampRate.Units        = 'Hardware';
% AO.QL1.RampRate.HWUnits      = 'Ampere/Second';
% AO.QL1.RampRate.PhysicsUnits = 'Ampere/Second';
%(what_is1)s

AO.QL1.OnControl.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Control';};
AO.QL1.OnControl.Mode = 'Simulator';
AO.QL1.OnControl.DataType = 'Scalar';
AO.QL1.OnControl.ChannelNames = { 'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv' };

AO.QL1.OnControl.HW2PhysicsParams = 1;
AO.QL1.OnControl.Physics2HWParams = 1;
AO.QL1.OnControl.Units        = 'Hardware';
AO.QL1.OnControl.HWUnits      = '';
AO.QL1.OnControl.PhysicsUnits = '';
AO.QL1.OnControl.Range = [0 1];

% AO.QL1.On.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Monitor';};
% AO.QL1.On.Mode = 'Simulator';
% AO.QL1.On.DataType = 'Scalar';
% AO.QL1.On.ChannelNames = {''};
% AO.QL1.On.HW2PhysicsParams = 1;
% AO.QL1.On.Physics2HWParams = 1;
% AO.QL1.On.Units        = 'Hardware';
% AO.QL1.On.HWUnits      = '';
% AO.QL1.On.PhysicsUnits = '';

% AO.QL1.Reset.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Control';};
% AO.QL1.Reset.Mode = 'Simulator';
% AO.QL1.Reset.DataType = 'Scalar';
% AO.QL1.Reset.ChannelNames = {''};
% AO.QL1.Reset.HW2PhysicsParams = 1;
% AO.QL1.Reset.Physics2HWParams = 1;
% AO.QL1.Reset.Units        = 'Hardware';
% AO.QL1.Reset.HWUnits      = '';
% AO.QL1.Reset.PhysicsUnits = '';
% AO.QL1.Reset.Range = [0 1];

AO.QL1.Fault.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Monitor';};
AO.QL1.Fault.Mode = 'Simulator';
AO.QL1.Fault.DataType = 'Scalar';
AO.QL1.Fault.ChannelNames = { 'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv' };

AO.QL1.Fault.HW2PhysicsParams = 1;
AO.QL1.Fault.Physics2HWParams = 1;
AO.QL1.Fault.Units        = 'Hardware';
AO.QL1.Fault.HWUnits      = '';
AO.QL1.Fault.PhysicsUnits = '';

AO.QL2.FamilyName = 'QL2';
AO.QL2.MemberOf   = {'QUAD';  'Magnet';};
AO.QL2.DeviceList = [ 1 1; 1 2; 1 3; 1 4; 1 5; 1 6; 1 7; 1 8; 1 9; 1 10; 1 11; 1 12; 1 13; 1 14; 1 15; 1 16; 1 17; 1 18; 1 19; 1 20; 1 21; 1 22; 1 23; 1 24; 1 25; 1 26; 1 27; 1 28; 1 29; 1 30 ];
AO.QL2.ElementList = (1:size(AO.QL2.DeviceList,1))';
AO.QL2.Status = ones(size(AO.QL2.DeviceList,1),1);
AO.QL2.Position = [];
AO.QL2.CommonNames = [ 'ql2g6c30b';'ql2g2c01a';'ql2g6c02b';'ql2g2c03a';'ql2g6c04b';'ql2g2c05a';'ql2g6c06b';'ql2g2c07a';'ql2g6c08b';'ql2g2c09a';'ql2g6c10b';'ql2g2c11a';'ql2g6c12b';'ql2g2c13a';'ql2g6c14b';'ql2g2c15a';'ql2g6c16b';'ql2g2c17a';'ql2g6c18b';'ql2g2c19a';'ql2g6c20b';'ql2g2c21a';'ql2g6c22b';'ql2g2c23a';'ql2g6c24b';'ql2g2c25a';'ql2g6c26b';'ql2g2c27a';'ql2g6c28b';'ql2g2c29a' ];

AO.QL2.Monitor.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Monitor'; 'Save';};
AO.QL2.Monitor.Mode = 'Simulator';
AO.QL2.Monitor.DataType = 'Scalar';
AO.QL2.Monitor.ChannelNames = { 'V:2-SR:C30-MG:G6{QL2:94}Fld:I';'V:2-SR:C01-MG:G2{QL2:141}Fld:I';'V:2-SR:C02-MG:G6{QL2:328}Fld:I';'V:2-SR:C03-MG:G2{QL2:388}Fld:I';'V:2-SR:C04-MG:G6{QL2:575}Fld:I';'V:2-SR:C05-MG:G2{QL2:636}Fld:I';'V:2-SR:C06-MG:G6{QL2:823}Fld:I';'V:2-SR:C07-MG:G2{QL2:870}Fld:I';'V:2-SR:C08-MG:G6{QL2:1081}Fld:I';'V:2-SR:C09-MG:G2{QL2:1128}Fld:I';'V:2-SR:C10-MG:G6{QL2:1328}Fld:I';'V:2-SR:C11-MG:G2{QL2:1388}Fld:I';'V:2-SR:C12-MG:G6{QL2:1575}Fld:I';'V:2-SR:C13-MG:G2{QL2:1622}Fld:I';'V:2-SR:C14-MG:G6{QL2:1809}Fld:I';'V:2-SR:C15-MG:G2{QL2:1856}Fld:I';'V:2-SR:C16-MG:G6{QL2:2043}Fld:I';'V:2-SR:C17-MG:G2{QL2:2090}Fld:I';'V:2-SR:C18-MG:G6{QL2:2301}Fld:I';'V:2-SR:C19-MG:G2{QL2:2348}Fld:I';'V:2-SR:C20-MG:G6{QL2:2535}Fld:I';'V:2-SR:C21-MG:G2{QL2:2582}Fld:I';'V:2-SR:C22-MG:G6{QL2:2769}Fld:I';'V:2-SR:C23-MG:G2{QL2:2836}Fld:I';'V:2-SR:C24-MG:G6{QL2:3023}Fld:I';'V:2-SR:C25-MG:G2{QL2:3070}Fld:I';'V:2-SR:C26-MG:G6{QL2:3257}Fld:I';'V:2-SR:C27-MG:G2{QL2:3304}Fld:I';'V:2-SR:C28-MG:G6{QL2:3515}Fld:I';'V:2-SR:C29-MG:G2{QL2:3562}Fld:I' };

AO.QL2.Monitor.HW2PhysicsFcn = @hw2at;
AO.QL2.Monitor.Physics2HWFcn = @at2hw;
AO.QL2.Monitor.Units        = 'Hardware';
AO.QL2.Monitor.HWUnits      = 'Ampere';
AO.QL2.Monitor.PhysicsUnits = '1/Meter^2';
%AO.QL2.Monitor.Real2RawFcn = @real2raw_ltb;
%AO.QL2.Monitor.Raw2RealFcn = @raw2real_ltb;

AO.QL2.Setpoint.MemberOf = {'QUAD'; 'Magnet'; 'Save/Restore'; 'Setpoint';};
AO.QL2.Setpoint.Mode = 'Simulator';
AO.QL2.Setpoint.DataType = 'Scalar';
AO.QL2.Setpoint.ChannelNames = { 'V:2-SR:C30-MG:G6{QL2:94}Fld:SP';'V:2-SR:C01-MG:G2{QL2:141}Fld:SP';'V:2-SR:C02-MG:G6{QL2:328}Fld:SP';'V:2-SR:C03-MG:G2{QL2:388}Fld:SP';'V:2-SR:C04-MG:G6{QL2:575}Fld:SP';'V:2-SR:C05-MG:G2{QL2:636}Fld:SP';'V:2-SR:C06-MG:G6{QL2:823}Fld:SP';'V:2-SR:C07-MG:G2{QL2:870}Fld:SP';'V:2-SR:C08-MG:G6{QL2:1081}Fld:SP';'V:2-SR:C09-MG:G2{QL2:1128}Fld:SP';'V:2-SR:C10-MG:G6{QL2:1328}Fld:SP';'V:2-SR:C11-MG:G2{QL2:1388}Fld:SP';'V:2-SR:C12-MG:G6{QL2:1575}Fld:SP';'V:2-SR:C13-MG:G2{QL2:1622}Fld:SP';'V:2-SR:C14-MG:G6{QL2:1809}Fld:SP';'V:2-SR:C15-MG:G2{QL2:1856}Fld:SP';'V:2-SR:C16-MG:G6{QL2:2043}Fld:SP';'V:2-SR:C17-MG:G2{QL2:2090}Fld:SP';'V:2-SR:C18-MG:G6{QL2:2301}Fld:SP';'V:2-SR:C19-MG:G2{QL2:2348}Fld:SP';'V:2-SR:C20-MG:G6{QL2:2535}Fld:SP';'V:2-SR:C21-MG:G2{QL2:2582}Fld:SP';'V:2-SR:C22-MG:G6{QL2:2769}Fld:SP';'V:2-SR:C23-MG:G2{QL2:2836}Fld:SP';'V:2-SR:C24-MG:G6{QL2:3023}Fld:SP';'V:2-SR:C25-MG:G2{QL2:3070}Fld:SP';'V:2-SR:C26-MG:G6{QL2:3257}Fld:SP';'V:2-SR:C27-MG:G2{QL2:3304}Fld:SP';'V:2-SR:C28-MG:G6{QL2:3515}Fld:SP';'V:2-SR:C29-MG:G2{QL2:3562}Fld:SP' };

AO.QL2.Setpoint.HW2PhysicsFcn = @hw2at;
AO.QL2.Setpoint.Physics2HWFcn = @at2hw;
AO.QL2.Setpoint.Units        = 'Hardware';
AO.QL2.Setpoint.HWUnits      = 'Ampere';
AO.QL2.Setpoint.PhysicsUnits = '1/Meter^2';
AO.QL2.Setpoint.Range = [0 160];
AO.QL2.Setpoint.Tolerance = .1;
AO.QL2.Setpoint.DeltaRespMat = 1;
%AO.QL2.Setpoint.RampRate = .15;
%AO.QL2.Setpoint.RunFlagFcn = @getrunflag_ltb;

% AO.QL2.RampRate.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Save/Restore';};
% AO.QL2.RampRate.Mode = 'Simulator';
% AO.QL2.RampRate.DataType = 'Scalar';
% AO.QL2.RampRate.ChannelNames = getname_ltb('Q', 'RampRate');
% AO.QL2.RampRate.HW2PhysicsFcn = @hw2at;
% AO.QL2.RampRate.Physics2HWFcn = @at2hw;
% AO.QL2.RampRate.Units        = 'Hardware';
% AO.QL2.RampRate.HWUnits      = 'Ampere/Second';
% AO.QL2.RampRate.PhysicsUnits = 'Ampere/Second';
%(what_is1)s

AO.QL2.OnControl.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Control';};
AO.QL2.OnControl.Mode = 'Simulator';
AO.QL2.OnControl.DataType = 'Scalar';
AO.QL2.OnControl.ChannelNames = { 'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv' };

AO.QL2.OnControl.HW2PhysicsParams = 1;
AO.QL2.OnControl.Physics2HWParams = 1;
AO.QL2.OnControl.Units        = 'Hardware';
AO.QL2.OnControl.HWUnits      = '';
AO.QL2.OnControl.PhysicsUnits = '';
AO.QL2.OnControl.Range = [0 1];

% AO.QL2.On.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Monitor';};
% AO.QL2.On.Mode = 'Simulator';
% AO.QL2.On.DataType = 'Scalar';
% AO.QL2.On.ChannelNames = {''};
% AO.QL2.On.HW2PhysicsParams = 1;
% AO.QL2.On.Physics2HWParams = 1;
% AO.QL2.On.Units        = 'Hardware';
% AO.QL2.On.HWUnits      = '';
% AO.QL2.On.PhysicsUnits = '';

% AO.QL2.Reset.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Control';};
% AO.QL2.Reset.Mode = 'Simulator';
% AO.QL2.Reset.DataType = 'Scalar';
% AO.QL2.Reset.ChannelNames = {''};
% AO.QL2.Reset.HW2PhysicsParams = 1;
% AO.QL2.Reset.Physics2HWParams = 1;
% AO.QL2.Reset.Units        = 'Hardware';
% AO.QL2.Reset.HWUnits      = '';
% AO.QL2.Reset.PhysicsUnits = '';
% AO.QL2.Reset.Range = [0 1];

AO.QL2.Fault.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Monitor';};
AO.QL2.Fault.Mode = 'Simulator';
AO.QL2.Fault.DataType = 'Scalar';
AO.QL2.Fault.ChannelNames = { 'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv' };

AO.QL2.Fault.HW2PhysicsParams = 1;
AO.QL2.Fault.Physics2HWParams = 1;
AO.QL2.Fault.Units        = 'Hardware';
AO.QL2.Fault.HWUnits      = '';
AO.QL2.Fault.PhysicsUnits = '';

AO.QL3.FamilyName = 'QL3';
AO.QL3.MemberOf   = {'QUAD';  'Magnet';};
AO.QL3.DeviceList = [ 1 1; 1 2; 1 3; 1 4; 1 5; 1 6; 1 7; 1 8; 1 9; 1 10; 1 11; 1 12; 1 13; 1 14; 1 15; 1 16; 1 17; 1 18; 1 19; 1 20; 1 21; 1 22; 1 23; 1 24; 1 25; 1 26; 1 27; 1 28; 1 29; 1 30 ];
AO.QL3.ElementList = (1:size(AO.QL3.DeviceList,1))';
AO.QL3.Status = ones(size(AO.QL3.DeviceList,1),1);
AO.QL3.Position = [];
AO.QL3.CommonNames = [ 'ql3g6c30b';'ql3g2c01a';'ql3g6c02b';'ql3g2c03a';'ql3g6c04b';'ql3g2c05a';'ql3g6c06b';'ql3g2c07a';'ql3g6c08b';'ql3g2c09a';'ql3g6c10b';'ql3g2c11a';'ql3g6c12b';'ql3g2c13a';'ql3g6c14b';'ql3g2c15a';'ql3g6c16b';'ql3g2c17a';'ql3g6c18b';'ql3g2c19a';'ql3g6c20b';'ql3g2c21a';'ql3g6c22b';'ql3g2c23a';'ql3g6c24b';'ql3g2c25a';'ql3g6c26b';'ql3g2c27a';'ql3g6c28b';'ql3g2c29a' ];

AO.QL3.Monitor.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Monitor'; 'Save';};
AO.QL3.Monitor.Mode = 'Simulator';
AO.QL3.Monitor.DataType = 'Scalar';
AO.QL3.Monitor.ChannelNames = { 'V:2-SR:C30-MG:G6{QL3:83}Fld:I';'V:2-SR:C01-MG:G2{QL3:152}Fld:I';'V:2-SR:C02-MG:G6{QL3:317}Fld:I';'V:2-SR:C03-MG:G2{QL3:399}Fld:I';'V:2-SR:C04-MG:G6{QL3:564}Fld:I';'V:2-SR:C05-MG:G2{QL3:647}Fld:I';'V:2-SR:C06-MG:G6{QL3:812}Fld:I';'V:2-SR:C07-MG:G2{QL3:881}Fld:I';'V:2-SR:C08-MG:G6{QL3:1070}Fld:I';'V:2-SR:C09-MG:G2{QL3:1139}Fld:I';'V:2-SR:C10-MG:G6{QL3:1317}Fld:I';'V:2-SR:C11-MG:G2{QL3:1399}Fld:I';'V:2-SR:C12-MG:G6{QL3:1564}Fld:I';'V:2-SR:C13-MG:G2{QL3:1633}Fld:I';'V:2-SR:C14-MG:G6{QL3:1798}Fld:I';'V:2-SR:C15-MG:G2{QL3:1867}Fld:I';'V:2-SR:C16-MG:G6{QL3:2032}Fld:I';'V:2-SR:C17-MG:G2{QL3:2101}Fld:I';'V:2-SR:C18-MG:G6{QL3:2290}Fld:I';'V:2-SR:C19-MG:G2{QL3:2359}Fld:I';'V:2-SR:C20-MG:G6{QL3:2524}Fld:I';'V:2-SR:C21-MG:G2{QL3:2593}Fld:I';'V:2-SR:C22-MG:G6{QL3:2758}Fld:I';'V:2-SR:C23-MG:G2{QL3:2847}Fld:I';'V:2-SR:C24-MG:G6{QL3:3012}Fld:I';'V:2-SR:C25-MG:G2{QL3:3081}Fld:I';'V:2-SR:C26-MG:G6{QL3:3246}Fld:I';'V:2-SR:C27-MG:G2{QL3:3315}Fld:I';'V:2-SR:C28-MG:G6{QL3:3504}Fld:I';'V:2-SR:C29-MG:G2{QL3:3573}Fld:I' };

AO.QL3.Monitor.HW2PhysicsFcn = @hw2at;
AO.QL3.Monitor.Physics2HWFcn = @at2hw;
AO.QL3.Monitor.Units        = 'Hardware';
AO.QL3.Monitor.HWUnits      = 'Ampere';
AO.QL3.Monitor.PhysicsUnits = '1/Meter^2';
%AO.QL3.Monitor.Real2RawFcn = @real2raw_ltb;
%AO.QL3.Monitor.Raw2RealFcn = @raw2real_ltb;

AO.QL3.Setpoint.MemberOf = {'QUAD'; 'Magnet'; 'Save/Restore'; 'Setpoint';};
AO.QL3.Setpoint.Mode = 'Simulator';
AO.QL3.Setpoint.DataType = 'Scalar';
AO.QL3.Setpoint.ChannelNames = { 'V:2-SR:C30-MG:G6{QL3:83}Fld:SP';'V:2-SR:C01-MG:G2{QL3:152}Fld:SP';'V:2-SR:C02-MG:G6{QL3:317}Fld:SP';'V:2-SR:C03-MG:G2{QL3:399}Fld:SP';'V:2-SR:C04-MG:G6{QL3:564}Fld:SP';'V:2-SR:C05-MG:G2{QL3:647}Fld:SP';'V:2-SR:C06-MG:G6{QL3:812}Fld:SP';'V:2-SR:C07-MG:G2{QL3:881}Fld:SP';'V:2-SR:C08-MG:G6{QL3:1070}Fld:SP';'V:2-SR:C09-MG:G2{QL3:1139}Fld:SP';'V:2-SR:C10-MG:G6{QL3:1317}Fld:SP';'V:2-SR:C11-MG:G2{QL3:1399}Fld:SP';'V:2-SR:C12-MG:G6{QL3:1564}Fld:SP';'V:2-SR:C13-MG:G2{QL3:1633}Fld:SP';'V:2-SR:C14-MG:G6{QL3:1798}Fld:SP';'V:2-SR:C15-MG:G2{QL3:1867}Fld:SP';'V:2-SR:C16-MG:G6{QL3:2032}Fld:SP';'V:2-SR:C17-MG:G2{QL3:2101}Fld:SP';'V:2-SR:C18-MG:G6{QL3:2290}Fld:SP';'V:2-SR:C19-MG:G2{QL3:2359}Fld:SP';'V:2-SR:C20-MG:G6{QL3:2524}Fld:SP';'V:2-SR:C21-MG:G2{QL3:2593}Fld:SP';'V:2-SR:C22-MG:G6{QL3:2758}Fld:SP';'V:2-SR:C23-MG:G2{QL3:2847}Fld:SP';'V:2-SR:C24-MG:G6{QL3:3012}Fld:SP';'V:2-SR:C25-MG:G2{QL3:3081}Fld:SP';'V:2-SR:C26-MG:G6{QL3:3246}Fld:SP';'V:2-SR:C27-MG:G2{QL3:3315}Fld:SP';'V:2-SR:C28-MG:G6{QL3:3504}Fld:SP';'V:2-SR:C29-MG:G2{QL3:3573}Fld:SP' };

AO.QL3.Setpoint.HW2PhysicsFcn = @hw2at;
AO.QL3.Setpoint.Physics2HWFcn = @at2hw;
AO.QL3.Setpoint.Units        = 'Hardware';
AO.QL3.Setpoint.HWUnits      = 'Ampere';
AO.QL3.Setpoint.PhysicsUnits = '1/Meter^2';
AO.QL3.Setpoint.Range = [0 160];
AO.QL3.Setpoint.Tolerance = .1;
AO.QL3.Setpoint.DeltaRespMat = 1;
%AO.QL3.Setpoint.RampRate = .15;
%AO.QL3.Setpoint.RunFlagFcn = @getrunflag_ltb;

% AO.QL3.RampRate.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Save/Restore';};
% AO.QL3.RampRate.Mode = 'Simulator';
% AO.QL3.RampRate.DataType = 'Scalar';
% AO.QL3.RampRate.ChannelNames = getname_ltb('Q', 'RampRate');
% AO.QL3.RampRate.HW2PhysicsFcn = @hw2at;
% AO.QL3.RampRate.Physics2HWFcn = @at2hw;
% AO.QL3.RampRate.Units        = 'Hardware';
% AO.QL3.RampRate.HWUnits      = 'Ampere/Second';
% AO.QL3.RampRate.PhysicsUnits = 'Ampere/Second';
%(what_is1)s

AO.QL3.OnControl.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Control';};
AO.QL3.OnControl.Mode = 'Simulator';
AO.QL3.OnControl.DataType = 'Scalar';
AO.QL3.OnControl.ChannelNames = { 'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv' };

AO.QL3.OnControl.HW2PhysicsParams = 1;
AO.QL3.OnControl.Physics2HWParams = 1;
AO.QL3.OnControl.Units        = 'Hardware';
AO.QL3.OnControl.HWUnits      = '';
AO.QL3.OnControl.PhysicsUnits = '';
AO.QL3.OnControl.Range = [0 1];

% AO.QL3.On.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Monitor';};
% AO.QL3.On.Mode = 'Simulator';
% AO.QL3.On.DataType = 'Scalar';
% AO.QL3.On.ChannelNames = {''};
% AO.QL3.On.HW2PhysicsParams = 1;
% AO.QL3.On.Physics2HWParams = 1;
% AO.QL3.On.Units        = 'Hardware';
% AO.QL3.On.HWUnits      = '';
% AO.QL3.On.PhysicsUnits = '';

% AO.QL3.Reset.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Control';};
% AO.QL3.Reset.Mode = 'Simulator';
% AO.QL3.Reset.DataType = 'Scalar';
% AO.QL3.Reset.ChannelNames = {''};
% AO.QL3.Reset.HW2PhysicsParams = 1;
% AO.QL3.Reset.Physics2HWParams = 1;
% AO.QL3.Reset.Units        = 'Hardware';
% AO.QL3.Reset.HWUnits      = '';
% AO.QL3.Reset.PhysicsUnits = '';
% AO.QL3.Reset.Range = [0 1];

AO.QL3.Fault.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Monitor';};
AO.QL3.Fault.Mode = 'Simulator';
AO.QL3.Fault.DataType = 'Scalar';
AO.QL3.Fault.ChannelNames = { 'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv' };

AO.QL3.Fault.HW2PhysicsParams = 1;
AO.QL3.Fault.Physics2HWParams = 1;
AO.QL3.Fault.Units        = 'Hardware';
AO.QL3.Fault.HWUnits      = '';
AO.QL3.Fault.PhysicsUnits = '';

AO.QM1.FamilyName = 'QM1';
AO.QM1.MemberOf   = {'QUAD';  'Magnet';};
AO.QM1.DeviceList = [ 1 1; 1 2; 1 3; 1 4; 1 5; 1 6; 1 7; 1 8; 1 9; 1 10; 1 11; 1 12; 1 13; 1 14; 1 15; 1 16; 1 17; 1 18; 1 19; 1 20; 1 21; 1 22; 1 23; 1 24; 1 25; 1 26; 1 27; 1 28; 1 29; 1 30; 1 31; 1 32; 1 33; 1 34; 1 35; 1 36; 1 37; 1 38; 1 39; 1 40; 1 41; 1 42; 1 43; 1 44; 1 45; 1 46; 1 47; 1 48; 1 49; 1 50; 1 51; 1 52; 1 53; 1 54; 1 55; 1 56; 1 57; 1 58; 1 59; 1 60 ];
AO.QM1.ElementList = (1:size(AO.QM1.DeviceList,1))';
AO.QM1.Status = ones(size(AO.QM1.DeviceList,1),1);
AO.QM1.Position = [];
AO.QM1.CommonNames = [ 'qm1g4c30a';'qm1g4c30b';'qm1g4c01a';'qm1g4c01b';'qm1g4c02a';'qm1g4c02b';'qm1g4c03a';'qm1g4c03b';'qm1g4c04a';'qm1g4c04b';'qm1g4c05a';'qm1g4c05b';'qm1g4c06a';'qm1g4c06b';'qm1g4c07a';'qm1g4c07b';'qm1g4c08a';'qm1g4c08b';'qm1g4c09a';'qm1g4c09b';'qm1g4c10a';'qm1g4c10b';'qm1g4c11a';'qm1g4c11b';'qm1g4c12a';'qm1g4c12b';'qm1g4c13a';'qm1g4c13b';'qm1g4c14a';'qm1g4c14b';'qm1g4c15a';'qm1g4c15b';'qm1g4c16a';'qm1g4c16b';'qm1g4c17a';'qm1g4c17b';'qm1g4c18a';'qm1g4c18b';'qm1g4c19a';'qm1g4c19b';'qm1g4c20a';'qm1g4c20b';'qm1g4c21a';'qm1g4c21b';'qm1g4c22a';'qm1g4c22b';'qm1g4c23a';'qm1g4c23b';'qm1g4c24a';'qm1g4c24b';'qm1g4c25a';'qm1g4c25b';'qm1g4c26a';'qm1g4c26b';'qm1g4c27a';'qm1g4c27b';'qm1g4c28a';'qm1g4c28b';'qm1g4c29a';'qm1g4c29b' ];

AO.QM1.Monitor.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Monitor'; 'Save';};
AO.QM1.Monitor.Mode = 'Simulator';
AO.QM1.Monitor.DataType = 'Scalar';
AO.QM1.Monitor.ChannelNames = { 'V:2-SR:C30-MG:G4{QM1:46}Fld:I';'V:2-SR:C30-MG:G4{QM1:67}Fld:I';'V:2-SR:C01-MG:G4{QM1:166}Fld:I';'V:2-SR:C01-MG:G4{QM1:187}Fld:I';'V:2-SR:C02-MG:G4{QM1:280}Fld:I';'V:2-SR:C02-MG:G4{QM1:301}Fld:I';'V:2-SR:C03-MG:G4{QM1:413}Fld:I';'V:2-SR:C03-MG:G4{QM1:434}Fld:I';'V:2-SR:C04-MG:G4{QM1:527}Fld:I';'V:2-SR:C04-MG:G4{QM1:548}Fld:I';'V:2-SR:C05-MG:G4{QM1:661}Fld:I';'V:2-SR:C05-MG:G4{QM1:682}Fld:I';'V:2-SR:C06-MG:G4{QM1:775}Fld:I';'V:2-SR:C06-MG:G4{QM1:796}Fld:I';'V:2-SR:C07-MG:G4{QM1:895}Fld:I';'V:2-SR:C07-MG:G4{QM1:916}Fld:I';'V:2-SR:C08-MG:G4{QM1:1033}Fld:I';'V:2-SR:C08-MG:G4{QM1:1054}Fld:I';'V:2-SR:C09-MG:G4{QM1:1153}Fld:I';'V:2-SR:C09-MG:G4{QM1:1174}Fld:I';'V:2-SR:C10-MG:G4{QM1:1280}Fld:I';'V:2-SR:C10-MG:G4{QM1:1301}Fld:I';'V:2-SR:C11-MG:G4{QM1:1413}Fld:I';'V:2-SR:C11-MG:G4{QM1:1434}Fld:I';'V:2-SR:C12-MG:G4{QM1:1527}Fld:I';'V:2-SR:C12-MG:G4{QM1:1548}Fld:I';'V:2-SR:C13-MG:G4{QM1:1647}Fld:I';'V:2-SR:C13-MG:G4{QM1:1668}Fld:I';'V:2-SR:C14-MG:G4{QM1:1761}Fld:I';'V:2-SR:C14-MG:G4{QM1:1782}Fld:I';'V:2-SR:C15-MG:G4{QM1:1881}Fld:I';'V:2-SR:C15-MG:G4{QM1:1902}Fld:I';'V:2-SR:C16-MG:G4{QM1:1995}Fld:I';'V:2-SR:C16-MG:G4{QM1:2016}Fld:I';'V:2-SR:C17-MG:G4{QM1:2115}Fld:I';'V:2-SR:C17-MG:G4{QM1:2136}Fld:I';'V:2-SR:C18-MG:G4{QM1:2253}Fld:I';'V:2-SR:C18-MG:G4{QM1:2274}Fld:I';'V:2-SR:C19-MG:G4{QM1:2373}Fld:I';'V:2-SR:C19-MG:G4{QM1:2394}Fld:I';'V:2-SR:C20-MG:G4{QM1:2487}Fld:I';'V:2-SR:C20-MG:G4{QM1:2508}Fld:I';'V:2-SR:C21-MG:G4{QM1:2607}Fld:I';'V:2-SR:C21-MG:G4{QM1:2628}Fld:I';'V:2-SR:C22-MG:G4{QM1:2721}Fld:I';'V:2-SR:C22-MG:G4{QM1:2742}Fld:I';'V:2-SR:C23-MG:G4{QM1:2861}Fld:I';'V:2-SR:C23-MG:G4{QM1:2882}Fld:I';'V:2-SR:C24-MG:G4{QM1:2975}Fld:I';'V:2-SR:C24-MG:G4{QM1:2996}Fld:I';'V:2-SR:C25-MG:G4{QM1:3095}Fld:I';'V:2-SR:C25-MG:G4{QM1:3116}Fld:I';'V:2-SR:C26-MG:G4{QM1:3209}Fld:I';'V:2-SR:C26-MG:G4{QM1:3230}Fld:I';'V:2-SR:C27-MG:G4{QM1:3329}Fld:I';'V:2-SR:C27-MG:G4{QM1:3350}Fld:I';'V:2-SR:C28-MG:G4{QM1:3467}Fld:I';'V:2-SR:C28-MG:G4{QM1:3488}Fld:I';'V:2-SR:C29-MG:G4{QM1:3587}Fld:I';'V:2-SR:C29-MG:G4{QM1:3608}Fld:I' };

AO.QM1.Monitor.HW2PhysicsFcn = @hw2at;
AO.QM1.Monitor.Physics2HWFcn = @at2hw;
AO.QM1.Monitor.Units        = 'Hardware';
AO.QM1.Monitor.HWUnits      = 'Ampere';
AO.QM1.Monitor.PhysicsUnits = '1/Meter^2';
%AO.QM1.Monitor.Real2RawFcn = @real2raw_ltb;
%AO.QM1.Monitor.Raw2RealFcn = @raw2real_ltb;

AO.QM1.Setpoint.MemberOf = {'QUAD'; 'Magnet'; 'Save/Restore'; 'Setpoint';};
AO.QM1.Setpoint.Mode = 'Simulator';
AO.QM1.Setpoint.DataType = 'Scalar';
AO.QM1.Setpoint.ChannelNames = { 'V:2-SR:C30-MG:G4{QM1:46}Fld:SP';'V:2-SR:C30-MG:G4{QM1:67}Fld:SP';'V:2-SR:C01-MG:G4{QM1:166}Fld:SP';'V:2-SR:C01-MG:G4{QM1:187}Fld:SP';'V:2-SR:C02-MG:G4{QM1:280}Fld:SP';'V:2-SR:C02-MG:G4{QM1:301}Fld:SP';'V:2-SR:C03-MG:G4{QM1:413}Fld:SP';'V:2-SR:C03-MG:G4{QM1:434}Fld:SP';'V:2-SR:C04-MG:G4{QM1:527}Fld:SP';'V:2-SR:C04-MG:G4{QM1:548}Fld:SP';'V:2-SR:C05-MG:G4{QM1:661}Fld:SP';'V:2-SR:C05-MG:G4{QM1:682}Fld:SP';'V:2-SR:C06-MG:G4{QM1:775}Fld:SP';'V:2-SR:C06-MG:G4{QM1:796}Fld:SP';'V:2-SR:C07-MG:G4{QM1:895}Fld:SP';'V:2-SR:C07-MG:G4{QM1:916}Fld:SP';'V:2-SR:C08-MG:G4{QM1:1033}Fld:SP';'V:2-SR:C08-MG:G4{QM1:1054}Fld:SP';'V:2-SR:C09-MG:G4{QM1:1153}Fld:SP';'V:2-SR:C09-MG:G4{QM1:1174}Fld:SP';'V:2-SR:C10-MG:G4{QM1:1280}Fld:SP';'V:2-SR:C10-MG:G4{QM1:1301}Fld:SP';'V:2-SR:C11-MG:G4{QM1:1413}Fld:SP';'V:2-SR:C11-MG:G4{QM1:1434}Fld:SP';'V:2-SR:C12-MG:G4{QM1:1527}Fld:SP';'V:2-SR:C12-MG:G4{QM1:1548}Fld:SP';'V:2-SR:C13-MG:G4{QM1:1647}Fld:SP';'V:2-SR:C13-MG:G4{QM1:1668}Fld:SP';'V:2-SR:C14-MG:G4{QM1:1761}Fld:SP';'V:2-SR:C14-MG:G4{QM1:1782}Fld:SP';'V:2-SR:C15-MG:G4{QM1:1881}Fld:SP';'V:2-SR:C15-MG:G4{QM1:1902}Fld:SP';'V:2-SR:C16-MG:G4{QM1:1995}Fld:SP';'V:2-SR:C16-MG:G4{QM1:2016}Fld:SP';'V:2-SR:C17-MG:G4{QM1:2115}Fld:SP';'V:2-SR:C17-MG:G4{QM1:2136}Fld:SP';'V:2-SR:C18-MG:G4{QM1:2253}Fld:SP';'V:2-SR:C18-MG:G4{QM1:2274}Fld:SP';'V:2-SR:C19-MG:G4{QM1:2373}Fld:SP';'V:2-SR:C19-MG:G4{QM1:2394}Fld:SP';'V:2-SR:C20-MG:G4{QM1:2487}Fld:SP';'V:2-SR:C20-MG:G4{QM1:2508}Fld:SP';'V:2-SR:C21-MG:G4{QM1:2607}Fld:SP';'V:2-SR:C21-MG:G4{QM1:2628}Fld:SP';'V:2-SR:C22-MG:G4{QM1:2721}Fld:SP';'V:2-SR:C22-MG:G4{QM1:2742}Fld:SP';'V:2-SR:C23-MG:G4{QM1:2861}Fld:SP';'V:2-SR:C23-MG:G4{QM1:2882}Fld:SP';'V:2-SR:C24-MG:G4{QM1:2975}Fld:SP';'V:2-SR:C24-MG:G4{QM1:2996}Fld:SP';'V:2-SR:C25-MG:G4{QM1:3095}Fld:SP';'V:2-SR:C25-MG:G4{QM1:3116}Fld:SP';'V:2-SR:C26-MG:G4{QM1:3209}Fld:SP';'V:2-SR:C26-MG:G4{QM1:3230}Fld:SP';'V:2-SR:C27-MG:G4{QM1:3329}Fld:SP';'V:2-SR:C27-MG:G4{QM1:3350}Fld:SP';'V:2-SR:C28-MG:G4{QM1:3467}Fld:SP';'V:2-SR:C28-MG:G4{QM1:3488}Fld:SP';'V:2-SR:C29-MG:G4{QM1:3587}Fld:SP';'V:2-SR:C29-MG:G4{QM1:3608}Fld:SP' };

AO.QM1.Setpoint.HW2PhysicsFcn = @hw2at;
AO.QM1.Setpoint.Physics2HWFcn = @at2hw;
AO.QM1.Setpoint.Units        = 'Hardware';
AO.QM1.Setpoint.HWUnits      = 'Ampere';
AO.QM1.Setpoint.PhysicsUnits = '1/Meter^2';
AO.QM1.Setpoint.Range = [0 160];
AO.QM1.Setpoint.Tolerance = .1;
AO.QM1.Setpoint.DeltaRespMat = 1;
%AO.QM1.Setpoint.RampRate = .15;
%AO.QM1.Setpoint.RunFlagFcn = @getrunflag_ltb;

% AO.QM1.RampRate.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Save/Restore';};
% AO.QM1.RampRate.Mode = 'Simulator';
% AO.QM1.RampRate.DataType = 'Scalar';
% AO.QM1.RampRate.ChannelNames = getname_ltb('Q', 'RampRate');
% AO.QM1.RampRate.HW2PhysicsFcn = @hw2at;
% AO.QM1.RampRate.Physics2HWFcn = @at2hw;
% AO.QM1.RampRate.Units        = 'Hardware';
% AO.QM1.RampRate.HWUnits      = 'Ampere/Second';
% AO.QM1.RampRate.PhysicsUnits = 'Ampere/Second';
%(what_is1)s

AO.QM1.OnControl.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Control';};
AO.QM1.OnControl.Mode = 'Simulator';
AO.QM1.OnControl.DataType = 'Scalar';
AO.QM1.OnControl.ChannelNames = { 'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv' };

AO.QM1.OnControl.HW2PhysicsParams = 1;
AO.QM1.OnControl.Physics2HWParams = 1;
AO.QM1.OnControl.Units        = 'Hardware';
AO.QM1.OnControl.HWUnits      = '';
AO.QM1.OnControl.PhysicsUnits = '';
AO.QM1.OnControl.Range = [0 1];

% AO.QM1.On.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Monitor';};
% AO.QM1.On.Mode = 'Simulator';
% AO.QM1.On.DataType = 'Scalar';
% AO.QM1.On.ChannelNames = {''};
% AO.QM1.On.HW2PhysicsParams = 1;
% AO.QM1.On.Physics2HWParams = 1;
% AO.QM1.On.Units        = 'Hardware';
% AO.QM1.On.HWUnits      = '';
% AO.QM1.On.PhysicsUnits = '';

% AO.QM1.Reset.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Control';};
% AO.QM1.Reset.Mode = 'Simulator';
% AO.QM1.Reset.DataType = 'Scalar';
% AO.QM1.Reset.ChannelNames = {''};
% AO.QM1.Reset.HW2PhysicsParams = 1;
% AO.QM1.Reset.Physics2HWParams = 1;
% AO.QM1.Reset.Units        = 'Hardware';
% AO.QM1.Reset.HWUnits      = '';
% AO.QM1.Reset.PhysicsUnits = '';
% AO.QM1.Reset.Range = [0 1];

AO.QM1.Fault.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Monitor';};
AO.QM1.Fault.Mode = 'Simulator';
AO.QM1.Fault.DataType = 'Scalar';
AO.QM1.Fault.ChannelNames = { 'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv' };

AO.QM1.Fault.HW2PhysicsParams = 1;
AO.QM1.Fault.Physics2HWParams = 1;
AO.QM1.Fault.Units        = 'Hardware';
AO.QM1.Fault.HWUnits      = '';
AO.QM1.Fault.PhysicsUnits = '';

AO.QM2.FamilyName = 'QM2';
AO.QM2.MemberOf   = {'QUAD';  'Magnet';};
AO.QM2.DeviceList = [ 1 1; 1 2; 1 3; 1 4; 1 5; 1 6; 1 7; 1 8; 1 9; 1 10; 1 11; 1 12; 1 13; 1 14; 1 15; 1 16; 1 17; 1 18; 1 19; 1 20; 1 21; 1 22; 1 23; 1 24; 1 25; 1 26; 1 27; 1 28; 1 29; 1 30; 1 31; 1 32; 1 33; 1 34; 1 35; 1 36; 1 37; 1 38; 1 39; 1 40; 1 41; 1 42; 1 43; 1 44; 1 45; 1 46; 1 47; 1 48; 1 49; 1 50; 1 51; 1 52; 1 53; 1 54; 1 55; 1 56; 1 57; 1 58; 1 59; 1 60 ];
AO.QM2.ElementList = (1:size(AO.QM2.DeviceList,1))';
AO.QM2.Status = ones(size(AO.QM2.DeviceList,1),1);
AO.QM2.Position = [];
AO.QM2.CommonNames = [ 'qm2g4c30a';'qm2g4c30b';'qm2g4c01a';'qm2g4c01b';'qm2g4c02a';'qm2g4c02b';'qm2g4c03a';'qm2g4c03b';'qm2g4c04a';'qm2g4c04b';'qm2g4c05a';'qm2g4c05b';'qm2g4c06a';'qm2g4c06b';'qm2g4c07a';'qm2g4c07b';'qm2g4c08a';'qm2g4c08b';'qm2g4c09a';'qm2g4c09b';'qm2g4c10a';'qm2g4c10b';'qm2g4c11a';'qm2g4c11b';'qm2g4c12a';'qm2g4c12b';'qm2g4c13a';'qm2g4c13b';'qm2g4c14a';'qm2g4c14b';'qm2g4c15a';'qm2g4c15b';'qm2g4c16a';'qm2g4c16b';'qm2g4c17a';'qm2g4c17b';'qm2g4c18a';'qm2g4c18b';'qm2g4c19a';'qm2g4c19b';'qm2g4c20a';'qm2g4c20b';'qm2g4c21a';'qm2g4c21b';'qm2g4c22a';'qm2g4c22b';'qm2g4c23a';'qm2g4c23b';'qm2g4c24a';'qm2g4c24b';'qm2g4c25a';'qm2g4c25b';'qm2g4c26a';'qm2g4c26b';'qm2g4c27a';'qm2g4c27b';'qm2g4c28a';'qm2g4c28b';'qm2g4c29a';'qm2g4c29b' ];

AO.QM2.Monitor.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Monitor'; 'Save';};
AO.QM2.Monitor.Mode = 'Simulator';
AO.QM2.Monitor.DataType = 'Scalar';
AO.QM2.Monitor.ChannelNames = { 'V:2-SR:C30-MG:G4{QM2:57}Fld:I';'V:2-SR:C30-MG:G4{QM2:61}Fld:I';'V:2-SR:C01-MG:G4{QM2:177}Fld:I';'V:2-SR:C01-MG:G4{QM2:181}Fld:I';'V:2-SR:C02-MG:G4{QM2:291}Fld:I';'V:2-SR:C02-MG:G4{QM2:295}Fld:I';'V:2-SR:C03-MG:G4{QM2:424}Fld:I';'V:2-SR:C03-MG:G4{QM2:428}Fld:I';'V:2-SR:C04-MG:G4{QM2:538}Fld:I';'V:2-SR:C04-MG:G4{QM2:542}Fld:I';'V:2-SR:C05-MG:G4{QM2:672}Fld:I';'V:2-SR:C05-MG:G4{QM2:676}Fld:I';'V:2-SR:C06-MG:G4{QM2:786}Fld:I';'V:2-SR:C06-MG:G4{QM2:790}Fld:I';'V:2-SR:C07-MG:G4{QM2:906}Fld:I';'V:2-SR:C07-MG:G4{QM2:910}Fld:I';'V:2-SR:C08-MG:G4{QM2:1044}Fld:I';'V:2-SR:C08-MG:G4{QM2:1048}Fld:I';'V:2-SR:C09-MG:G4{QM2:1164}Fld:I';'V:2-SR:C09-MG:G4{QM2:1168}Fld:I';'V:2-SR:C10-MG:G4{QM2:1291}Fld:I';'V:2-SR:C10-MG:G4{QM2:1295}Fld:I';'V:2-SR:C11-MG:G4{QM2:1424}Fld:I';'V:2-SR:C11-MG:G4{QM2:1428}Fld:I';'V:2-SR:C12-MG:G4{QM2:1538}Fld:I';'V:2-SR:C12-MG:G4{QM2:1542}Fld:I';'V:2-SR:C13-MG:G4{QM2:1658}Fld:I';'V:2-SR:C13-MG:G4{QM2:1662}Fld:I';'V:2-SR:C14-MG:G4{QM2:1772}Fld:I';'V:2-SR:C14-MG:G4{QM2:1776}Fld:I';'V:2-SR:C15-MG:G4{QM2:1892}Fld:I';'V:2-SR:C15-MG:G4{QM2:1896}Fld:I';'V:2-SR:C16-MG:G4{QM2:2006}Fld:I';'V:2-SR:C16-MG:G4{QM2:2010}Fld:I';'V:2-SR:C17-MG:G4{QM2:2126}Fld:I';'V:2-SR:C17-MG:G4{QM2:2130}Fld:I';'V:2-SR:C18-MG:G4{QM2:2264}Fld:I';'V:2-SR:C18-MG:G4{QM2:2268}Fld:I';'V:2-SR:C19-MG:G4{QM2:2384}Fld:I';'V:2-SR:C19-MG:G4{QM2:2388}Fld:I';'V:2-SR:C20-MG:G4{QM2:2498}Fld:I';'V:2-SR:C20-MG:G4{QM2:2502}Fld:I';'V:2-SR:C21-MG:G4{QM2:2618}Fld:I';'V:2-SR:C21-MG:G4{QM2:2622}Fld:I';'V:2-SR:C22-MG:G4{QM2:2732}Fld:I';'V:2-SR:C22-MG:G4{QM2:2736}Fld:I';'V:2-SR:C23-MG:G4{QM2:2872}Fld:I';'V:2-SR:C23-MG:G4{QM2:2876}Fld:I';'V:2-SR:C24-MG:G4{QM2:2986}Fld:I';'V:2-SR:C24-MG:G4{QM2:2990}Fld:I';'V:2-SR:C25-MG:G4{QM2:3106}Fld:I';'V:2-SR:C25-MG:G4{QM2:3110}Fld:I';'V:2-SR:C26-MG:G4{QM2:3220}Fld:I';'V:2-SR:C26-MG:G4{QM2:3224}Fld:I';'V:2-SR:C27-MG:G4{QM2:3340}Fld:I';'V:2-SR:C27-MG:G4{QM2:3344}Fld:I';'V:2-SR:C28-MG:G4{QM2:3478}Fld:I';'V:2-SR:C28-MG:G4{QM2:3482}Fld:I';'V:2-SR:C29-MG:G4{QM2:3598}Fld:I';'V:2-SR:C29-MG:G4{QM2:3602}Fld:I' };

AO.QM2.Monitor.HW2PhysicsFcn = @hw2at;
AO.QM2.Monitor.Physics2HWFcn = @at2hw;
AO.QM2.Monitor.Units        = 'Hardware';
AO.QM2.Monitor.HWUnits      = 'Ampere';
AO.QM2.Monitor.PhysicsUnits = '1/Meter^2';
%AO.QM2.Monitor.Real2RawFcn = @real2raw_ltb;
%AO.QM2.Monitor.Raw2RealFcn = @raw2real_ltb;

AO.QM2.Setpoint.MemberOf = {'QUAD'; 'Magnet'; 'Save/Restore'; 'Setpoint';};
AO.QM2.Setpoint.Mode = 'Simulator';
AO.QM2.Setpoint.DataType = 'Scalar';
AO.QM2.Setpoint.ChannelNames = { 'V:2-SR:C30-MG:G4{QM2:57}Fld:SP';'V:2-SR:C30-MG:G4{QM2:61}Fld:SP';'V:2-SR:C01-MG:G4{QM2:177}Fld:SP';'V:2-SR:C01-MG:G4{QM2:181}Fld:SP';'V:2-SR:C02-MG:G4{QM2:291}Fld:SP';'V:2-SR:C02-MG:G4{QM2:295}Fld:SP';'V:2-SR:C03-MG:G4{QM2:424}Fld:SP';'V:2-SR:C03-MG:G4{QM2:428}Fld:SP';'V:2-SR:C04-MG:G4{QM2:538}Fld:SP';'V:2-SR:C04-MG:G4{QM2:542}Fld:SP';'V:2-SR:C05-MG:G4{QM2:672}Fld:SP';'V:2-SR:C05-MG:G4{QM2:676}Fld:SP';'V:2-SR:C06-MG:G4{QM2:786}Fld:SP';'V:2-SR:C06-MG:G4{QM2:790}Fld:SP';'V:2-SR:C07-MG:G4{QM2:906}Fld:SP';'V:2-SR:C07-MG:G4{QM2:910}Fld:SP';'V:2-SR:C08-MG:G4{QM2:1044}Fld:SP';'V:2-SR:C08-MG:G4{QM2:1048}Fld:SP';'V:2-SR:C09-MG:G4{QM2:1164}Fld:SP';'V:2-SR:C09-MG:G4{QM2:1168}Fld:SP';'V:2-SR:C10-MG:G4{QM2:1291}Fld:SP';'V:2-SR:C10-MG:G4{QM2:1295}Fld:SP';'V:2-SR:C11-MG:G4{QM2:1424}Fld:SP';'V:2-SR:C11-MG:G4{QM2:1428}Fld:SP';'V:2-SR:C12-MG:G4{QM2:1538}Fld:SP';'V:2-SR:C12-MG:G4{QM2:1542}Fld:SP';'V:2-SR:C13-MG:G4{QM2:1658}Fld:SP';'V:2-SR:C13-MG:G4{QM2:1662}Fld:SP';'V:2-SR:C14-MG:G4{QM2:1772}Fld:SP';'V:2-SR:C14-MG:G4{QM2:1776}Fld:SP';'V:2-SR:C15-MG:G4{QM2:1892}Fld:SP';'V:2-SR:C15-MG:G4{QM2:1896}Fld:SP';'V:2-SR:C16-MG:G4{QM2:2006}Fld:SP';'V:2-SR:C16-MG:G4{QM2:2010}Fld:SP';'V:2-SR:C17-MG:G4{QM2:2126}Fld:SP';'V:2-SR:C17-MG:G4{QM2:2130}Fld:SP';'V:2-SR:C18-MG:G4{QM2:2264}Fld:SP';'V:2-SR:C18-MG:G4{QM2:2268}Fld:SP';'V:2-SR:C19-MG:G4{QM2:2384}Fld:SP';'V:2-SR:C19-MG:G4{QM2:2388}Fld:SP';'V:2-SR:C20-MG:G4{QM2:2498}Fld:SP';'V:2-SR:C20-MG:G4{QM2:2502}Fld:SP';'V:2-SR:C21-MG:G4{QM2:2618}Fld:SP';'V:2-SR:C21-MG:G4{QM2:2622}Fld:SP';'V:2-SR:C22-MG:G4{QM2:2732}Fld:SP';'V:2-SR:C22-MG:G4{QM2:2736}Fld:SP';'V:2-SR:C23-MG:G4{QM2:2872}Fld:SP';'V:2-SR:C23-MG:G4{QM2:2876}Fld:SP';'V:2-SR:C24-MG:G4{QM2:2986}Fld:SP';'V:2-SR:C24-MG:G4{QM2:2990}Fld:SP';'V:2-SR:C25-MG:G4{QM2:3106}Fld:SP';'V:2-SR:C25-MG:G4{QM2:3110}Fld:SP';'V:2-SR:C26-MG:G4{QM2:3220}Fld:SP';'V:2-SR:C26-MG:G4{QM2:3224}Fld:SP';'V:2-SR:C27-MG:G4{QM2:3340}Fld:SP';'V:2-SR:C27-MG:G4{QM2:3344}Fld:SP';'V:2-SR:C28-MG:G4{QM2:3478}Fld:SP';'V:2-SR:C28-MG:G4{QM2:3482}Fld:SP';'V:2-SR:C29-MG:G4{QM2:3598}Fld:SP';'V:2-SR:C29-MG:G4{QM2:3602}Fld:SP' };

AO.QM2.Setpoint.HW2PhysicsFcn = @hw2at;
AO.QM2.Setpoint.Physics2HWFcn = @at2hw;
AO.QM2.Setpoint.Units        = 'Hardware';
AO.QM2.Setpoint.HWUnits      = 'Ampere';
AO.QM2.Setpoint.PhysicsUnits = '1/Meter^2';
AO.QM2.Setpoint.Range = [0 160];
AO.QM2.Setpoint.Tolerance = .1;
AO.QM2.Setpoint.DeltaRespMat = 1;
%AO.QM2.Setpoint.RampRate = .15;
%AO.QM2.Setpoint.RunFlagFcn = @getrunflag_ltb;

% AO.QM2.RampRate.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Save/Restore';};
% AO.QM2.RampRate.Mode = 'Simulator';
% AO.QM2.RampRate.DataType = 'Scalar';
% AO.QM2.RampRate.ChannelNames = getname_ltb('Q', 'RampRate');
% AO.QM2.RampRate.HW2PhysicsFcn = @hw2at;
% AO.QM2.RampRate.Physics2HWFcn = @at2hw;
% AO.QM2.RampRate.Units        = 'Hardware';
% AO.QM2.RampRate.HWUnits      = 'Ampere/Second';
% AO.QM2.RampRate.PhysicsUnits = 'Ampere/Second';
%(what_is1)s

AO.QM2.OnControl.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Control';};
AO.QM2.OnControl.Mode = 'Simulator';
AO.QM2.OnControl.DataType = 'Scalar';
AO.QM2.OnControl.ChannelNames = { 'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv' };

AO.QM2.OnControl.HW2PhysicsParams = 1;
AO.QM2.OnControl.Physics2HWParams = 1;
AO.QM2.OnControl.Units        = 'Hardware';
AO.QM2.OnControl.HWUnits      = '';
AO.QM2.OnControl.PhysicsUnits = '';
AO.QM2.OnControl.Range = [0 1];

% AO.QM2.On.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Monitor';};
% AO.QM2.On.Mode = 'Simulator';
% AO.QM2.On.DataType = 'Scalar';
% AO.QM2.On.ChannelNames = {''};
% AO.QM2.On.HW2PhysicsParams = 1;
% AO.QM2.On.Physics2HWParams = 1;
% AO.QM2.On.Units        = 'Hardware';
% AO.QM2.On.HWUnits      = '';
% AO.QM2.On.PhysicsUnits = '';

% AO.QM2.Reset.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Control';};
% AO.QM2.Reset.Mode = 'Simulator';
% AO.QM2.Reset.DataType = 'Scalar';
% AO.QM2.Reset.ChannelNames = {''};
% AO.QM2.Reset.HW2PhysicsParams = 1;
% AO.QM2.Reset.Physics2HWParams = 1;
% AO.QM2.Reset.Units        = 'Hardware';
% AO.QM2.Reset.HWUnits      = '';
% AO.QM2.Reset.PhysicsUnits = '';
% AO.QM2.Reset.Range = [0 1];

AO.QM2.Fault.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Monitor';};
AO.QM2.Fault.Mode = 'Simulator';
AO.QM2.Fault.DataType = 'Scalar';
AO.QM2.Fault.ChannelNames = { 'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv';'fakepv' };

AO.QM2.Fault.HW2PhysicsParams = 1;
AO.QM2.Fault.Physics2HWParams = 1;
AO.QM2.Fault.Units        = 'Hardware';
AO.QM2.Fault.HWUnits      = '';
AO.QM2.Fault.PhysicsUnits = '';




% Save the AO so that family2dev will work
% setao(AO);

% The operational mode sets the path, filenames, and other important parameters
% Run setoperationalmode after most of the AO is built so that the Units and Mode fields
% can be set in setoperationalmode

setao(AO);
setoperationalmode(OperationalMode);

