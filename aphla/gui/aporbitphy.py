"""
Physics Routines for aporbit
============================

"""
import numpy as np
import aphla as ap

from PyQt4.QtCore import QObject, Qt, QSettings, QSize, QString, QThread, SIGNAL
from PyQt4.QtGui import QApplication, QBrush, QMdiArea, QMessageBox, QPen, QDialog
import PyQt4.Qwt5 as Qwt

from elempickdlg import ElementPickDlg
from orbitcorrdlg import OrbitCorrDlg
from aporbitplot import ApOrbitPlot, ApPlot, DcctCurrentPlot, ApPlotWidget, ApMdiSubPlot
from apbba import ApBbaDlg
import cothread
import time
import logging
_logger = logging.getLogger(__name__)

class ApMachInitThread(QThread):
    def __init__(self, mach, lat):
        super(ApMachInitThread, self).__init__()
        self.mach = mach
        self.latname = lat

    def run(self):
        #
        # Note: logging is not recommended: Cross Thread signal.
        # 
        print "initializing ", self.mach, self.latname
        #_logger.info("background initializing {0}.{1}".format(
        #    self.mach, self.latname))

        ap.machines.load(self.mach)
        #print "initialized ", self.mach, self.latname
        if self.latname: ap.machines.use(self.latname)
        else: self.latname = ap.machines.getLattice().name
        #_logger.info("initialized {0}, using {1}".format(
        #    self.mach, self.latname))
        # send the signal to caller thread
        elems = ap.getElements("*")
        pvs = []
        for e in elems: pvs.extend(e.pv())
        #mons = ap.catools.ct.connect(pvs, wait=False)
        cothread.Callback(self._connect_pvs, pvs)
        self.emit(SIGNAL("initialized(PyQt_PyObject)"), 
                  (self.mach, self.latname))
        #print "signal sent"

    def _connect_pvs(self, pvs):
        #cothread.catools.connect(pvs, timeout = 8)
        ap.catools.ct.caget(pvs)
        self.emit(SIGNAL("connected(PyQt_PyObject)"), "%d" % len(pvs))



class ApOrbitPhysics:
    def __init__(self, mdiarea):
        self.mdiarea = mdiarea
        self.deadelems = set()
        self.corbitdlg = None # orbit correction dlg
        self.bbadlg = None
        pass

    def close(self):
        if self.corbitdlg: self.corbitdlg.close()
        if self.bbadlg: self.bbadlg.close()

    def updateDeadElementPlots(self):
        for w in self.mdiarea.subWindowList():
            for e in self.deadelems:
                if e.name not in w.data.names(): continue
                w.data.disable(e.name)

        
    def chooseElement(self, fam):
        elems = ap.getElements(fam)
        form = ElementPickDlg(elems, self.deadelems, fam)

        if form.exec_(): 
            choice = form.result()
            deadlst = []
            for i in range(len(elems)):
                if elems[i].name in choice: continue
                deadlst.append(elems[i])
            # do nothing if dead element list did not change
            if set(deadlst) == self.deadelems: return
            self.deadelems = set(deadlst)

        _logger.info("{0} {1} '{2}' are disabled".format(
                len(deadlst), fam, [e.name for e in deadlst]))
        self.updateDeadElementPlots()

    def elementChecked(self, elem, stat):
        #print "element state:", elem, stat
        if stat == False and elem not in self.deadelems:
            self.deadelems.add(elem)
            _logger.info("'%s' is disabled" % elem.name)
        elif stat == True and elem in self.deadelems:
            self.deadelems.add(elem)
            _logger.info("'%s' is enabled" % elem.name)
        self.updateDeadElementPlots()

    def correctOrbit(self, **kwargs):
        """
        """
        # use the current aphla lattice
        bpms = kwargs.get('bpms', None)
        if bpms is None:
            bpms = [e for e in ap.getElements('BPM') 
                    if e not in self.deadelems]
        trims = kwargs.get('trims', None)
        if trims is None:
            alltrims = set(ap.getElements('HCOR') + ap.getElements('VCOR'))
            trims = [e for e in alltrims if e not in self.deadelems]
        obt = kwargs.get('obt', None)
        if obt is None:
            obt = [[0.0, 0.0] for i in range(len(bpms))]

        _logger.info("corrector orbit with BPM {0}/{1}, COR {2}/{3}".format(
                len(bpms), len(ap.getElements('BPM')),
                len(trims), len(alltrims)))

        repeat = kwargs.pop("repeat", 1)
        kwargs['verbose'] = 0
        # use 1.0 if not set scaling the kicker strength
        kwargs.setdefault('scale', 1.0)
        kwargs['dead'] = list(self.deadelems)
        for i in range(repeat):
            _logger.info("setting a local bump")
            QApplication.processEvents()
            ret = ap.setLocalBump(bpms, trims, obt, **kwargs)
            if ret[0] != 0:
                _logger.error(ret[1])
                break

        #return sp0

        #try:
        #    ap.setLocalBump(bpms, trims, obt)
        #except Exception as e:
        #    QMessageBox.warning(self, "Error:", " {0}".format(e))

    def createLocalBump(self, wx, wy):
        """create local bump"""
        if self.corbitdlg is None:
            #print self.obtdata.elem_names
            # assuming BPM has both x and y, the following s are same
            s, x, xe = wx.data.data(nomask=True)
            s, y, ye = wy.data.data(nomask=True)
            x, y = [0.0]*len(s), [0.0] * len(s)
            xunit = wx.data.yunit
            yunit = wy.data.yunit
            #print np.shape(x), np.shape(y)
            self.corbitdlg = OrbitCorrDlg(
                ap.getElements(wx.data.names()), 
                s, x, y, xunit = xunit, yunit=yunit,
                stepsize = 200e-6, 
                orbit_plots=(wx, wy),
                correct_orbit = self.correctOrbit)
            self.corbitdlg.resize(600, 500)
            self.corbitdlg.setWindowTitle("Create Local Bump")
            #self.connect(self.corbitdlg, SIGNAL("finished(int)"),
            #             self.plot1.curve2.setVisible)
            #self.obtxplot.plotDesiredOrbit(self.orbitx_data.golden(), 
            #                            self.orbitx_data.x)
            #self.obtyplot.plotDesiredOrbit(self.orbity_data.golden(), 
            #                            self.orbity_data.x)

        self.corbitdlg.show()
        self.corbitdlg.raise_()
        self.corbitdlg.activateWindow()

    def measBeta(self):
        p = ApMdiSubPlot(live=False)
        p.setAttribute(Qt.WA_DeleteOnClose)
        curves = [p.aplot.curve1, p.aplot.addCurve(),  # x and xref
                  p.aplot.addCurve(), p.aplot.addCurve() # y and yref
                  ]
        for curv in curves: curv.setStyle(Qwt.QwtPlotCurve.Lines)
        curves[0].setPen(QPen(Qt.red, 1.3, Qt.DashLine))
        curves[0].setZ(curves[1].z() + 2)
        curves[1].setPen(QPen(Qt.red, 1.5))
        curves[2].setPen(QPen(Qt.blue, 1.3, Qt.DashLine))
        curves[2].setZ(curves[3].z() + 2)
        curves[2].setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Triangle,
                                          QBrush(Qt.blue),
                                          QPen(Qt.black, 1),
                                          QSize(8, 8)))
        curves[3].setPen(QPen(Qt.blue, 1.5))
        
        #p.aplot.curve1.setStyle(Qwt.QwtPlotCurve.)

        #p.setWindowTitle("[%s.%s] %s %s" % (mach, lat, title, fld))
        self.mdiarea.addSubWindow(p)
        #print "Show"
        p.show()
        #plots.append(p)

        qs = ap.getGroupMembers(['C20', 'QUAD']) + \
            ap.getGroupMembers(['C21', 'QUAD'])
        xl = min([q.sb for q in qs])
        xr = max([q.se for q in qs])
        s, btx, bty = [], [], []
        try:
            betaref = ap.getBeta([q.name for q in qs], spos=True)
            curves[1].setData(betaref[:,-1], betaref[:,0], None)
            curves[3].setData(betaref[:,-1], betaref[:,1], None)

            fullmagprof = ap.machines.getLattice().getBeamlineProfile()
            magprof = [v for v in fullmagprof if max(v[0]) > xl \
                           and min(v[0]) < xr]
            p.aplot.setMagnetProfile(magprof)
            p.wid.autoScaleXY()
            p.aplot.replot()

            for q in qs[:3]:
                tbeta, tk1, tnu = ap.measBeta(q, full=True)
                #print tk1, tnu, tbeta
                QApplication.processEvents()
                s.append(tbeta[0,-1])
                btx.append(tbeta[0,0])
                bty.append(tbeta[0,1])
                curves[0].setData(s, btx, None)
                curves[2].setData(s, bty, None)
                p.wid.autoScaleXY()
                p.aplot.replot()
                _logger.info("beta measured for {0} " \
                             "(s={1}, btx={2}, bty={3})".format(
                        q.name, s[-1], btx[-1], bty[-1]))
        except:
            _logger.error("error at measBeta")
            raise

        _logger.info("finished beta measurement.")
        #if magprof: p.wid.setMagnetProfile(magprof)
        #self.connect(p, SIGNAL("destroyed()"), self.subPlotDestroyed)
        #print "update the plot"
        #p.updatePlot()
        # set the zoom stack
        #print "autozoom"
        #p.aplot.setErrorBar(self.error_bar)

    def measDispersion(self):
        p = ApMdiSubPlot(live=False)
        p.setAttribute(Qt.WA_DeleteOnClose)
        curves = [p.aplot.curve1, p.aplot.addCurve(),  # x and xref
                  p.aplot.addCurve(), p.aplot.addCurve() # y and yref
                  ]
        for curv in curves: curv.setStyle(Qwt.QwtPlotCurve.Lines)
        curves[0].setPen(QPen(Qt.red, 1.3, Qt.DashLine))
        curves[1].setPen(QPen(Qt.red, 1.5))
        curves[2].setPen(QPen(Qt.blue, 1.3, Qt.DashLine))
        curves[3].setPen(QPen(Qt.blue, 1.5))
        curves[2].setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Triangle,
                                          QBrush(Qt.blue),
                                          QPen(Qt.black, 1),
                                          QSize(8, 8)))
        
        #p.aplot.curve1.setStyle(Qwt.QwtPlotCurve.)

        #p.setWindowTitle("[%s.%s] %s %s" % (mach, lat, title, fld))
        self.mdiarea.addSubWindow(p)
        #print "Show"
        p.show()
        #plots.append(p)

        #bpms = ap.getGroupMembers(['C20', 'BPM']) + \
        #    ap.getGroupMembers(['C21', 'BPM'])
        bpms = ap.getElements('BPM')
        xl = min([q.sb for q in bpms])
        xr = max([q.se for q in bpms])
        s, btx, bty = [], [], []
        try:
            etaref = ap.getEta([q.name for q in bpms], spos=True)
            curves[1].setData(etaref[:,-1], etaref[:,0], None)
            curves[3].setData(etaref[:,-1], etaref[:,1], None)

            fullmagprof = ap.machines.getLattice().getBeamlineProfile()
            magprof = [v for v in fullmagprof if max(v[0]) > xl \
                           and min(v[0]) < xr]
            p.aplot.setMagnetProfile(magprof)
            #p.wid.autoScaleXY()
            p.aplot.replot()


            disp = ap.measDispersion(bpms, verbose=2)
            curves[0].setData(disp[:,-1], disp[:,0], None)
            curves[2].setData(disp[:,-1], disp[:,1], None)
            p.wid.autoScaleXY()
            p.aplot.replot()
            _logger.info("dispersion eta measured")
        except:
            _logger.error("error at measEta")
            raise

        _logger.info("finished eta measurement.")
        #if magprof: p.wid.setMagnetProfile(magprof)
        #self.connect(p, SIGNAL("destroyed()"), self.subPlotDestroyed)
        #print "update the plot"
        #p.updatePlot()
        # set the zoom stack
        #print "autozoom"
        #p.aplot.setErrorBar(self.error_bar)
        
    def runBba(self, bpms):
        """create local bump"""
        inp = {'bpms': [], 'quads': [], 'cors': [], 'quad_dkicks': [],
               'cor_dkicks': []}
        for bpm in bpms:
            inp['bpms'].extend([(bpm, 'x'), (bpm, 'y')])
            quad = ap.getClosest(bpm, 'QUAD')
            inp['quads'].extend([(quad, 'k1'), (quad, 'k1')])
            cor = ap.getNeighbors(bpm, 'HCOR', 1)[0]
            inp['cors'].append((cor, 'x'))
            cor = ap.getNeighbors(bpm, 'VCOR', 1)[0]
            inp['cors'].append((cor, 'y'))
            inp['quad_dkicks'].extend([1e-2, 1e-2])
            inp['cor_dkicks'].extend([np.linspace(-6e-5, 6e-5, 4),
                                     np.linspace(-6e-5, 6e-5, 4)])
                                     
        if self.bbadlg is None:
            #print self.obtdata.elem_names
            # assuming BPM has both x and y, the following s are same
            self.bbadlg = ApBbaDlg()
            self.bbadlg.resize(500, 200)
            self.bbadlg.setWindowTitle("Beam based alignment")
            #self.obtxplot.plotDesiredOrbit(self.orbitx_data.golden(), 
            #                            self.orbitx_data.x)
            #self.obtyplot.plotDesiredOrbit(self.orbity_data.golden(), 
            #                            self.orbity_data.x)

        self.bbadlg.show()
        self.bbadlg.raise_()
        self.bbadlg.activateWindow()

        from cothread.catools import caget, caput
        print __file__, "BBA align", caget('V:2-SR:C30-BI:G2{PH1:11}SA:X')

        self.bbadlg.runAlignment(**inp)
