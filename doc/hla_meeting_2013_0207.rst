2013/02/07 Status of Software Development for Commissioning
------------------------------------------------------------

- The :ref:`NSLS2 Software Requirement <nsls2-softreq>`
- The :ref:`NSLS2 Software Plan (more details)<nsls2-software-plan>`

  - Low level: EPICS channel access. `CSS (Control System Studio) <http://cs-studio.sourceforge.net>`_ 
  - Middle level: Element name/object based control. CSS with channel finder. Pannels.
  - High level: Elements and their relations. Beam manipulation, measurement and analysis. Input/Output Data management. CSS panels.
  - Python ``aphla`` can do jobs in all levels.

- We leave CSS panels to controls group. They build expert pannels and then we decised whether a simplified pannel for each subsystem are needed.
- Python ``aphla`` are in three parts

  - Core library (L. Yang)

    - data management: PV, twiss, ORM, unit conversion, etc.
    - low/middle level control.
    - element management: lattice layout (magnet), group, location.
    - measurement: ORM, twiss
    - tunning: orbit correction (local bump), tune, chromaticity, BBA.

  - GUI (Graphical User Interface) 

    - aplauncher (Y. Hidaka): "phone-book" of all high-level applications, scripts, ...
    - aporbit (L. Yang): orbit and magnet monitor. middle level control of any element which are tagged in channel finder.
    - apbba (L. Yang): beam based alignment
    - plotter (Y. Hidaka): plotter vs. ipython/python notebook is like MathCAD vs. Matlab/Mathematica/Maple
    - lattice tunner (Y. Hidaka): ramping of selected elements

  - Python scripts and notebooks (every one ...)

    - It is close to Mathematica but for python scripts.
    - Network accessible. Server(Kernel)/Client
    - The code and the outputs are together. Can be saved exported as PDF.
    - Scripts can be imported to notebooks.
    - A repository of these notebooks. (version controlled)
    
- PyTracy as a simulation tool. (J. Choi).
- Some database for AP. (J. Choi). Magnet measurement, lattice.
- Services and Tools (G. Shen, K. Shroff, etc.)

  - Virtual accelerator with EPICS channel access.

    - orbit, tune, twiss.
    - insertion device
    - turn-by-turn BPM is a work-in-progress.

  - Channel finder

    - virtual accelerator PV and lattice
    - LTD1: 108, LTD2: 105, LTB: 207, BR: 396
    - V2SR: 3089, V1LTD1: 41, V1LTD2: 3
    - all PV: 148,480
    - all hostName: 64, all iocName: 186

  - Archiver. CSS/Command line tools available.
  - CSS widgets

    - channel viewer/tree/table
    - channel orchestrator (ramping, step between two set of setpoints)
    - line2D/line/ ..

  - Unit conversion service: in progress
  - Twiss/Lattice service: in plan

    - lattice geometry (from DB)
    - magnet setting (from DB or machine)
    - simulation (Tracy or elegant)
    - data from service to DB
    - data from service/DB to python client
    - data visualization on web (optional)

- RF/Diagnostics. (not including BPM, tune) I assume python ``aphla`` is mostly a user of diagnostics data. The data are availabe in EPICS. Non EPICS data are hard (if not impossible) to retrieve. I also assume the data is processed and the hardware setting operations are limited from python ``aphla``.
- `Code version control. <http://code.nsls2.bnl.gov/job/hla-lyyang>`_
- `Code regression test. <http://lsasd2.ls.bnl.gov:8080/>`_
- `Documentation <http://lsasd2.ls.bnl.gov/~lyyang/hla/>`_: tutorial, user guide and library reference. The lib reference are accessible from Python terminal via ``help()`` and ``dir()``
- Matlab Middle Layer and LOCO

  - MML + AT + LOCO is like ``aphla`` + PyTracy + PyLOCO
  - MML and AT configuration V2SR are generated from ``aphla`` using channel finder data.
  - switching V2SR to SR will be the same if we tag SR PVs the same way (we should).
  - More and more testing ... (X. Yang)
- Insertion device (Y. Li)

Notes
~~~~~~~

- Data errors are harder to identify than code. Regression test works well for code, need human to find the problems in data. e.g. range of correctors, curve for magnet measurement.
- The interplay of PyTracy simulation and machine reading is a weak link. (fixable)
- Twiss/Lattice service has a lot of work, but still in plan mode. (does not prevent the commissioning, but very useful)

