import aphla as ap

patch={'q1': {'k1': -12.38103029065561},
       'q2': {'k1': 13.05625044521254},
       'q3': {'k1': -4.291155182},
       'q1bd1': {'k1': -8.984411885820821},
       'q2bd1': {'k1': 7.98520609273425}
}



def convert_at_lattice(latname):
    oupt = []
    elems = ap.getElements('*')
    # remove the VCOR
    elems = [e for e in elems if e.family != 'VCOR']
    
    dft = {'name': None, 'sb': None, 'length': None,
           'atclass': 'drift', 'atfamily': 'HALFD'}
    for i,e in enumerate(elems):
        print i, "sb={0}".format(e.sb), "se={0}".format(e.se), e
        rec = {'name': e.name, 'family': e.family,
               'sb': e.sb, 'length': e.length,
               'atclass': 'marker', 'atfamily': e.family}
        
        if e.family in ['BPM', 'FLAG', 'ICT']:
            # name, family, new: (name, type, family)
            # 
            rec['sb'] = e.sb + e.length/2.0
            rec['length'] = 0.0
            rec['atfamily'] = e.family
            if rec['family'] == 'FLAG': rec['atfamily'] = 'SCREEN'
            if e.length > 0.0:
                dft['name'] = 'DHF_'+rec['name']
                dft['length'] = e.length/2.0
                dft['sb'] = e.sb
                print dft
                oupt.append(dft.copy())
                oupt.append(rec.copy())
                dft['sb'] = e.length/2.0 + e.sb
                oupt.append(dft.copy())
            else:
                oupt.append(rec)

        elif e.family in ['HCOR']:
            # assuming H/V in pair. named as 'c[xy]*'
            hvname = e.name[0] + e.name[2:]
            rec['name'] = hvname
            rec['atfamily'] = 'HVCM'
            rec['atclass'] = 'corrector'
            oupt.append(rec.copy())
        elif e.family in ['VCOR']:
            # handled in HCOR as HVCM
            raise RuntimeError("'VCOR' should be removed")
        elif e.family in ['QUAD']:
            rec['atclass'] = 'quadrupole'
            rec['k1'] = None
            oupt.append(rec.copy())
        else:
            print i,e
            raise RuntimeError("unrecognized type: {0}".format(e))
    return oupt

def at_definition(rec):
    name, cla = rec['name'], rec['atclass']
    L = rec['length']
    h = "%s = %s('%s'," % (name, cla, rec['atfamily'])
    if cla in ['marker']:
        return h + " 'IdentityPass');"
    elif cla in ['drift']:
        return h+" {0}, 'DriftPass');".format(rec['length'])
    elif cla in ['corrector']:
        return h+" {0}, [0 0], 'CorrectorPass');".format(L)
    elif cla in ['quadrupole']:
        k1 = rec['k1']
        if k1 is None: k1 = patch[name]['k1']
        return h+" {0}, {1}, 'StrMPoleSymplectic4Pass');".format(
            L, k1)
    else:
        raise RuntimeError("unknown AT type '%s'" % cla)
    
def export_at_lattice(fname, latname):
    lat = convert_at_lattice(latname)
    for i,e in enumerate(lat):
        print i, e
    oupt = open(fname, 'w')
    oupt.write("""function varargout = %slattice(varargin)

global THERING 

if nargin >=1
   Energy = varargin{1};
else
  Energy = 200e6;
end\n\n

%%BEG_ = marker('BEG', 'IdentityPass');\n
""" % (latname.lower(),))

    rdft = {'name': None, 'length': 0.0, 'sb': 0.0,
            'atclass': 'drift', 'atfamily': 'DRIFT'}
    elems, s = [], 0.0
    for i,r in enumerate(lat):
        if r is None: continue
        # append drift if there is space
        if r['sb'] > s:
            rdft['length'] = r['sb'] - s
            rdft['name'] = 'D_%d_%s' % (i, r['name'])
            oupt.write(at_definition(rdft) + "\n")
            elems.append(rdft['name'])
            s += rdft['length']

        oupt.write(at_definition(r) + " %s= {0}\n".format(s))
        s += r['length']
        print i, s, r['length'], r['name']
        elems.append(r['name'])

    oupt.write("L%s= [" % latname)
    oupt.write(' '.join(elems))
    oupt.write("];\n")
    oupt.write("""\nbuildlat(L%s);
THERING = setcellstruct(THERING, 'Energy', 1:length(THERING), Energy);

for i=1:length(THERING),
    s = findspos(THERING, i+1);
  fprintf('%%s L=%%f, s=%%f\\n', THERING{i}.FamName, THERING{i}.Length, s);
end

L0 = findspos(THERING, length(THERING)+1);
fprintf('   Total Length = %%.6f meters  \\n', L0)
""" % (latname,))

    oupt.close()


def export_mml_init(fname, latname):
    oupt = open(fname, 'w')
    oupt.write("""function %sinit(varargin)

if nargin < 1
   OperationalMode = 1;
end

setao([]);

""" % (latname.lower(),))

    bpms = ap.getElements('BPM')

    bpmx_devlist = "; ".join(['1 %d' % i for i in range(1, len(bpms)+1)])
    bpmx_commonnames = ";".join(["'%s'" % e.name for e in bpms])
    bpmy_commonnames = ";".join(["'%s'" % e.name for e in bpms])
    bpmx_monitor_pv = ";".join(["'%s'" % e.pv(field='x')[0] for e in bpms])
    bpmy_monitor_pv = ";".join(["'%s'" % e.pv(field='x')[0] for e in bpms])
    # fake
    bpmx_sum_pv = ";".join(["'pv1'" for i in range(len(bpms))])
    bpmy_sum_pv = ";".join(["'pv1'" for i in range(len(bpms))])

    hcms = ap.getElements('HCOR')
    for i,e in enumerate(hcms):
        print i, e, e.pv(field='x', handle='readback')
    hcm_devlist = "; ".join(['1 %d' % i for i in range(1, len(hcms)+1)])
    hcm_commonnames = ";".join(["'% 6s'" % e.name for e in hcms])
    hcm_monitor_pv =  ";".join(["'%s'" % e.pv(field='x', handle='readback')[0] for e in hcms])
    hcm_setpoint_pv =  ";".join(["'%s'" % e.pv(field='x', handle='setpoint')[0] for e in hcms])
    hcm_oncontrol_pv = ";".join(["'fakepv'" for i in range(len(hcms))])
    hcm_fault_pv = ";".join(["'fakepv'" for i in range(len(hcms))])

    vcms = ap.getElements('VCOR')
    vcm_devlist = "; ".join(['1 %d' % i for i in range(1, len(vcms)+1)])
    vcm_commonnames = ";".join(["'% 6s'" % e.name for e in vcms])
    vcm_monitor_pv =  ";".join(["'%s'" % e.pv(field='y', handle='readback')[0] for e in vcms])
    vcm_setpoint_pv =  ";".join(["'%s'" % e.pv(field='y', handle='setpoint')[0] for e in vcms])
    vcm_oncontrol_pv = ";".join(["'fakepv'" for i in range(len(vcms))])
    vcm_fault_pv = ";".join(["'fakepv'" for i in range(len(vcms))])

    quads = ap.getElements('QUAD')
    q_devlist = "; ".join(['1 %d' % i for i in range(1, len(quads)+1)])
    q_commonnames = ";".join(["'% 5s'" % e.name for e in quads])
    q_monitor_pv =  ";".join(["'%s'" % e.pv(field='k1', handle='readback')[0] for e in quads])
    q_setpoint_pv =  ";".join(["'%s'" % e.pv(field='k1', handle='setpoint')[0] for e in quads])
    q_oncontrol_pv = ";".join(["'fakepv'" for i in range(len(quads))])
    q_fault_pv = ";".join(["'fakepv'" for i in range(len(quads))])

    screens = ap.getElements('FLAG')
    screen_devlist = "; ".join(['1 %d' % i for i in range(1, len(screens)+1)])
    screen_commonnames = ";".join(["'% 6s'" % e.name for e in screens])

    aodict = {'bpmx_devlist': bpmx_devlist,
              'bpmx_commonnames': bpmx_commonnames,
              'bpmy_commonnames': bpmy_commonnames,
              'bpmx_monitor_pv': bpmx_monitor_pv,
              'bpmy_monitor_pv': bpmy_monitor_pv,
              'bpmx_sum_pv': bpmx_sum_pv,
              'bpmy_sum_pv': bpmy_sum_pv,
              'hcm_devlist': hcm_devlist,
              'hcm_commonnames': hcm_commonnames,
              'hcm_monitor_pv': hcm_monitor_pv,
              'hcm_setpoint_pv': hcm_setpoint_pv,
              'hcm_oncontrol_pv': hcm_oncontrol_pv,
              'hcm_fault_pv': hcm_fault_pv,
              'vcm_devlist': vcm_devlist,
              'vcm_commonnames': vcm_commonnames,
              'vcm_monitor_pv': vcm_monitor_pv,
              'vcm_setpoint_pv': vcm_setpoint_pv,
              'vcm_oncontrol_pv': vcm_oncontrol_pv,
              'vcm_fault_pv': vcm_fault_pv,
              'q_devlist': q_devlist,
              'q_commonnames': q_commonnames,
              'q_monitor_pv': q_monitor_pv,
              'q_setpoint_pv': q_setpoint_pv,
              'q_oncontrol_pv': q_oncontrol_pv,
              'q_fault_pv': q_fault_pv,
              'screen_devlist': screen_devlist,
              'screen_commonnames': screen_commonnames,
    }
    #print bpmx_commonnames
    #print bpmy_commonnames
    #print bpmx_monitor_pv
    #print bpmy_monitor_pv

    oupt.write(
"""
%% BPM
AO.BPMx.FamilyName  = 'BPMx';
AO.BPMx.MemberOf    = {'BPM'; 'BPMx';};
AO.BPMx.DeviceList  = [ %(bpmx_devlist)s ];
AO.BPMx.ElementList = (1:size(AO.BPMx.DeviceList,1))';
AO.BPMx.Status      = ones(size(AO.BPMx.DeviceList,1),1);
AO.BPMx.Position    = [];
AO.BPMx.CommonNames = [%(bpmx_commonnames)s];

AO.BPMx.Monitor.MemberOf = {'PlotFamily'; 'BPM'; 'BPMx'; 'Monitor'; 'Save';};
AO.BPMx.Monitor.Mode = 'Simulator';
AO.BPMx.Monitor.DataType = 'Scalar';
AO.BPMx.Monitor.ChannelNames = { %(bpmx_monitor_pv)s; ''};

AO.BPMx.Monitor.HW2PhysicsParams = 1e-3;  %% HW [mm], Simulator [Meters]
AO.BPMx.Monitor.Physics2HWParams = 1000;
AO.BPMx.Monitor.Units            = 'Hardware';
AO.BPMx.Monitor.HWUnits          = 'mm';
AO.BPMx.Monitor.PhysicsUnits     = 'Meter';
%%AO.BPMx.Monitor.SpecialFunctionGet = @getx_ltb;

AO.BPMx.Sum.MemberOf = {'PlotFamily'; 'BPM'; 'BPMx'; 'Monitor'; 'Sum';};
AO.BPMx.Sum.Mode = 'Simulator';
AO.BPMx.Sum.DataType = 'Scalar';
AO.BPMx.Sum.ChannelNames = { %(bpmx_sum_pv)s };

AO.BPMx.Sum.HW2PhysicsParams = 1;  %% HW [Volts], Simulator [Volts]
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
AO.BPMy.CommonNames = [ %(bpmy_commonnames)s ];

AO.BPMy.Monitor.MemberOf = {'PlotFamily'; 'BPM'; 'BPMy'; 'Monitor'; 'Save';};
AO.BPMy.Monitor.Mode = 'Simulator';
AO.BPMy.Monitor.DataType = 'Scalar';
AO.BPMy.Monitor.ChannelNames = { %(bpmy_monitor_pv)s };

AO.BPMy.Monitor.HW2PhysicsParams = 1e-3;  %% HW [mm], Simulator [Meters]
AO.BPMy.Monitor.Physics2HWParams = 1000;
AO.BPMy.Monitor.Units            = 'Hardware';
AO.BPMy.Monitor.HWUnits          = 'mm';
AO.BPMy.Monitor.PhysicsUnits     = 'Meter';

AO.BPMy.Sum.MemberOf = {'PlotFamily'; 'BPM'; 'BPMy'; 'Monitor'; 'Sum';};
AO.BPMy.Sum.Mode = 'Simulator';
AO.BPMy.Sum.DataType = 'Scalar';
AO.BPMy.Sum.ChannelNames = { %(bpmy_sum_pv)s };

AO.BPMy.Sum.HW2PhysicsParams = 1;  %% HW [Volts], Simulator [Volts]
AO.BPMy.Sum.Physics2HWParams = 1;
AO.BPMy.Sum.Units            = 'Hardware';
AO.BPMy.Sum.HWUnits          = '';
AO.BPMy.Sum.PhysicsUnits     = '';


%% HCM
AO.HCM.FamilyName  = 'HCM';
AO.HCM.MemberOf    = {'HCM'; 'Magnet'; 'COR';};
AO.HCM.DeviceList  = [ %(hcm_devlist)s ];
AO.HCM.ElementList = (1:size(AO.HCM.DeviceList,1))';
AO.HCM.Status      = ones(size(AO.HCM.DeviceList,1),1);
AO.HCM.Position    = [];
AO.HCM.CommonNames = [ %(hcm_commonnames)s ];

AO.HCM.Monitor.MemberOf = {'HCM'; 'Magnet'; 'COR'; 'Monitor'; 'PlotFamily'; 'Save';};
AO.HCM.Monitor.Mode = 'Simulator';
AO.HCM.Monitor.DataType = 'Scalar';
AO.HCM.Monitor.ChannelNames = { %(hcm_monitor_pv)s };
AO.HCM.Monitor.HW2PhysicsFcn = @hw2at;
AO.HCM.Monitor.Physics2HWFcn = @at2hw;
AO.HCM.Monitor.Units        = 'Hardware';
AO.HCM.Monitor.HWUnits      = 'Ampere';
AO.HCM.Monitor.PhysicsUnits = 'Radian';
%%AO.HCM.Monitor.Real2RawFcn = @real2raw_ltb;
%%AO.HCM.Monitor.Raw2RealFcn = @raw2real_ltb;

AO.HCM.Setpoint.MemberOf = {'HCM'; 'Magnet'; 'COR'; 'Save/Restore'; 'Setpoint'};
AO.HCM.Setpoint.Mode = 'Simulator';
AO.HCM.Setpoint.DataType = 'Scalar';
AO.HCM.Setpoint.ChannelNames = { %(hcm_setpoint_pv)s };
AO.HCM.Setpoint.HW2PhysicsFcn = @hw2at;
AO.HCM.Setpoint.Physics2HWFcn = @at2hw;
AO.HCM.Setpoint.Units        = 'Hardware';
AO.HCM.Setpoint.HWUnits      = 'Ampere';
AO.HCM.Setpoint.PhysicsUnits = 'Radian';
AO.HCM.Setpoint.Range = [-3 3];
AO.HCM.Setpoint.Tolerance  = .1 * ones(length(AO.HCM.ElementList), 1);  %% Hardware units
AO.HCM.Setpoint.DeltaRespMat = 1;
%% AO.HCM.Setpoint.RampRate = 1;
%% AO.HCM.Setpoint.RunFlagFcn = @getrunflag_ltb;
%% AO.HCM.RampRate.MemberOf = {'HCM'; 'Magnet'; 'COR'; 'PlotFamily'; 'Save/Restore';};
%% AO.HCM.RampRate.Mode = 'Simulator';
%% AO.HCM.RampRate.DataType = 'Scalar';
%% AO.HCM.RampRate.ChannelNames = getname_ltb(AO.HCM.FamilyName, 'RampRate');
%% AO.HCM.RampRate.HW2PhysicsParams = 1;
%% AO.HCM.RampRate.Physics2HWParams = 1;
%% AO.HCM.RampRate.Units        = 'Hardware';
%% AO.HCM.RampRate.HWUnits      = 'Ampere/Second';
%% AO.HCM.RampRate.PhysicsUnits = 'Ampere/Second';

AO.HCM.OnControl.MemberOf = {'HCM'; 'Magnet'; 'COR'; 'PlotFamily'; 'Boolean Control';};
AO.HCM.OnControl.Mode = 'Simulator';
AO.HCM.OnControl.DataType = 'Scalar';
AO.HCM.OnControl.ChannelNames = { %(hcm_oncontrol_pv)s };

AO.HCM.OnControl.HW2PhysicsParams = 1;
AO.HCM.OnControl.Physics2HWParams = 1;

AO.HCM.OnControl.Units        = 'Hardware';
AO.HCM.OnControl.HWUnits      = '';
AO.HCM.OnControl.PhysicsUnits = '';
AO.HCM.OnControl.Range = [0 1];
%%AO.HCM.OnControl.SpecialFunctionSet = @setsp_OnControlMagnet;

%% AO.HCM.On.MemberOf = {'HCM'; 'Magnet'; 'COR'; 'PlotFamily'; 'Boolean Monitor';};
%% AO.HCM.On.Mode = 'Simulator';
%% AO.HCM.On.DataType = 'Scalar';
%% AO.HCM.On.ChannelNames = getname_ltb(AO.HCM.FamilyName, 'On');
%% AO.HCM.On.HW2PhysicsParams = 1;
%% AO.HCM.On.Physics2HWParams = 1;
%% AO.HCM.On.Units        = 'Hardware';
%% AO.HCM.On.HWUnits      = '';
%% AO.HCM.On.PhysicsUnits = '';

AO.HCM.Fault.MemberOf = {'HCM'; 'Magnet'; 'COR'; 'PlotFamily'; 'Boolean Monitor';};
AO.HCM.Fault.Mode = 'Simulator';
AO.HCM.Fault.DataType = 'Scalar';
AO.HCM.Fault.ChannelNames = { %(hcm_fault_pv)s };

AO.HCM.Fault.HW2PhysicsParams = 1;
AO.HCM.Fault.Physics2HWParams = 1;
AO.HCM.Fault.Units        = 'Hardware';
AO.HCM.Fault.HWUnits      = '';
AO.HCM.Fault.PhysicsUnits = '';


%% VCM
AO.VCM.FamilyName  = 'VCM';
AO.VCM.MemberOf    = {'VCM'; 'Magnet'; 'COR';};
AO.VCM.DeviceList  = AO.HCM.DeviceList;
AO.VCM.ElementList = (1:size(AO.VCM.DeviceList,1))';
AO.VCM.Status      = ones(size(AO.VCM.DeviceList,1),1);
AO.VCM.Position    = [];
AO.VCM.CommonNames = [ %(vcm_commonnames)s ];

AO.VCM.Monitor.MemberOf = {'VCM'; 'Magnet'; 'COR'; 'Monitor'; 'PlotFamily'; 'Save';};
AO.VCM.Monitor.Mode = 'Simulator';
AO.VCM.Monitor.DataType = 'Scalar';
AO.VCM.Monitor.ChannelNames = { %(vcm_monitor_pv)s };

AO.VCM.Monitor.HW2PhysicsFcn = @hw2at;
AO.VCM.Monitor.Physics2HWFcn = @at2hw;
AO.VCM.Monitor.Units        = 'Hardware';
AO.VCM.Monitor.HWUnits      = 'Ampere';
AO.VCM.Monitor.PhysicsUnits = 'Radian';
%%AO.VCM.Monitor.Real2RawFcn = @real2raw_ltb;
%%AO.VCM.Monitor.Raw2RealFcn = @raw2real_ltb;

AO.VCM.Setpoint.MemberOf = {'VCM'; 'Magnet'; 'COR'; 'Save/Restore'; 'Setpoint'};
AO.VCM.Setpoint.Mode = 'Simulator';
AO.VCM.Setpoint.DataType = 'Scalar';
AO.VCM.Setpoint.ChannelNames = { %(vcm_setpoint_pv)s };

AO.VCM.Setpoint.HW2PhysicsFcn = @hw2at;
AO.VCM.Setpoint.Physics2HWFcn = @at2hw;
AO.VCM.Setpoint.Units        = 'Hardware';
AO.VCM.Setpoint.HWUnits      = 'Ampere';
AO.VCM.Setpoint.PhysicsUnits = 'Radian';
AO.VCM.Setpoint.Range = [-3 3];
AO.VCM.Setpoint.Tolerance  = .1;
AO.VCM.Setpoint.DeltaRespMat = 1;
%%AO.VCM.Setpoint.RampRate = 1;
%%AO.VCM.Setpoint.RunFlagFcn = @getrunflag_ltb;

%% AO.VCM.RampRate.MemberOf = {'VCM'; 'Magnet'; 'COR'; 'PlotFamily'; 'Save/Restore';};
%% AO.VCM.RampRate.Mode = 'Simulator';
%% AO.VCM.RampRate.DataType = 'Scalar';
%% AO.VCM.RampRate.ChannelNames = getname_ltb(AO.VCM.FamilyName, 'RampRate');
%% AO.VCM.RampRate.HW2PhysicsParams = 1;
%% AO.VCM.RampRate.Physics2HWParams = 1;
%% AO.VCM.RampRate.Units        = 'Hardware';
%% AO.VCM.RampRate.HWUnits      = 'Ampere/Second';
%% AO.VCM.RampRate.PhysicsUnits = 'Ampere/Second';

AO.VCM.OnControl.MemberOf = {'VCM'; 'Magnet'; 'COR'; 'PlotFamily'; 'Boolean Control';};
AO.VCM.OnControl.Mode = 'Simulator';
AO.VCM.OnControl.DataType = 'Scalar';
AO.VCM.OnControl.ChannelNames = { %(vcm_oncontrol_pv)s };

AO.VCM.OnControl.HW2PhysicsParams = 1;
AO.VCM.OnControl.Physics2HWParams = 1;
AO.VCM.OnControl.Units        = 'Hardware';
AO.VCM.OnControl.HWUnits      = '';
AO.VCM.OnControl.PhysicsUnits = '';
AO.VCM.OnControl.Range = [0 1];
%%AO.VCM.OnControl.SpecialFunctionSet = @setsp_OnControlMagnet;

%% AO.VCM.On.MemberOf = {'VCM'; 'Magnet'; 'COR'; 'PlotFamily'; 'Boolean Monitor';};
%% AO.VCM.On.Mode = 'Simulator';
%% AO.VCM.On.DataType = 'Scalar';
%% AO.VCM.On.ChannelNames = {''}
%% AO.VCM.On.HW2PhysicsParams = 1;
%% AO.VCM.On.Physics2HWParams = 1;
%% AO.VCM.On.Units        = 'Hardware';
%% AO.VCM.On.HWUnits      = '';
%% AO.VCM.On.PhysicsUnits = '';

%% AO.VCM.Reset.MemberOf = {'VCM'; 'Magnet'; 'COR'; 'PlotFamily'; 'Boolean Control';};
%% AO.VCM.Reset.Mode = 'Simulator';
%% AO.VCM.Reset.DataType = 'Scalar';
%% AO.VCM.Reset.ChannelNames = {''}
%% AO.VCM.Reset.HW2PhysicsParams = 1;
%% AO.VCM.Reset.Physics2HWParams = 1;
%% AO.VCM.Reset.Units        = 'Hardware';
%% AO.VCM.Reset.HWUnits      = '';
%% AO.VCM.Reset.PhysicsUnits = '';
%% AO.VCM.Reset.Range = [0 1];

AO.VCM.Fault.MemberOf = {'VCM'; 'Magnet'; 'COR'; 'PlotFamily'; 'Boolean Monitor';};
AO.VCM.Fault.Mode = 'Simulator';
AO.VCM.Fault.DataType = 'Scalar';
AO.VCM.Fault.ChannelNames = { %(vcm_fault_pv)s };

AO.VCM.Fault.HW2PhysicsParams = 1;
AO.VCM.Fault.Physics2HWParams = 1;
AO.VCM.Fault.Units        = 'Hardware';
AO.VCM.Fault.HWUnits      = 'Second';
AO.VCM.Fault.PhysicsUnits = 'Second';



AO.Q.FamilyName = 'Q';
AO.Q.MemberOf   = {'QUAD';  'Magnet';};
AO.Q.DeviceList = [ %(q_devlist)s ];
AO.Q.ElementList = (1:size(AO.Q.DeviceList,1))';
AO.Q.Status = ones(size(AO.Q.DeviceList,1),1);
AO.Q.Position = [];
AO.Q.CommonNames = [ %(q_commonnames)s ];

AO.Q.Monitor.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Monitor'; 'Save';};
AO.Q.Monitor.Mode = 'Simulator';
AO.Q.Monitor.DataType = 'Scalar';
AO.Q.Monitor.ChannelNames = { %(q_monitor_pv)s };

AO.Q.Monitor.HW2PhysicsFcn = @hw2at;
AO.Q.Monitor.Physics2HWFcn = @at2hw;
AO.Q.Monitor.Units        = 'Hardware';
AO.Q.Monitor.HWUnits      = 'Ampere';
AO.Q.Monitor.PhysicsUnits = '1/Meter^2';
%%AO.Q.Monitor.Real2RawFcn = @real2raw_ltb;
%%AO.Q.Monitor.Raw2RealFcn = @raw2real_ltb;

AO.Q.Setpoint.MemberOf = {'QUAD'; 'Magnet'; 'Save/Restore'; 'Setpoint';};
AO.Q.Setpoint.Mode = 'Simulator';
AO.Q.Setpoint.DataType = 'Scalar';
AO.Q.Setpoint.ChannelNames = { %(q_setpoint_pv)s };

AO.Q.Setpoint.HW2PhysicsFcn = @hw2at;
AO.Q.Setpoint.Physics2HWFcn = @at2hw;
AO.Q.Setpoint.Units        = 'Hardware';
AO.Q.Setpoint.HWUnits      = 'Ampere';
AO.Q.Setpoint.PhysicsUnits = '1/Meter^2';
AO.Q.Setpoint.Range = [0 160];
AO.Q.Setpoint.Tolerance = .1;
AO.Q.Setpoint.DeltaRespMat = 1;
%%AO.Q.Setpoint.RampRate = .15;
%%AO.Q.Setpoint.RunFlagFcn = @getrunflag_ltb;

%% AO.Q.RampRate.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Save/Restore';};
%% AO.Q.RampRate.Mode = 'Simulator';
%% AO.Q.RampRate.DataType = 'Scalar';
%% AO.Q.RampRate.ChannelNames = getname_ltb('Q', 'RampRate');
%% AO.Q.RampRate.HW2PhysicsFcn = @hw2at;
%% AO.Q.RampRate.Physics2HWFcn = @at2hw;
%% AO.Q.RampRate.Units        = 'Hardware';
%% AO.Q.RampRate.HWUnits      = 'Ampere/Second';
%% AO.Q.RampRate.PhysicsUnits = 'Ampere/Second';
%%(what_is1)s

AO.Q.OnControl.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Control';};
AO.Q.OnControl.Mode = 'Simulator';
AO.Q.OnControl.DataType = 'Scalar';
AO.Q.OnControl.ChannelNames = { %(q_oncontrol_pv)s };

AO.Q.OnControl.HW2PhysicsParams = 1;
AO.Q.OnControl.Physics2HWParams = 1;
AO.Q.OnControl.Units        = 'Hardware';
AO.Q.OnControl.HWUnits      = '';
AO.Q.OnControl.PhysicsUnits = '';
AO.Q.OnControl.Range = [0 1];

%% AO.Q.On.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Monitor';};
%% AO.Q.On.Mode = 'Simulator';
%% AO.Q.On.DataType = 'Scalar';
%% AO.Q.On.ChannelNames = {''};
%% AO.Q.On.HW2PhysicsParams = 1;
%% AO.Q.On.Physics2HWParams = 1;
%% AO.Q.On.Units        = 'Hardware';
%% AO.Q.On.HWUnits      = '';
%% AO.Q.On.PhysicsUnits = '';

%% AO.Q.Reset.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Control';};
%% AO.Q.Reset.Mode = 'Simulator';
%% AO.Q.Reset.DataType = 'Scalar';
%% AO.Q.Reset.ChannelNames = {''};
%% AO.Q.Reset.HW2PhysicsParams = 1;
%% AO.Q.Reset.Physics2HWParams = 1;
%% AO.Q.Reset.Units        = 'Hardware';
%% AO.Q.Reset.HWUnits      = '';
%% AO.Q.Reset.PhysicsUnits = '';
%% AO.Q.Reset.Range = [0 1];

AO.Q.Fault.MemberOf = {'QUAD'; 'Magnet'; 'PlotFamily'; 'Boolean Monitor';};
AO.Q.Fault.Mode = 'Simulator';
AO.Q.Fault.DataType = 'Scalar';
AO.Q.Fault.ChannelNames = { %(q_fault_pv)s };

AO.Q.Fault.HW2PhysicsParams = 1;
AO.Q.Fault.Physics2HWParams = 1;
AO.Q.Fault.Units        = 'Hardware';
AO.Q.Fault.HWUnits      = '';
AO.Q.Fault.PhysicsUnits = '';



%%AO.BEND.FamilyName = 'BEND';
%%AO.BEND.MemberOf   = {'BEND'; 'Magnet'};
%%AO.BEND.DeviceList = [1 1; 1 2; 1 3; 1 4;];
%%AO.BEND.ElementList = (1:size(AO.BEND.DeviceList,1))';
%%AO.BEND.Status = ones(size(AO.BEND.DeviceList,1),1);
%% AO.BEND.Position = [];
%% AO.BEND.CommonNames = [ 
%%    'BEND1'
%%    'BEND2'
%%    'BEND3'
%%    'BEND4'
%%    ];

%% AO.BEND.Monitor.MemberOf = {'BEND'; 'Magnet'; 'PlotFamily'; 'Monitor'; 'Save';};
%% AO.BEND.Monitor.Mode = 'Simulator';
%% AO.BEND.Monitor.DataType = 'Scalar';
%% AO.BEND.Monitor.ChannelNames = {
%%    'LTB-MG{Bend:1}I:Ps1DCCT1-I'
%%    'LTB-MG{Bend:2}I:Ps1DCCT1-I'
%%    'LTB-MG{Bend:3}I:Ps1DCCT1-I'
%%    'LTB-MG{Bend:4}I:Ps1DCCT1-I'
%%    };
%% AO.BEND.Monitor.HW2PhysicsFcn = @hw2at;
%% AO.BEND.Monitor.Physics2HWFcn = @at2hw;
%% AO.BEND.Monitor.Units        = 'Hardware';
%% AO.BEND.Monitor.HWUnits      = 'Ampere';
%% AO.BEND.Monitor.PhysicsUnits = 'Radian';
%%%% AO.BEND.Monitor.Real2RawFcn = @real2raw_ltb;
%%%% AO.BEND.Monitor.Raw2RealFcn = @raw2real_ltb;

%% AO.BEND.Setpoint.MemberOf = {'BEND'; 'Magnet'; 'Save/Restore'; 'Setpoint';};
%% AO.BEND.Setpoint.Mode = 'Simulator';
%% AO.BEND.Setpoint.DataType = 'Scalar';
%% AO.BEND.Setpoint.ChannelNames = {
%%    'LTB-MG{Bend:1}I:Sp1-SP'
%%    'LTB-MG{Bend:2}I:Sp1-SP'
%%    'LTB-MG{Bend:3}I:Sp1-SP'
%%    'LTB-MG{Bend:4}I:Sp1-SP'
%%    };
%% AO.BEND.Setpoint.HW2PhysicsFcn = @hw2at;
%% AO.BEND.Setpoint.Physics2HWFcn = @at2hw;
%% AO.BEND.Setpoint.Units        = 'Hardware';
%% AO.BEND.Setpoint.HWUnits      = 'Ampere';
%% AO.BEND.Setpoint.PhysicsUnits = 'Radian';
%% AO.BEND.Setpoint.Range = [0 110];
%% AO.BEND.Setpoint.Tolerance = .1;  %% Hardware units
%%%% AO.BEND.Setpoint.RampRate = 1;
%%%% AO.BEND.Setpoint.RunFlagFcn = @getrunflag_ltb;

%% %% AO.BEND.RampRate.MemberOf = {'BEND'; 'Magnet'; 'PlotFamily'; 'Save/Restore';};
%% %% AO.BEND.RampRate.Mode = 'Simulator';
%% %% AO.BEND.RampRate.DataType = 'Scalar';
%% %% AO.BEND.RampRate.ChannelNames = getname_ltb(%% AO.BEND.FamilyName, 'RampRate');
%% %% AO.BEND.RampRate.HW2PhysicsParams = 1;
%% %% AO.BEND.RampRate.Physics2HWParams = 1;
%% %% AO.BEND.RampRate.Units        = 'Hardware';
%% %% AO.BEND.RampRate.HWUnits      = 'Ampere/Second';
%% %% AO.BEND.RampRate.PhysicsUnits = 'Ampere/Second';

%% AO.BEND.OnControl.MemberOf = {'BEND'; 'Magnet'; 'PlotFamily'; 'Boolean Control';};
%% AO.BEND.OnControl.Mode = 'Simulator';
%% AO.BEND.OnControl.DataType = 'Scalar';
%% AO.BEND.OnControl.ChannelNames = {
%%    'LTB-MG{Bend:1}PsOnOff-Sel'
%%    'LTB-MG{Bend:2}PsOnOff-Sel'
%%    'LTB-MG{Bend:3}PsOnOff-Sel'
%%    'LTB-MG{Bend:4}PsOnOff-Sel'
%%    };
%% AO.BEND.OnControl.HW2PhysicsParams = 1;
%% AO.BEND.OnControl.Physics2HWParams = 1;
%% AO.BEND.OnControl.Units        = 'Hardware';
%% AO.BEND.OnControl.HWUnits      = '';
%% AO.BEND.OnControl.PhysicsUnits = '';
%% AO.BEND.OnControl.Range = [0 1];
%% AO.BEND.OnControl.SpecialFunctionSet = @setsp_OnControlMagnet;

%% AO.BEND.On.MemberOf = {'BEND'; 'Magnet'; 'PlotFamily'; 'Boolean Monitor';};
%% AO.BEND.On.Mode = 'Simulator';
%% AO.BEND.On.DataType = 'Scalar';
%% AO.BEND.On.ChannelNames = getname_ltb(AO.BEND.FamilyName, 'On');
%% AO.BEND.On.HW2PhysicsParams = 1;
%% AO.BEND.On.Physics2HWParams = 1;
%% AO.BEND.On.Units        = 'Hardware';
%% AO.BEND.On.HWUnits      = '';
%% AO.BEND.On.PhysicsUnits = '';

%% AO.BEND.Reset.MemberOf = {'BEND'; 'Magnet'; 'PlotFamily'; 'Boolean Control';};
%% AO.BEND.Reset.Mode = 'Simulator';
%% AO.BEND.Reset.DataType = 'Scalar';
%% AO.BEND.Reset.ChannelNames = getname_ltb(AO.BEND.FamilyName, 'Reset');
%% AO.BEND.Reset.HW2PhysicsParams = 1;
%% AO.BEND.Reset.Physics2HWParams = 1;
%% AO.BEND.Reset.Units        = 'Hardware';
%% AO.BEND.Reset.HWUnits      = '';
%% AO.BEND.Reset.PhysicsUnits = '';
%% AO.BEND.Reset.Range = [0 1];

%%AO.BEND.Fault.MemberOf = {'BEND'; 'Magnet'; 'PlotFamily'; 'Boolean Monitor';};
%%AO.BEND.Fault.Mode = 'Simulator';
%%AO.BEND.Fault.DataType = 'Scalar';
%%AO.BEND.Fault.ChannelNames = {
%%    'LTB-MG{Bend:1}Sum1-Sts'
%%    'LTB-MG{Bend:2}Sum1-Sts'
%%    'LTB-MG{Bend:3}Sum1-Sts'
%%    'LTB-MG{Bend:4}Sum1-Sts'
%%    };
%%AO.BEND.Fault.HW2PhysicsParams = 1;
%%AO.BEND.Fault.Physics2HWParams = 1;
%%AO.BEND.Fault.Units        = 'Hardware';
%%AO.BEND.Fault.HWUnits      = '';
%%AO.BEND.Fault.PhysicsUnits = '';


%% Screen
AO.Screen.FamilyName = 'Screen';
AO.Screen.MemberOf = {'PlotFamily'; 'Screen';};
AO.Screen.DeviceList = [ %(screen_devlist)s ];
AO.Screen.ElementList = (1:size(AO.Screen.DeviceList,1))';
AO.Screen.Status = ones(size(AO.Screen.DeviceList,1),1);
AO.Screen.Position = (1:size(AO.Screen.DeviceList,1))';
AO.Screen.CommonNames = [ %(screen_commonnames)s ];

AO.Screen.Monitor.MemberOf = {'PlotFamily';  'Boolean Monitor';};
AO.Screen.Monitor.Mode = 'Simulator';
AO.Screen.Monitor.DataType = 'Scalar';
AO.Screen.Monitor.ChannelNames = {''};
AO.Screen.Monitor.HW2PhysicsParams = 1;
AO.Screen.Monitor.Physics2HWParams = 1;
AO.Screen.Monitor.Units        = 'Hardware';
AO.Screen.Monitor.HWUnits      = '';
AO.Screen.Monitor.PhysicsUnits = '';

AO.Screen.Setpoint.MemberOf = {'Screen'; 'Boolean Control';};
AO.Screen.Setpoint.Mode = 'Simulator';
AO.Screen.Setpoint.DataType = 'Scalar';
AO.Screen.Setpoint.ChannelNames = {''};
AO.Screen.Setpoint.HW2PhysicsParams = 1;
AO.Screen.Setpoint.Physics2HWParams = 1;
AO.Screen.Setpoint.Units        = 'Hardware';
AO.Screen.Setpoint.HWUnits      = '';
AO.Screen.Setpoint.PhysicsUnits = '';
AO.Screen.Setpoint.Range = [0 1];
AO.Screen.Setpoint.Tolerance = .5 * ones(length(AO.Screen.ElementList), 1);  %% Hardware units
%%AO.Screen.Setpoint.SpecialFunctionGet = @getScreen;
%%AO.Screen.Setpoint.SpecialFunctionSet = @setScreen;

%% AO.Screen.InControl.MemberOf = {'PlotFamily'; 'Boolean Control';};
%% AO.Screen.InControl.Mode = 'Simulator';
%% AO.Screen.InControl.DataType = 'Scalar';
%% AO.Screen.InControl.ChannelNames = {''};
%% AO.Screen.InControl.HW2PhysicsParams = 1;
%% AO.Screen.InControl.Physics2HWParams = 1;
%% AO.Screen.InControl.Units        = 'Hardware';
%% AO.Screen.InControl.HWUnits      = '';
%% AO.Screen.InControl.PhysicsUnits = '';
%% AO.Screen.InControl.Range = [0 1];
%%
%% AO.Screen.In.MemberOf = {'PlotFamily'; 'Boolean Monitor';};
%% AO.Screen.In.Mode = 'Simulator';
%% AO.Screen.In.DataType = 'Scalar';
%% AO.Screen.In.ChannelNames = {''};
%% AO.Screen.In.HW2PhysicsParams = 1;
%% AO.Screen.In.Physics2HWParams = 1;
%% AO.Screen.In.Units        = 'Hardware';
%% AO.Screen.In.HWUnits      = '';
%% AO.Screen.In.PhysicsUnits = '';
%%
%% AO.Screen.Out.MemberOf = {'PlotFamily'; 'Boolean Monitor';};
%% AO.Screen.Out.Mode = 'Simulator';
%% AO.Screen.Out.DataType = 'Scalar';
%% AO.Screen.Out.ChannelNames = {''};
%% AO.Screen.Out.HW2PhysicsParams = 1;
%% AO.Screen.Out.Physics2HWParams = 1;
%% AO.Screen.Out.Units        = 'Hardware';
%% AO.Screen.Out.HWUnits      = '';
%% AO.Screen.Out.PhysicsUnits = '';



%% AO.Screen.LampControl.MemberOf = {'PlotFamily'; 'Boolean Control';};
%% AO.Screen.LampControl.Mode = 'Simulator';
%% AO.Screen.LampControl.DataType = 'Scalar';
%% AO.Screen.LampControl.ChannelNames = {''};
%% AO.Screen.LampControl.HW2PhysicsParams = 1;
%% AO.Screen.LampControl.Physics2HWParams = 1;
%% AO.Screen.LampControl.Units        = 'Hardware';
%% AO.Screen.LampControl.HWUnits      = '';
%% AO.Screen.LampControl.PhysicsUnits = '';
%% AO.Screen.LampControl.Range = [0 1];
%%
%% AO.Screen.Lamp.MemberOf = {'PlotFamily'; 'Boolean Monitor';};
%% AO.Screen.Lamp.Mode = 'Simulator';
%% AO.Screen.Lamp.DataType = 'Scalar';
%% AO.Screen.Lamp.ChannelNames = getname_ltb(AO.Screen.FamilyName, 'Lamp');
%% AO.Screen.Lamp.HW2PhysicsParams = 1;
%% AO.Screen.Lamp.Physics2HWParams = 1;
%% AO.Screen.Lamp.Units        = 'Hardware';
%% AO.Screen.Lamp.HWUnits      = '';
%% AO.Screen.Lamp.PhysicsUnits = '';


%% Save the AO so that family2dev will work
setao(AO);


%% The operational mode sets the path, filenames, and other important parameters
%% Run setoperationalmode after most of the AO is built so that the Units and Mode fields
%% can be set in setoperationalmode
setao(AO);
setoperationalmode(OperationalMode);

""" % aodict)
    oupt.close()


if __name__ == "__main__":
    ap.initNSLS2V2()
    latname = 'V1LTD1'

    # save the current lattice
    lat = ap.machines.getLattice()    
    # switch lattice
    ap.machines.use(latname)
    #overlapped = ap.machines._lat.getOverlapped()

    export_at_lattice("nsls2%s.m" % (latname.lower()), latname)
    export_mml_init("%sinit.m" % latname.lower(), latname)


    # restore
    ap.machines.use(lat)
