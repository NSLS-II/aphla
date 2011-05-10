.. HLA documentation master file, created by
   sphinx-quickstart on Wed Oct  6 15:27:47 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to HLA documentation!
===================================

.. htmlonly::
   :Release: |version|
   :Date: |today|

   Download `PDF <./hla.pdf>`_

.. toctree::
   :maxdepth: 1

   intro.rst
   tutorial.rst
   requirement.rst
   ref.rst
   todo.rst
   appendix.rst

HLA Routines
==============


:mod:`hla.current`
******************

================================ ===========================================================
symbol                           description                                                
================================ ===========================================================
:func:`~hla.current.getCurrent`  Get the current from channel "SR:C00-BI:G00{DCCT:00}CUR-RB"
:func:`~hla.current.getLifetime` Monitor current change with, calculate lifetime dI/dt
================================ ===========================================================

:mod:`hla.hlalib`
*****************

======================================== ==================================================
symbol                                   description                                       
======================================== ==================================================
:func:`~hla.hlalib.eget`                 easier get with element name(s)         
:func:`~hla.hlalib.eput`                 easier put                              
:func:`~hla.hlalib.getRbChannels`        get the pv names for a list of elements 
:func:`~hla.hlalib.getSpChannels`        get the pv names for a list of elements 
:func:`~hla.hlalib.levenshtein_distance` Find the Levenshtein distance between two strings.
:func:`~hla.hlalib.reset_trims`          reset all trims in group "TRIMX" and "TRIMY"
======================================== ==================================================

:mod:`hla.latmanage`
********************

========================================= =====================================================================
symbol                                    description                                                          
========================================= =====================================================================
:func:`~hla.latmanage.addGroup`           add a new group, *group* should be plain string, characters in
:func:`~hla.latmanage.addGroupMembers`    Add a new member to a existing group     
:func:`~hla.latmanage.getBeta`            get the beta function from stored data   
:func:`~hla.latmanage.getChromaticity`    get chromaticity                         
:func:`~hla.latmanage.getChromaticityRm`  TODO                                     
:func:`~hla.latmanage.getCurrentMode`     TODO                                     
:func:`~hla.latmanage.getDispersion`      get the dispersion                       
:func:`~hla.latmanage.getElements`        return list of elements, given cell girder and sequence.
:func:`~hla.latmanage.getEta`             get the dispersion from stored data      
:func:`~hla.latmanage.getFftTune`         get tune from FFT                        
:func:`~hla.latmanage.getGroupMembers`    Get all elements in a group. If group is a list, consider which op:
:func:`~hla.latmanage.getGroups`          Get all groups own these elements, '*' returns all possible groups,
:func:`~hla.latmanage.getLocations`       Get the location of a group, either returned as a dictionary in
:func:`~hla.latmanage.getModes`           TODO                                     
:func:`~hla.latmanage.getNeighbors`       Get a list of n elements belongs to group. The list is sorted along s
:func:`~hla.latmanage.getPhase`           get the phase from stored data           
:func:`~hla.latmanage.getStepSize`        Return default stepsize of a given element
:func:`~hla.latmanage.getTune`            get tune                                 
:func:`~hla.latmanage.getTuneRm`          TODO                                     
:func:`~hla.latmanage.getTunes`           get tunes                                
:func:`~hla.latmanage.removeGroup`        Remove a group if it is empty            
:func:`~hla.latmanage.removeGroupMembers` Remove a member from group               
:func:`~hla.latmanage.removeLatticeMode`  TODO                                     
:func:`~hla.latmanage.saveBeta`           TODO                                     
:func:`~hla.latmanage.saveChromaticity`   TODO                                     
:func:`~hla.latmanage.saveChromaticityRm` TODO                                     
:func:`~hla.latmanage.saveDispersion`     TODO                                     
:func:`~hla.latmanage.savePhase`          TODO                                     
:func:`~hla.latmanage.saveTune`           TODO                                     
:func:`~hla.latmanage.saveTuneRm`         TODO                                     
========================================= =====================================================================

:mod:`hla.measorm`
******************

================================ ========================================================
symbol                           description                                             
================================ ========================================================
:class:`~hla.measorm.Orm`        Orbit Response Matrix           
:func:`~hla.measorm.measChromRm` measure chromaticity response matrix
:func:`~hla.measorm.measOrbitRm` Measure the beta function by varying quadrupole strength
================================ ========================================================

:mod:`hla.orbit`
****************

=============================== ========================================
symbol                          description                             
=============================== ========================================
:class:`~hla.orbit.Orbit`       TODO                           
:func:`~hla.orbit.getFullOrbit` Return orbit                   
:func:`~hla.orbit.getOrbit`     Return orbit                   
:func:`~hla.orbit.getOrbitRm`   TODO                           
:func:`~hla.orbit.perturbOrbit` TODO                           
=============================== ========================================

:mod:`hla.rf`
*************

============================== ========================================
symbol                         description                             
============================== ========================================
:func:`~hla.rf.getRfFrequency` Get the RF frequency          
:func:`~hla.rf.getRfVoltage`   Return RF voltage             
:func:`~hla.rf.putRfFrequency` set the rf frequency          
============================== ========================================





.. _EPICS: http://www.aps.anl.gov/epics
.. _Python: http://www.python.org/
.. _iPython: http://ipython.scipy.org/moin/
.. _matplotlib: http://matplotlib.sourceforge.net/
.. _SciPy: http://www.scipy.org/
.. _NumPy: http://numpy.scipy.org/


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

