function updateatindex
%UPDATEATINDEX - Updates the AT indices in the MiddleLayer with the present AT lattice (THERING)


global THERING


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Append Accelerator Toolbox information %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Since changes in the AT model could change the AT indexes, etc,
% It's best to regenerate all the model indices whenever a model is loaded

% Sort by family first (findcells is linear and slow)
Indices = atindex(THERING);

AO = getao;


% BPMS
try
    AO.BPMx.AT.ATType = 'xTurns';
    AO.BPMx.AT.ATIndex = Indices.BPM(:); % findcells(THERING,'FamName','BPM')';
    AO.BPMx.Position = findspos(THERING, AO.BPMx.AT.ATIndex)';

    AO.BPMy.AT.ATType = 'yTurns';
    AO.BPMy.AT.ATIndex = Indices.BPM(:); % findcells(THERING,'FamName','BPM')';
    AO.BPMy.Position = findspos(THERING, AO.BPMy.AT.ATIndex)';
catch
    warning('BPM family not found in the model.');
end


% CORRECTORS
try
    % Horizontal correctors are at every AT corrector
    AO.HCM.AT.ATType = 'COR';
    AO.HCM.AT.ATIndex = buildatindex(AO.HCM.FamilyName, Indices.COR);
    AO.HCM.Position = findspos(THERING, AO.HCM.AT.ATIndex(:,1))';

    % Not all correctors are vertical correctors
    AO.VCM.AT.ATType = 'COR';
    AO.VCM.AT.ATIndex = buildatindex(AO.VCM.FamilyName, Indices.COR);
    AO.VCM.Position = findspos(THERING, AO.VCM.AT.ATIndex(:,1))';
catch
    warning('Corrector family not found in the model.');
end


% QUADRUPOLES
try
   %
    AO.QH1.AT.ATType = 'QH1';
    AO.QH1.AT.ATIndex = buildatindex(AO.QH1.FamilyName);
    AO.QH1.Position = findspos(THERING, AO.QH1.AT.ATIndex(:,1))';

    AO.QH2.AT.ATType = 'QH2';
    AO.QH2.AT.ATIndex = buildatindex(AO.QH2.FamilyName);
    AO.QH2.Position = findspos(THERING, AO.QH2.AT.ATIndex(:,1))';

    AO.QH3.AT.ATType = 'QH3';
    AO.QH3.AT.ATIndex = buildatindex(AO.QH3.FamilyName);
    AO.QH3.Position = findspos(THERING, AO.QH3.AT.ATIndex(:,1))';

    AO.QL1.AT.ATType = 'QL1';
    AO.QL1.AT.ATIndex = buildatindex(AO.QL1.FamilyName);
    AO.QL1.Position = findspos(THERING, AO.QL1.AT.ATIndex(:,1))';

    AO.QL2.AT.ATType = 'QL2';
    AO.QL2.AT.ATIndex = buildatindex(AO.QL2.FamilyName);
    AO.QL2.Position = findspos(THERING, AO.QL2.AT.ATIndex(:,1))';

    AO.QL3.AT.ATType = 'QL3';
    AO.QL3.AT.ATIndex = buildatindex(AO.QL3.FamilyName);
    AO.QL3.Position = findspos(THERING, AO.QL3.AT.ATIndex(:,1))';

    AO.QM1.AT.ATType = 'QM1';
    AO.QM1.AT.ATIndex = buildatindex(AO.QM1.FamilyName);
    AO.QM1.Position = findspos(THERING, AO.QM1.AT.ATIndex(:,1))';

    AO.QM2.AT.ATType = 'QM2';
    AO.QM2.AT.ATIndex = buildatindex(AO.QM2.FamilyName);
    AO.QM2.Position = findspos(THERING, AO.QM2.AT.ATIndex(:,1))';
catch
    warning('Q family not found in the model.');
end


% BEND
%try
%    AO.BEND.AT.ATType = 'BEND';
%    AO.BEND.AT.ATIndex = buildatindex(AO.BEND.FamilyName);
%    AO.BEND.Position = findspos(THERING, AO.BEND.AT.ATIndex(:,1))';
%catch
%    warning('BEND family not found in the model.');
%end


% SCREEN
%try
%    AO.Screen.AT.ATType = 'TV';
%    AO.Screen.AT.ATIndex = buildatindex(AO.Screen.FamilyName, Indices.SCREEN);
%    AO.Screen.Position = findspos(THERING, AO.Screen.AT.ATIndex(:,1))';
%catch
%    warning('Screen family not found in the model.');
%end

setao(AO);




% Set TwissData at the start
try
    % LTB twiss parameters at the input 
    TwissData.alpha = [-.5 -.6]';
    TwissData.beta  = [4.5 4.8]';
    TwissData.mu    = [0 0]';
    TwissData.ClosedOrbit = [0 0 0 0]';
    TwissData.dP = 0;
    TwissData.dL = 0;
    TwissData.Dispersion  = [0 0 0 0]';
    
    setpvmodel('TwissData', '', TwissData);  % Same as, THERING{1}.TwissData = TwissData;

    % Golden tune???
    %setpvmodel('TwissData', 'Tune', []); 

catch
     warning('Setting the twiss data parameters in the GTB MML failed.');
end

