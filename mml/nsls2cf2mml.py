import aphla as ap
from fnmatch import fnmatch

def patch(latname, elem, k, **kwargs):
    d={'V1LTD1': {'q1': {'k1': -12.38103029065561},
                  'q2': {'k1': 13.05625044521254},
                  'q3': {'k1': -4.291155182},
                  'q1bd1': {'k1': -8.984411885820821},
                  'q2bd1': {'k1': 7.98520609273425}
              },
       'V2SR': {"sl1g*c*[ab]": { "k2": -1.95754},
                "sl2g*c*[ab]": { "k2": 25.9682},
                "sl3g*c*[ab]": { "k2": -28.2618},
                "sm1g*c*a": { "k2": -24.131},
                "sm2g*c*[ab]": { "k2": 28.7157},
                "sm1g*c*b": { "k2": -26.0949},
                "sh4g*c*[ab]": { "k2": -20.4869},
                "sh3g*c*[ab]": { "k2": -4.1557},
                "sh1g*c*[ab]": { "k2": 24.1977},
                "ql1g*c*[ab]": { "k1": -1.56216},
                "ql2g*c*[ab]": { "k1": 1.81307},
                "ql3g*c*[ab]": { "k1": -1.48928},
                "sqmhg*c*a": { "k1": 0},
                "qm2g*c*[ab]": { "k1": 1.2223},
                "qm1g*c*[ab]": { "k1": -0.803148},
                "qh3g*c*[ab]": { "k1": -1.70755},
                "qh2g*c*[ab]": { "k1": 1.47765},
                "qh1g*c*[ab]": { "k1": -0.633004},
                "sqhhg*c*a": { "k1": 0},
                "qh2g*c*a": { "k1": 1.47765},
                "qh3g*c*a": { "k1": -1.70755},
            }
    }
    try:
        ret = d[latname][elem][k]
        return ret
    except:
        v = d[latname]
        for fam in v.keys():
            if fnmatch(elem, fam): 
                return v[fam][k]
    print "Did not find '%s.%s'" % (elem, k) 
    return k

def convert_at_lattice(latname):
    oupt = []
    elems = ap.getElements('*')
    # remove the VCOR
    # elems = [e for e in elems if e.family not in ['VCOR', 'VFCOR']]
    
    dft = {'name': None, 'sb': None, 'length': None,
           'atclass': 'drift', 'atfamily': 'HALFD'}
    for i,e in enumerate(elems):
        print i, "sb={0}".format(e.sb), "se={0}".format(e.se), e
        rec = {'name': e.name, 'family': e.family,
               'sb': e.sb, 'length': e.length,
               'atclass': 'marker', 'atfamily': e.family}
        
        if e.family in ['FLAG', 'ICT']:
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

        if e.family in ['BPM']:
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
        elif e.family in ['COR']:
            rec['name'] = e.name
            rec['atfamil'] = 'HVCOR'
            rec['atclass'] = 'corrector'
            oupt.append(rec.copy())            
        elif e.family in ['DIPOLE']:
            rec['atfamily'] = 'rbend'
        elif e.family in ['HCOR', 'HFCOR']:
            # assuming H/V in pair. named as 'c[xy]*'
            hvname = e.name[0] + e.name[2:]
            rec['name'] = hvname
            rec['atfamily'] = 'HVCM'
            rec['atclass'] = 'corrector'
            oupt.append(rec.copy())
        elif e.family in ['VCOR', 'VFCOR']:
            # handled in HCOR as HVCM
            raise RuntimeError("'VCOR' should be removed")
        elif e.family in ['QUAD', 'SQUAD']:
            rec['atclass'] = 'quadrupole'
            rec['k1'] = None
            oupt.append(rec.copy())
        elif e.family in ['SEXT']:
            rec['atclass'] = 'sextupole'
            rec['k2'] = None
            oupt.append(rec.copy())
        elif e.family in ['', None, 'DCCT']:
            pass
        elif e.family in ['HCOR_IDCU', 'VCOR_IDCU', 'HCOR_IDCS', 'VCOR_IDCS', 'INSERTION']:
            pass
        else:
            print i,e
            raise RuntimeError("unrecognized type '{0}': {1}".format(e.family, e))
    return oupt

def at_definition(latname, rec):
    """
    given a record, return an AT definition
    """
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
        if k1 is None: k1 = patch(latname, name, 'k1')
        return h+" {0}, {1}, 'StrMPoleSymplectic4Pass');".format(
            L, k1)
    elif cla in ['sextupole']:
        k2 = rec['k2']
        if k2 is None: k2 = patch(latname, name, 'k2')
        return h+" {0}, {1}, 'StrMPoleSymplectic4Pass');".format(
            L, k2/2.0)
    else:
        raise RuntimeError("unknown AT type '%s'" % cla)
    
def export_at_lattice(template, latname):
    lat = convert_at_lattice(latname)
    for i,e in enumerate(lat):
        print i, e
    fname = template[:-len('.template')]
    strtmpl = open(template, 'r').read()

    rdft = {'name': None, 'length': 0.0, 'sb': 0.0,
            'atclass': 'drift', 'atfamily': 'DRIFT'}
    elems, s, body = [], 0.0, ''
    for i,r in enumerate(lat):
        if r is None: continue
        # append drift if there is space
        if r['sb'] > s:
            rdft['length'] = r['sb'] - s
            rdft['name'] = 'D_%d_%s' % (i, r['name'])
            body += at_definition(latname, rdft) + "\n"
            elems.append(rdft['name'])
            s += rdft['length']
        try:
            body += at_definition(latname, r) + " %s= {0}\n".format(s)
            s += r['length']
        except:
            print i, s, r['length'], r['name']
            raise

        elems.append(r['name'])

    body += "L%s= [ %s ];\n" % (latname, ' '.join(elems))

    oupt = open(fname, 'w')
    oupt.write(strtmpl % { 'latname': latname, 'body':body})

    oupt.close()


def calc_devlist(elemlist):
    ret = []
    #
    for e in elemlist:
        # use C[0-9][0-9]
        ret.append([int(e.cell[1:])])

    ret[0].append(1)
    k = 1
    for i in range(1, len(ret)):
        k = k + 1
        if ret[i][0] != ret[i-1][0]: k = 1
        ret[i].append(k)
    return ret

def export_mml_init(template, latname):
    fmain = open(template['main'][:-len('.template')], 'w')
    ao_main = open(template['main'], 'r').read()

    bpms = ap.getElements('BPM')

    bpmx_devlist = "; ".join(['%d %d' % (v[0], v[1]) for v in calc_devlist(bpms)])
    bpmx_commonnames = ";".join(["'% 8s'" % e.name for e in bpms])
    bpmy_commonnames = ";".join(["'% 8s'" % e.name for e in bpms])
    bpmx_monitor_pv = ";".join(["'%s'" % e.pv(field='x')[0] for e in bpms])
    bpmy_monitor_pv = ";".join(["'%s'" % e.pv(field='x')[0] for e in bpms])
    # fake
    bpmx_sum_pv = ";".join(["'pv1'" for i in range(len(bpms))])
    bpmy_sum_pv = ";".join(["'pv1'" for i in range(len(bpms))])

    ao_bpm = open(template['bpm'], 'r').read() % {
        'bpmx_devlist': bpmx_devlist,
        'bpmx_commonnames': bpmx_commonnames,
        'bpmy_commonnames': bpmy_commonnames,
        'bpmx_monitor_pv': bpmx_monitor_pv,
        'bpmy_monitor_pv': bpmy_monitor_pv,
        'bpmx_sum_pv': bpmx_sum_pv,
        'bpmy_sum_pv': bpmy_sum_pv}
    
    hvcms = ap.getElements('COR')
    #for i,e in enumerate(hcms):
    #    print i, e, e.pv(field='x', handle='readback')
    hcm_devlist = "; ".join(['%d %d' % (v[0], v[1]) for v in calc_devlist(hvcms)])
    hcm_commonnames = ";".join(["'% 8s'" % e.name for e in hvcms])
    hcm_monitor_pv =  ";".join(["'%s'" % e.pv(field='x', handle='readback')[0] for e in hvcms])
    hcm_setpoint_pv =  ";".join(["'%s'" % e.pv(field='x', handle='setpoint')[0] for e in hvcms])
    hcm_oncontrol_pv = ";".join(["'fakepv'" for i in range(len(hvcms))])
    hcm_fault_pv = ";".join(["'fakepv'" for i in range(len(hvcms))])

    vcm_devlist = "; ".join(['%s %d' % (e.cell[1:], i+1) for i,e in enumerate(hvcms)])
    vcm_commonnames = ";".join(["'% 8s'" % e.name for e in hvcms])
    vcm_monitor_pv =  ";".join(["'%s'" % e.pv(field='y', handle='readback')[0] for e in hvcms])
    vcm_setpoint_pv =  ";".join(["'%s'" % e.pv(field='y', handle='setpoint')[0] for e in hvcms])
    vcm_oncontrol_pv = ";".join(["'fakepv'" for i in range(len(hvcms))])
    vcm_fault_pv = ";".join(["'fakepv'" for i in range(len(hvcms))])

    ao_hvcm = open(template['hvcm'], 'r').read() % {
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
        'vcm_fault_pv': vcm_fault_pv}

    fmain.write(ao_main % {
        'ao_bpm': ao_bpm,
        'ao_hvcm': ao_hvcm,
        'ao_q': ''})

    fmain.close()
    return

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

    oupt = open(fname, 'w')
    oupt.write( open(template, 'r').read() % aodict)
    oupt.close()


if __name__ == "__main__":
    ap.machines.init("nsls2v2")

    # save the current lattice
    lat = ap.machines.getLattice()    

    ## switch lattice
    #latname = 'V1LTD1'
    #ap.machines.use(latname)
    #export_at_lattice("nsls2v1ltd1.m.template", latname)
    #export_mml_init("v1ltd1init.m.template", latname)

    latname = 'V2SR'
    ap.machines.use(latname)
    export_at_lattice("nsls2v2sr.m.template", latname)
    templates = {'main': "v2srinit.m.template", 
                 'bpm': "v2srinit_ao_bpm.m.template", 
                 'hvcm': "v2srinit_ao_hvcm.m.template", 
                 'quad': "v2srinit_ao_q.m.template"}

    export_mml_init(templates, latname)

    # restore
    ap.machines.use(lat)
