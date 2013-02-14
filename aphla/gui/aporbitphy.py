"""
Physics Routines for aporbit
============================

"""

import aphla as ap
from PyQt4.QtCore import Qt, QSettings, QSize
from PyQt4.QtGui import QApplication, QBrush, QMdiArea, QPen
import PyQt4.Qwt5 as Qwt
from aporbitplot import ApOrbitPlot, ApPlot, DcctCurrentPlot, ApPlotWidget, ApMdiSubPlot

import logging
_logger = logging.getLogger(__name__)

class ApOrbitPhysics:
    def __init__(self, mdiarea):
        self.mdiarea = mdiarea
        pass

    def measBeta(self):
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

        bpms = ap.getGroupMembers(['C20', 'BPM']) + \
            ap.getGroupMembers(['C21', 'BPM'])
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
            curves[2].setData(disp[:,-1], disp[:,0], None)
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
        
