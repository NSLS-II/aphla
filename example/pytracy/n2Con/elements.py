from PyQt4.QtCore import *
from PyQt4.QtGui import *
import pytracy
import numpy
import hla
import styles
import sys

# import hla

NAME, FAMILY, STRENGTH, STATUS = range(4) 
#, END, ONOFF SETVAL, GETVAL, ONOFF, STATUS, MSSGE = range(8)
# Normal, Hovered, Pressed = range(3)
Normal, Error = range(2)

# spatial_index 
X_,  Y_ , Z_ = 0,1,2

# ps_index 
x_, px_, y_, py_, delta_, ct_ = 0,1,2,3,4,5

# pthicktype 
thick, thin = 0,1

# PartsKind 
drift, Wigl, Mpole, Cavity, marker, undef, Insertion, FieldMap, Spreader, Recombiner, Solenoid = range(11) # 0,1,2,3,4,5,6,7,8,9,10

# QDoubleSpinBox

# enum
All, Dip, Quad, Sext, Oct, Dec, Dodec = range(7) # 0,1,2,3,4,5,6
Horizontal, Vertical = 1,2
Meth_Linear, Meth_First, Meth_Second, Meth_Fourth, Meth_genfun = 0,1,2,4,5

HOMmax = 21
n_hamr_max = 10
pytracy.globval.MatMeth = True

K_Val={"Sext:H1":24.1977, "Quad:H1":-0.633004, "Quad:H2":1.47765, "Sext:H3":-4.1557, "Quad:H3":-1.70755, "Sext:H4":-20.4869,\
       "Quad:M1":-0.803148, "Sext:M1":-24.131, "Quad:M2":1.2223, "Sext:M2":28.7157, "Sext:M2HALF":57.4314,\
       "Quad:L3":-1.48928, "Sext:L3":-28.2618, "Quad:L2":1.81307, "Sext:L2":25.9682, "Quad:L1":-1.56216, "Sext:L1":-1.95754}

# class Element(QObject):
#     def __init__(self, name, onoff):
#         super(Element, self).__init__()
#         self.name=QString(name)
#         self.onoff = onoff

class compElement(hla.element.Element):
    def __init__(self,elementList,parent=None):
        super(compElement,self).__init__()
        self.elements=elementList
        self.sb = min(ele.sb for ele in self.elements)
        self.se = max(ele.se for ele in self.elements)
        self.length = self.se - self.sb
#       self.family = [ele.family for ele in self.elements)
        self.family = "COMPOSITE"
        self.name = [elem.name for elem in self.elements]
        self.stat = 0

    def pv(self):
        return [ele.pv() for ele in self.elements]



class ElementsModel(QAbstractTableModel):

    def __init__(self, machinename=QString("LTD1-txt")):
        super(ElementsModel, self).__init__()
        #    self.machinename = machinename
        # hla.initNSLS2VSRTwiss()
        hla.machines.initNSLS2VSRTxt()
        hla.machines.use(machinename)
        # g=hla.getGroups()
        self.elements = hla.getElements('*')
        for ele in self.elements:
            ele.stat = 1
        self.selectedElements = []
        self.famNames=[]
        self.loadcell()
        self.dirty = False
        self.cell = pytracy.PyCell
        self.globval = pytracy.globval

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        if index.column()==STRENGTH:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index)|
                            Qt.ItemIsEditable)
        else:
            # shoud return follow when returned Qt.ItemIsEnabled strage thing happen: the first column is not selected
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index))
          


    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or \
           not (0 <= index.row() < len(self.selectedElements)):
            return QVariant()
#       ele = self.cell[index.row()]
        column = index.column()
# NAME, FAMILY, STRENGTH, STATUS = range(4)
        ele = self.selectedElements[index.row()]
        if role == Qt.DisplayRole:
            if column == NAME:
                return QVariant(ele.name)
            elif column == FAMILY:
                if isinstance(ele.elements,list):
                    return QVariant([elem.family for elem in ele.elements])
                return QVariant(ele.family)
            
            elif column == STRENGTH:
                if ele.family == "QUAD":
                    return QVariant(self.cell[ele.numInCell].Elem.M.PB[HOMmax+2]) # For one value default
                elif ele.family == "SEXT":
                    return QVariant(self.cell[ele.numInCell].Elem.M.PB[HOMmax+3]) # For one value default
                elif ele.family == "FCOR" or ele.family[:3]=="COR":
                    pb = self.cell[ele.numInCell].Elem.M.PB
                    pl = self.cell[ele.numInCell].Elem.PL
                    return QVariant([1000.0*pb[HOMmax+1]*pl,1000.0*pb[HOMmax-1]*pl])
                elif  ele.family =="SQUADnCOR":
                    pb = self.cell[ele.numInCell].Elem.M.PB
                    pl = self.cell[ele.numInCell].Elem.PL
                    return QVariant([1000.0*pb[HOMmax+1]*pl,pb[HOMmax-2],1000.0*pb[HOMmax-1]*pl])
                elif ele.family == "BPM":
                    return QVariant([1000.0*self.cell[ele.numInCell].BeamPos[0],1000.0*self.cell[ele.numInCell].BeamPos[1]])
                else:
                    return QVariant(0)
            elif column == STATUS:
                return QVariant(ele.stat) 

        elif role == Qt.TextAlignmentRole:
#           if column == GETVAL or column == GETSET or column == PUTSET:
                return QVariant(int(Qt.AlignCenter|Qt.AlignVCenter))
#               return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))
#           return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
#       elif role == Qt.TextColorRole and column == TEU:
#           if ship.teu < 80000:
#               return QVariant(QColor(Qt.black))
#           elif ship.teu < 100000:
#               return QVariant(QColor(Qt.darkBlue))
#           elif ship.teu < 120000:
#               return QVariant(QColor(Qt.blue))
#           else:
#               return QVariant(QColor(Qt.red))
#       elif role == Qt.BackgroundColorRole:
#           if ship.country in (u"Bahamas", u"Cyprus", u"Denmark",
#                   u"France", u"Germany", u"Greece"):
#               return QVariant(QColor(250, 230, 250))
#           elif ship.country in (u"Hong Kong", u"Japan", u"Taiwan"):
#               return QVariant(QColor(250, 250, 230))
#           elif ship.country in (u"Marshall Islands",):
#               return QVariant(QColor(230, 250, 250))
#           else:
#               return QVariant(QColor(210, 230, 230))
        return QVariant()


    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and 0 <= index.row() < len(self.selectedElements):
            fam = self.selectedElements[index.row()].family
            column = index.column()
            if column == STRENGTH:
                cellnum = self.selectedElements[index.row()].numInCell
                pl = self.cell[cellnum].Elem.PL
                mpole = self.cell[cellnum].Elem.M.PB
                if fam == "FCOR" or fam[:3] == "COR":
                    mpole[HOMmax+1] = 0.001*value[0]/pl if pl>0 else 0.001*value[0]
                    mpole[HOMmax-1] = 0.001*value[1]/pl if pl>0 else 0.001*value[1]
                    self.cell[cellnum].Elem.M.Porder = 1
                if fam == "SQUADnCOR":
                    mpole[HOMmax+1] = 0.001*value[0]/pl if pl>0 else 0.001*value[0]
                    mpole[HOMmax-2] = 0.001*value[1]/pl if pl>0 else 0.001*value[1]
                    mpole[HOMmax-1] = 0.001*value[2]/pl if pl>0 else 0.001*value[2]
# Max Porder !!!!!!!!1
                    self.cell[cellnum].Elem.M.Porder = 2 if value[1] > 0 else 1
                if fam == "QUAD":
                    mpole[HOMmax+2] = value
                self.cell[cellnum].Elem.M.PB = mpole
                pytracy.Ring_GetTwiss(True,0)
#   mpolArray   PBpar;     // design
#   mpolArray   PBsys;     // systematic
#   mpolArray   PBrms;     // rms
#   mpolArray   PBrnd;     // random number
#   mpolArray   PB;        // total

                

            if column == STATUS:
                self.elements[index.row()].stat=value
            self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
            return True
        return False





    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(Qt.AlignCenter|Qt.AlignVCenter))
            return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            if section == NAME:
                return QVariant("NAME")
            elif section == FAMILY:
                return QVariant("FAMILY")
            elif section == STRENGTH:
                return QVariant("STRENGTH")
#           elif section == DESCRIPTION:
#               return QVariant("Description")
#           elif section == TEU:
#               return QVariant("TEU")
            elif section == STATUS:
                return QVariant("STATUS")
        return QVariant(int(section + 1))

    def rowCount(self, index=QModelIndex()):
        return len(self.selectedElements)

    def columnCount(self, index=QModelIndex()):
        return 4

    def loadcell(self):
#       print pytracy.cellconcat
        pytracy.cellconcat = False
        pytracy.globval.MatMeth = False
        k = 0
        globaldrnum = 0
        preEle = None
        prese = 0
        compEle = None
        print 'all:',len(self.elements)
        for n,ele in enumerate(self.elements):
            if ele.se == 0:
                continue
#           s0 = ele.se - ele.length
            dl = ele.sb-prese
#           print ele.name
#           print "Element Num",len(self.selectedElements)
#           print ele.name,ele.family,ele.sb,ele.length,ele.se,"dl",dl
            if dl > 0:   
#               print "dl positive",
            # if the elements are separated 
            # insert the previous element to the Cell, make a drift and also insert it
                if compEle is not None:
#                   print "compEle is not None"
                    comp = compElement(compEle)
#                   print "addCompositeToCell",comp.sb,comp.length,comp.se
                    self.addCompositeToCell(comp)
                    comp.numInCell = pytracy.globval.Cell_nLoc
                    self.selectedElements.append(comp)
                    compEle=None
                elif preEle is not None:
#                   print "compEle is None"
                    preEle.elements = None
                    self.addElementToCell(preEle)
#                   print "addElementToCell",preEle.sb,preEle.length,preEle.se
                    preEle.numInCell = pytracy.globval.Cell_nLoc
                    self.selectedElements.append(preEle)
                # find if the Drift of same length is already in the ElemFam
                dfnum = findDriftFam(dl)
                if dfnum < 0:
                    globaldrnum += 1
                    dfname = ("D%03d"%globaldrnum)
                    dfnum = addDrift(dfname,dl)
                    self.famNames.append(dfname)
                pytracy.globval.Cell_nLoc += 1
#               print "adddrift",dfnum,dl
                pytracy.PyCell[pytracy.globval.Cell_nLoc].Fnum = dfnum
            else:
#               print "dl negative"
            # there is no gap from or overlapped with the previous element
                if compEle is None:
                    compEle=[preEle,ele]
                else:   # already in Composition mode
                    compEle.append(ele)
            preEle = ele
            prese = ele.se
#           dummy = raw_input(":::")
    
        if compEle is not None:
            comp = compElement(compEle)
            comp.numInCell = pytracy.globval.Cell_nLoc
            self.addCompositeToCell(comp)
            self.selectedElements.append(comp)
        else:
            preEle.elements = None
            self.addElementToCell(preEle)
            self.selectedElements.append(preEle)
#       print "loop finished with famnum", famnum
     
#   GetRingType();/* define whether a ring or a transfer line */
        pytracy.globval.RingType = 1;

#   GetEnergy();  /* define particle energy */
        pytracy.globval.Energy = 3.0;

#   GetCODEPS();  /* define COD precision */
        pytracy.globval.CODeps = 1e-12;

#   GetDP();      /* define energy offset */
        pytracy.globval.dPcommon = 1e-8;

        pytracy.RegisterKids(); # Check wether too many elements */
#       sys.exit()

        pytracy.Cell_Init()

        pytracy.globval.H_exact     = False; # Small Ring Hamiltonian^M
        pytracy.globval.quad_fringe = False; # quadrupole fringe fields on/off^M
        pytracy.globval.EPU         = False; # Elliptically Polarizing Undulator^M
        pytracy.globval.Cavity_on   = False; # Cavity on/off */^M
        pytracy.globval.radiation   = False; # radiation on/off */^M
        pytracy.globval.IBS         = False; # diffusion on/off */^M
        pytracy.globval.emittance   = False; # emittance  on/off */^M
        pytracy.globval.pathlength  = False; # Path lengthening computation */^M
        pytracy.globval.CODimax     = 40;    # maximum number of iterations for COD^M

        pytracy.globval.delta_RF = 0.03 # RFacceptance
        pytracy.Cell_SetdP(0.0)
#       print self.famNames
#       print pytracy.PyCell[pytracy.globval.Cell_nLoc].S

        pytracy.Ring_GetTwiss(True,0)
#       for i in range(pytracy.globval.Cell_nLoc):
#       for i,e in enumerate(self.selectedElements):
#           print "Element",e.name,e.family,pytracy.PyCell[e.numInCell].Elem.PName
#           print "Element",i,"CellNum",e.numInCell,e.sb,e.length,pytracy.PyCell[e.numInCell].Elem.PL,e.se,pytracy.PyCell[e.numInCell].S
#       print
#       for i in range(30): #(pytracy.globval.Cell_nLoc):
#           cell = pytracy.PyCell[i]
#           print i,"Fnum",cell.Fnum,"Knum",cell.Knum,"PName",cell.Elem.PName,"Pkind",cell.Elem.Pkind,"PL",cell.Elem.PL,"S",cell.S
#           if i%100 == 29:
#           elem = pytracy.PyElemFam[i]
#           print "PName",elem.ElemF.PName, "Pkind",elem.ElemF.Pkind, "PL",elem.ElemF.PL
#           cell = pytracy.PyCell[i]
#           print cell.S,cell.Beta[0],cell.Beta[1]
#       sys.exit()
#       print "Cell_Init finished"
        print "Total Length",pytracy.PyCell[pytracy.globval.Cell_nLoc].S

        
    def addCompositeToCell(self,ele):
        if len(ele.elements) == 3:  # HCOR, SQUAD, VCOR
            famname = "SQUADnCOR"
        elif ele.elements[0].family[1:]=="FCOR":
            famname = "FCOR"
        elif ele.elements[0].family[1:]=="COR":
            if ele.length > 0.25:
                famname = "COR03"
            else:
                famname = "COR02"
        else:
            famname = "CAVITY"

        ele.family = famname

#       if famname in self.famDict.iterkeys() 
        if famname in self.famNames:
#           fnum = self.famDict[famname][0]
            fnum = self.famNames.index(famname) + 1
        elif famname == "SQUADnCOR":
            fnum = addMpole(famname,ele.length,2)
            self.famNames.append(famname)
#           self.famDict[famname]=(pytracy.globval.Elem_nFam, ele.length)
        elif famname == "CAVITY":
            fnum = addCavity(famname)
            self.famNames.append(famname)
        else:
            fnum = addCorrector(famname,ele.length)
            self.famNames.append(famname)

        if pytracy.globval.Cell_nLoc < 8000 : # pytracy.Cell_nLocMax:
            pytracy.globval.Cell_nLoc +=1
            pytracy.PyCell[pytracy.globval.Cell_nLoc].Fnum = fnum
        else:
            print "Cell Number exceeded the Maximum: 8000"
    
    def addElementToCell(self,ele):
        if ele.family == "BPM" :
            famname = "BPM"
        elif ele.family == "CAVITY" :
            famname = "CAVITY"
        else:
            pvs = ele.pv()
            if isinstance(pvs,list):
                pv = pvs[0]
            else:
                pv = pvs
            famname = pv[(pv.index('{')+1):pv.index('}')]
#       elemfams = pytracy.PyElemFam[:pytracy.Elem_nFamMax]
#       names = [elem.ElemF.PName for elem in elemfams]
#       print self.famNames
        exist = False
        if famname in self.famNames:
            if famname=="Sext:M2" and ele.length < 0.2:
                famname1 = famname + "HALF"
                self.famNames.append(famname1)
                famnum = addSext(famname1,ele.length,K_Val[famname])
            else:
                famnum = self.famNames.index(famname) + 1
        else:
            if ele.family == 'DIPOLE' or ele.family == 'BEND':
                self.famNames.append(famname)
                famnum = addBend(famname,ele.length)
            elif ele.family == "QUAD":
                self.famNames.append(famname)
                famnum = addQuad(famname,ele.length,K_Val[famname])
            elif ele.family == "SEXT":
                self.famNames.append(famname)
                famnum = addSext(famname,ele.length,K_Val[famname])
            elif ele.family == "HCOR" or ele.family == "HFCOR" or ele.family == "VCOR" or ele.family == "VFCOR":
                self.famNames.append(famname)
                famnum = addCorrector(famname,ele.length)
#               if ele.family == "HCOR" or ele.family == "HFCOR":
#                   pytracy.globval.hcorr = famnum
#               else:
#                   pytracy.globval.vcorr = famnum
#           elif ele.family == "SQUAD":
#               print famname,ele.sb,ele.se
#               famnum = addSQuad(famname,ele.length,0)
#               print famname,ele.sb,ele.se
            elif ele.family == "BPM" :
                self.famNames.append(famname)
                famnum = addBPM(famname)
            elif ele.family == "CAVITY":
                self.famNames.append(famname)
                famnum = addCavity(famname)
            elif ele.family == "FLAG" or ele.family == "ICT":
                pass
            else:
                print "Unknown Family: ", ele.family,"(name:",ele.name,")"
#           if ele.sb < prese:
#               print "overlapped",famname
                    
#       print self.famNames
#       print ele.family,"Found : ",famnum
    
        pytracy.globval.Cell_nLoc += 1
        k = pytracy.globval.Cell_nLoc
        pytracy.PyCell[k].Fnum = famnum
        ele.numInCell = k
    

# Radid GUI p488
# http://www.qtcentre.org/threads/26916-inserting-custom-Widget-to-listview
class ElementsDelegate(QStyledItemDelegate):

    def __init__(self, parent=None):
        super(ElementsDelegate, self).__init__(parent)
        self.lastUnderMouse = QModelIndex()
        self.editrow = -1


    def paint(self, painter, opt, index):
        fam = index.model().selectedElements[index.row()].family
        if fam == "SQUADnCOR" or fam == "FCOR" or fam[:3] == "COR":
            nelem = 3 if fam == "SQUADnCOR" else  2
            if index.column()== NAME:
                painter.save()
                QStyledItemDelegate.paint(self,painter,opt,index)
                # for selected state (opt.state | QStyle.State_Selected), 
                # without the above line only the text will be written even for selected row
                if opt.state & QStyle.State_Selected and self.editrow == index.row():
                    painter.setPen(Qt.black)
                qnames =  index.data().toList()
                values = [name.toString() for name in qnames]
                left = opt.rect.left()
                top = opt.rect.top()
                height = opt.rect.height()//nelem
                for i in range(nelem):
                     painter.drawText(QRect(left,top+height*i,opt.rect.width(),height),
                                           Qt.AlignCenter|Qt.AlignVCenter,QString(values[i]))
                painter.restore()

            elif index.column()== FAMILY:
                painter.save()
                QStyledItemDelegate.paint(self,painter,opt,index)
                # for selected state (opt.state | QStyle.State_Selected),
                # without the above line only the text will be written even for selected row
                if opt.state & QStyle.State_Selected and self.editrow == index.row():
                    painter.setPen(Qt.black)
                qfams =  index.data().toList()
                values = [fam.toString() for fam in qfams]
                left = opt.rect.left()
                top = opt.rect.top()
                height = opt.rect.height()//nelem
                for i in range(nelem):
                     painter.drawText(QRect(left,top+height*i,opt.rect.width(),height),
                                           Qt.AlignCenter|Qt.AlignVCenter,QString(values[i]))
                painter.restore()
                if self.editrow == index.row():
                    self.editrow = -1 

            elif index.column() == STRENGTH:
                pb = index.data().toList()
#               if nelem == 3:
#                   dvalues = [pb[HOMmax+1].toDouble()[0],pb[HOMmax-2].toDouble()[0],pb[HOMmax-1].toDouble()[0]]
#                   values=["%f"%pb[HOMmax+1],"%f"%pb[HOMmax-2],"%f"%pb[HOMmax-1]]
                values=["%4.2f"%val.toDouble()[0] for val in pb]
#               else:
#                   values = [pb[HOMmax+1].toString(),pb[HOMmax-1].toString()]
#                   values=["%f"%pb[HOMmax+1],"%f"%pb[HOMmax-1]]
                left = opt.rect.left()
                top = opt.rect.top()
                height = opt.rect.height()//nelem
                for i in range(nelem):
                     painter.drawText(QRect(left,top+height*i,opt.rect.width(),height),
                                           Qt.AlignCenter|Qt.AlignVCenter,QString(values[i]))
            if index.column() == STATUS:
                return

        elif fam == "BPM":
            if index.column() == STRENGTH:
                rds = index.data().toList()
                values=["%4.2f"%val.toDouble()[0] for val in rds]

                left = opt.rect.left()
                top = opt.rect.top()
                width = opt.rect.width()//2
                height = opt.rect.height()
                for i in range(2):
                     painter.drawText(QRect(left+width*i,top,width,height),
                                           Qt.AlignCenter|Qt.AlignVCenter,QString(values[i]))
            elif index.column() == STATUS:
                painter.fillRect(opt.rect,QColor("#fffacd")) #Qt.opt.palette.highlight()) #Qt.red)

            else:
                QStyledItemDelegate.paint(self,painter,opt,index)
                
                
        elif index.column() == STATUS:
            s = index.data().toInt()[0]
            opt.text = QString("OFF") #trUtf8("Button text");	
            opt.state |= QStyle.State_Enabled;	
            if (s == Normal):
                opt.state |= QStyle.State_MouseOver;	
            if (s == Error):	
                opt.state |= QStyle.State_Sunken;	
                opt.text = QString("ON") #trUtf8("Button text")
            if s==1:
                painter.fillRect(opt.rect,QColor("#fffacd")) #Qt.opt.palette.highlight()) #Qt.red)
            else:
                painter.fillRect(opt.rect,Qt.black)
        else:
            QStyledItemDelegate.paint(self,painter,opt,index)


    def createEditor(self, parent, option, index):
        fam = index.model().selectedElements[index.row()].family
        if index.column() == STRENGTH:
            if fam == "FCOR" or fam[:3] == "COR":
               editor = QWidget(parent)
#              editor.setContentsMargins(0,0,0,0)
               layout = QVBoxLayout(editor)
               layout.setSpacing(0)
               layout.setMargin(0)
               editor.spin1 = QDoubleSpinBox(editor)
               editor.spin1.setSingleStep(0.01)
               editor.spin1.setRange(-5.0,5.0)
               editor.spin2 = QDoubleSpinBox(editor)
               editor.spin2.setSingleStep(0.01)
               editor.spin2.setRange(-5.0,5.0)
               layout.addWidget(editor.spin1)
               layout.addWidget(editor.spin2)
               return editor
            elif fam == "SQUADnCOR" :
               editor = QWidget(parent)
#              editor.setContentsMargins(0,0,0,0)
               layout = QVBoxLayout(editor)
               layout.setSpacing(0)
               layout.setMargin(0)
               editor.spin1 = QDoubleSpinBox(editor)
               editor.spin1.setSingleStep(0.01)
               editor.spin1.setRange(-5.0,5.0)
               editor.spin2 = QDoubleSpinBox(editor)
               editor.spin2.setSingleStep(0.01)
               editor.spin2.setRange(-5.0,5.0)
               editor.spin3 = QDoubleSpinBox(editor)
               editor.spin3.setSingleStep(0.01)
               editor.spin3.setRange(-5.0,5.0)
               layout.addWidget(editor.spin1)
               layout.addWidget(editor.spin2)
               layout.addWidget(editor.spin3)
               return editor
            dspinbox = QDoubleSpinBox(parent)
            dspinbox.setSingleStep(0.01)
            if fam == "SEXT":
                dspinbox.setRange(-100.0,100.0)
            elif fam == "QUAD":
                dspinbox.setRange(-5.0,5.0)
            return dspinbox

        else:
            return QItemDelegate.createEditor(self, parent, option, index)


    def setEditorData(self, editor, index):
        fam = index.model().selectedElements[index.row()].family
        if index.column() == STRENGTH:
            if fam == "SQUADnCOR":
                valist = index.data().toList()
                editor.spin1.setValue(valist[0].toDouble()[0])
                editor.spin2.setValue(valist[1].toDouble()[0])
                editor.spin3.setValue(valist[2].toDouble()[0])
                self.editrow = index.row()
            elif fam == "FCOR" or fam[:3] == "COR":
                valist = index.data().toList()
                editor.spin1.setValue(valist[0].toDouble()[0])
                editor.spin2.setValue(valist[1].toDouble()[0])
                self.editrow = index.row()
            else:
                editor.setValue(index.data().toDouble()[0])
#               editor.setValue(index.model().data(index).toDouble())

    def setModelData(self, editor, model, index):
        fam = index.model().selectedElements[index.row()].family
        if index.column() == STRENGTH:
            if fam == "SQUADnCOR":
                value=[editor.spin1.value(), editor.spin2.value(), editor.spin3.value()]
                # since it was customized QVariant is not needed for setData'value
                model.setData(index,value)
            elif fam == "FCOR" or fam[:3] == "COR":
                value=[editor.spin1.value(), editor.spin2.value()]
                model.setData(index,value)
            else :
                model.setData(index,editor.value())
        

    def editorEvent(self, event, model, option, index):
 
        if (event.type() == QEvent.MouseButtonPress and index.column()==STATUS): 
                # or event.type() == QEvent.MouseButtonDblClick) :
            self.lastUnderMouse = index
         
        if event.type() == QEvent.MouseButtonRelease and index == self.lastUnderMouse :
                if (index.isValid() and index.column() == STATUS) :
                    sta = model.data(index).toInt()[0]
                    if sta == Error:
                        model.setData(index, Normal)    #, Qt.UserRole) 
                    else:
                        model.setData(index, Error)
                    self.emit(SIGNAL("needsUpdate(QModelIndex)"),index) 
                    self.lastUnderMouse = QModelIndex() 
                    
        return QStyledItemDelegate.editorEvent(self, event, model, option, index);





      # def Mpole_Alloc():
#     M = pytracy.MpoleType()
# 
#     M.Pmethod = Meth_Fourth; 
#     M.PN = 0;
# /* Displacement errors */
#     for j in range(2):
#         M.PdSsys[j] = 0.0
#         M.PdSrms[j] = 0.0
#         M.PdSrnd[j] = 0.0
  
#     M.PdTpar = 0.0 #  /* Roll angle */
#     M.PdTsys = 0.0 #  /* systematic Roll errors */
#     M.PdTrms = 0.0 #  /* random Roll errors */
#     M.PdTrnd = 0.0 #  /* random seed */
#     for j in range(2*HOMmax + 1):
#   /* Initializes multipoles strengths to zero */
#         M.PB[j]    = 0.0; 
#         M.PBpar[j] = 0.0;
#         M.PBsys[j] = 0.0; 
#         M.PBrms[j] = 0.0;
#         M.PBrnd[j] = 0.0;
  
#     M.Porder = 0; 
#     M.n_design = 0;
#     M.Pirho  = 0.0 #  /* inverse of curvature radius */
#     M.PTx1   = 0.0 #  /* Entrance angle */
#     M.PTx2   = 0.0 #  /* Exit angle */
#     M.Pgap   = 0.0 #  /* Gap for fringe field ??? */

#     M.Pc0 = 0.0; 
#     M.Pc1 = 0.0; 
#     M.Ps1 = 0.0;

#     return M

def Cav_Alloc():
    C = pytracy.CavityType()
    C.Pvolt = 0.0; C.Pfreq = 0.0; C.phi = 0.0; C.Ph = 0;
    return C


def Wiggler_Alloc(Elem):
    W = pytracy.WigglerType()

    W.Pmethod = Meth_Linear; 
    W.PN = 0;
    for j in range(2):
        W.PdSsys[j] = 0.0; 
        W.PdSrnd[j] = 0.0;
  
    W.PdTpar = 0.0; 
    W.PdTsys = 0.0; 
    W.PdTrnd = 0.0;
    W.n_harm = 0;
    for j in range(n_harm_max):
        W.BoBrhoV[j] = 0.0; 
        W.BoBrhoH[j] = 0.0; 
        W.kxV[j] = 0.0; 
        W.kxH[j] = 0.0;
        W.phi[j] = 0.0;
    W.lambda0 = 0.0
  
    for j in range(HOMmax+1):
        W.PBW[j+HOMmax] = 0.0;
    W.Porder = 0;
    return W


# def mkCell(elist):
#     for ele in elist:
#         if ele.family == 'QUAD':
            
#     if elist

def addDrift(name, val):
    pytracy.globval.Elem_nFam += 1
    if (pytracy.globval.Elem_nFam <= pytracy.Elem_nFamMax) :
        famnum = pytracy.globval.Elem_nFam
        WITH = pytracy.PyElemFam[famnum-1]
        WITH1 = WITH.ElemF
        WITH1.PName = name
        WITH1.PL = val;
        WITH1.Pkind = drift
        WITH1.D = pytracy.Drift_Alloc(WITH1)
        return famnum
    else :
        print "Elem_nFamMax exceeded: ", globval.Elem_nFam,  "(", Elem_nFamMax,")"
        return -1

def findDriftFam(length):
    for n in range(pytracy.globval.Elem_nFam):
        if pytracy.PyElemFam[n].ElemF.Pkind == drift and pytracy.PyElemFam[n].ElemF.PL == length:
            return n+1
    return -1

def addBend(name,QL=0, nmeth=Meth_Linear, nslice=4,t=6.0, QK=0):
    if (pytracy.globval.Elem_nFam < pytracy.Elem_nFamMax) :
        pytracy.globval.Elem_nFam += 1
        famnum = pytracy.globval.Elem_nFam
        WITH = pytracy.PyElemFam[famnum-1]
        WITH1 = WITH.ElemF
        WITH1.PName = name
        WITH1.PL = QL
        WITH1.Pkind = Mpole
        WITH1.M=pytracy.Mpole_Alloc(WITH1)
        WITH2 = WITH1.M;
        WITH2 = pytracy.MpoleType()
        WITH2.Pmethod = nmeth;
        if (nmeth != Meth_Linear) :
                pytracy.globval.MatMeth = False
        WITH2.PN = nslice;
        if (WITH1.PL != 0.0):
            WITH2.Pirho = t * numpy.pi / 180.0 / WITH1.PL;
        else :
            WITH2.Pirho = t * numpy.pi / 180.0;
        WITH2.Porder = 0
        WITH2.n_design = Dip
        WITH2.PBpar[HOMmax+2] = QK
        return famnum
    else :
        print "Elem_nFamMax exceeded: ", globval.Elem_nFam,  "(", Elem_nFamMax,")"
        return -1

def addQuad(name,QL=0,QK=0, nmeth=Meth_Fourth, nslice=4):
    pytracy.globval.Elem_nFam += 1
    if (pytracy.globval.Elem_nFam <= pytracy.Elem_nFamMax) :
#       print "addQuad1",pytracy.globval.Elem_nFam
        famnum = pytracy.globval.Elem_nFam
#       print "addQuad2 famnum",famnum
        WITH = pytracy.PyElemFam[famnum-1]
        WITH1 = WITH.ElemF
        WITH1.PName = name
        WITH1.PL = QL
        WITH1.Pkind = Mpole
        WITH1.M=pytracy.Mpole_Alloc(WITH1)
        WITH2 = WITH1.M;
        WITH2.Pmethod = nmeth;
        if (nmeth != Meth_Linear) :
            pytracy.globval.MatMeth = False
        WITH2.PN = nslice;
        WITH2.Porder = 2
        WITH2.n_design = Quad
#       WITH2.PBpar[HOMmax+2] = QK
        pbpar = (2*HOMmax+1)*[0]
        pbpar[HOMmax+2]=QK
        WITH2.PBpar = pbpar
#       print "addQuad QK:",QK, "HOMmax+2", WITH2.PBpar[HOMmax+2]
        return famnum
    else :
        print "Elem_nFamMax exceeded: ", globval.Elem_nFam,  "(", Elem_nFamMax,")"
        return -1

def addSQuad(name,QL=0,QK=0, nmeth=Meth_Fourth, nslice=4):
    pytracy.globval.Elem_nFam += 1
    if (pytracy.globval.Elem_nFam <= pytracy.Elem_nFamMax) :
        famnum = pytracy.globval.Elem_nFam
        WITH = pytracy.PyElemFam[famnum-1]
        WITH1 = WITH.ElemF
        WITH1.PName = name
        WITH1.PL = QL
        WITH1.Pkind = Mpole
        WITH1.M=pytracy.Mpole_Alloc(WITH1)
        WITH2 = WITH1.M;
        WITH2.Pmethod = nmeth;
        if (nmeth != Meth_Linear) :
            pytracy.globval.MatMeth = False
        WITH2.PN = nslice;
        WITH2.Porder = 2
        WITH2.n_design = 2
        pbpar = (2*HOMmax+1)*[0]
        pbpar[HOMmax-2]=QK
        WITH2.PBpar = pbpar
        return famnum
    else :
        print "Elem_nFamMax exceeded: ", globval.Elem_nFam,  "(", Elem_nFamMax,")"
        return -1

def addSext(name,QL=0,QK=0,nmeth=Meth_Fourth,nslice=1):
    pytracy.globval.Elem_nFam += 1
    if (pytracy.globval.Elem_nFam <= pytracy.Elem_nFamMax) :
        famnum = pytracy.globval.Elem_nFam
        WITH = pytracy.PyElemFam[famnum-1]
        WITH1 = WITH.ElemF
        WITH1.PName = name
        WITH1.PL = QL
        WITH1.Pkind = Mpole
        WITH1.M=pytracy.Mpole_Alloc(WITH1)
        WITH2 = WITH1.M;
        WITH2.Pmethod = nmeth;
        if (nmeth != Meth_Linear) :
            pytracy.globval.MatMeth = False
        WITH2.PN = nslice;
        if (WITH1.PL != 0.0):
            WITH2.Pthick = thick
        else:
            WITH2.Pthick = thin
        WITH2.Porder = 3
        WITH2.n_design = Sext
        pbpar = (2*HOMmax+1)*[0]
        pbpar[HOMmax+3]=QK
        WITH2.PBpar = pbpar
        return famnum
    else :
        print "Elem_nFamMax exceeded: ", globval.Elem_nFam,  "(", Elem_nFamMax,")"
        return -1

def addCavity(name,Vrf = 0,Frf = 0,QPhi = 0,harnum = 0):
    pytracy.globval.Elem_nFam += 1
    if (pytracy.globval.Elem_nFam <= pytracy.Elem_nFamMax) :
        famnum = pytracy.globval.Elem_nFam
        WITH = pytracy.PyElemFam[famnum-1]
        WITH1 = WITH.ElemF
        WITH1.PName = name
        WITH1.Pkind = Cavity
        WITH1.C = Cav_Alloc()
        WITH3 = WITH1.C;
        WITH3.Pvolt = Vrf;  # /* Voltage [V] */
        WITH3.Pfreq = Frf;  # /* Frequency in Hz */
        WITH3.phi = QPhi*numpy.pi/180.0;
        WITH3.Ph = harnum;
        return famnum
    else :
        print "Elem_nFamMax exceeded: ", globval.Elem_nFam,  "(", Elem_nFamMax,")"
        return -1

def addCorrector(name,QL=0,nmeth=Meth_Linear,nslice=1):
    pytracy.globval.Elem_nFam += 1
    if (pytracy.globval.Elem_nFam <= pytracy.Elem_nFamMax) :
        famnum = pytracy.globval.Elem_nFam
        WITH = pytracy.PyElemFam[famnum-1]
        WITH1 = WITH.ElemF
        WITH1.PName = name
        WITH1.PL = QL
        WITH1.Pkind =  Mpole
        WITH1.M=pytracy.Mpole_Alloc(WITH1)
        WITH2 = WITH1.M
        if (WITH1.PL != 0.0):
            WITH2.Pthick = thick
        else:
            WITH2.Pthick = thin
        WITH2.Pmethod = nmeth
        if (nmeth != Meth_Linear) :
            pytracy.globval.MatMeth = False
        WITH2.PN = nslice;
        return famnum
    else :
        print "Elem_nFamMax exceeded: ", globval.Elem_nFam,  "(", Elem_nFamMax,")"
        return -1

def addMpole(name,QL=0,Porder = 0,nmeth=Meth_Linear,nslice=1):
    pytracy.globval.Elem_nFam += 1
    if (pytracy.globval.Elem_nFam <= pytracy.Elem_nFamMax) :
        famnum = pytracy.globval.Elem_nFam
        WITH = pytracy.PyElemFam[famnum-1]
        WITH1 = WITH.ElemF
        WITH1.PName = name
        WITH1.PL = QL
        WITH1.Pkind =  Mpole
        WITH1.M=pytracy.Mpole_Alloc(WITH1)
        WITH2 = WITH1.M
        if (WITH1.PL != 0.0):
            WITH2.Pthick = thick
        else:
            WITH2.Pthick = thin
        WITH2.Pmethod = nmeth
        if (nmeth != Meth_Linear) :
            pytracy.globval.MatMeth = False
        WITH2.PN = nslice
        WITH2.Porder = 2 # Porder
        WITH2.n_design = Porder 
        return famnum
    else :
        print "Elem_nFamMax exceeded: ", globval.Elem_nFam,  "(", Elem_nFamMax,")"
        return -1

def addBPM(name):
    pytracy.globval.Elem_nFam += 1
    if (pytracy.globval.Elem_nFam <= pytracy.Elem_nFamMax) :
        famnum = pytracy.globval.Elem_nFam
        WITH = pytracy.PyElemFam[famnum-1]
        WITH1 = WITH.ElemF
        WITH1.Pkind = Mpole
        WITH1.PName = name
        WITH1.PL = 0.0
        WITH1.M=pytracy.Mpole_Alloc(WITH1)
        WITH2 = WITH1.M;
        WITH2.Pthick = thin
        return famnum
    else :
        print "Elem_nFamMax exceeded: ", globval.Elem_nFam,  "(", Elem_nFamMax,")"
        return -1


if __name__ == "__main__":
    constructModel()
