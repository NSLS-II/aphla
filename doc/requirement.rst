NSLS2 HLA Requirement (List of Applications/Scripts)
=====================================================

.. _Software Requirement:

.. role:: hla
.. role:: hladone

This chapter describes software requirement for NSLS-II
commissioning. This list is mainly from [Willeke2009]_ and [Krinsky2010]_,
plus some personal experiences.

:hla:`Software implemented as part of the HLA is marked`. Finished
software/scripts are :hladone:`also marked`. The functions which need only
simple monitoring in HLA is not marked as a HLA feature.

General Operation
------------------

- Overall status page (warning when read/set are different too much ?)
    - The status includes beam information, and hardware status including
      magnet and its power supply, vacuum, RF, and so on.
    - The applications will provide overall status of the whole machine,
      and give warnings when any abnormal beam behaviour is detected, for
      example a readback differs from setting point larger than its
      threshhold. 
    - :hla:`major magnets reading: (Dipole, Quad, Sext, Trim, ...)` (CSS operation panel)
- Permit system monitor and control
- Data logger and data display
- Electronic logbook
- :hla:`Converting between machine unit and physics unit.` (G.Shen)
- :hla:`Smooth Ramping`
    - :hla:`list channels we are interested.`
    - :hla:`ramp (i.e. linear interpolation) whole group at certain rate.`
    - :hla:`searching for channels with wild-card`
    - save state of the machine, read back and set the machine. (for small
      set of PVs, HLA can implement.)
    - :hla:`linear interpolation to a saved state.`

  The control group may provide ramping for whole storage ring, here this
  application can ramp specified channels between two states.

- view archive data in certain time frame.
    - link to logbook to view reasons for shutdown, current drop (?)
    - simple statistic for the data: average, variance, maximum, minimum.
    - Monitoring stability of any readings and online data: magnet
      readback, orbit, temperature, vacuum.
    - print, save figures.
- Major Subsystem
    - RF display and control.
        - page with all relevant settings, read back, status, parameters
        - optional: RF feedback status which detects orbit drift vs RF
          frequency.
    - Vacuum display and control. "Water flow" or 3D plot of vacuum status
        - Pressure vs index.
        - optional: Pressure vs pump location.
        - optional: waterflow plot.   along the ring with time line info.
    - Magnet temperature interlock display and control
    - Cryogenics system display and control
    - Pulsed magnet systems monitor and control
    - :hla:`Fast orbit feedback control above cell level` 
	- :hla:`turn on/off`
	- :hla:`disable/enable certain trim/BPM`
	- :hla:`update(import/export) RespMatrix`
        - :hla:`fast/slow strength shift`
        - :hla:`fast/slow strength monitoring and analysis`
    - Insertion Device (see the following)
- Safety Systems
    - Personal protection system status display
    - Equipment protection status display and control
    - Beam containment status display and control
    - Top-off status monitor
    - Machine protection system display and control
- :hla:`Accelerator parameter store/restore (*)`
    - :hla:`manage, editing capability for stored accelerator status.`
    - :hla:`smoothly ramp from one stage to another.`
    - :hla:`smooth ramping of one set of magnets (PVs)`
    - :hla:`compare two stages, online and saved data, two data file.`
- Temperature monitoring display
    - Tunnel air temperature and humidity monitor
    - Water colling system display
    - magnet and crygenics temperature display
- Injection Control
- Front-end monitoring and control
- Scraper and movable mask operations
- :hladone:`General high level element control (GUI)`  

Beam Diagnostics
------------------------------

- :hladone:`Measure the orbit response matrix, with flexible number of BPMs and correctors.`  (L.Yang)
    - :hladone:`Import/Export orbit response matrix for orbit correction`
    - :hla:`Import/Export ORM for feedback`

- :hla:`Beam orbit display`. (L.Yang)
    - :hladone:`display closed orbit (static), 1Hz rate`
    - :hladone:`turn by turn bpm reading (including single turn)` (Y.Hu)
    - :hla:`single turn` (Y.Hu)
    - :hla:`Plot orbit change from now on.`
    - :hladone:`BPM status information`
    - :hla:`difference (referecne orbit display)`
    - :hla:`Orbit statistics. stability, especially drift and variation,
      variation`
    - :hla:`BPM testing stability, polarity.`
    - BPM current dependency, resolution.
    - :hla:`Absolute orbit offset and orbit offset with respect to golden
      orbit`

- :hla:`Static beam orbit control` (L.Yang)
    - :hla:`Edit golden orbit control (also affect feedback system)`
        - Interplay with feedback system when creating local bump: update
          the reference orbit to feedback.

    - :hladone:`Correct static orbit with selected correctors and BPMs`
    - :hladone:`Enable/disable BPMs for orbit correction and feedback.`
    - :hladone:`Enable/disable correctors for orbit correction and feedback`

- :hla:`Turn-by-turn BPM data` 
    - :hla:`closed orbit established using corrector and single shot BPM
      data`
    - :hladone:`get/plot turn-by-turn BPM signal, including orbit and sub/diff`
    - :hla:`Realtime tune based on turn-by-turn BPM`
    - :hladone:`BPM buttons readout.`
    - :hla:`Correct orbit based on single shot orbit`

- :hla:`Beam current history and lifetime display` (Y.Hu, L.Yang)
- :hla:`Bunch intensity display and history display/analysis (*)` (Y.Hu, L.Yang)
- :hla:`Beam emittance display (*)` (Y.Hu, L.Yang)
- :hla:`Injection element display and control page (*)` (G.Wang)
- :hla:`Injection efficiency` (G.Wang)
- :hla:`Injection filling pattern` (G.Wang, Y.Hu)
- Timing system display and control 
- Synchronization system display and control
- :hla:`Tune display and control (*)` (Y.Hu)
    - horizontal/vertical tune number, 1Hz update
    - FFT of turn by turn BPM data, choice of any live BPM.
    - 2D tune footprint with resonance lines

- :hla:`Beam profile: current, size, rms, center, image.` (Y.Hu, etc.)
- :hla:`Bunch length and profile if it is available (*)` (Y.Hu, etc.)
- :hla:`Measure BPM linearity` (Y.Hu, etc.)
- Bad BPM identification should be done in other application. Data
  synchronization to be done in low level server part.




Injector
----------

Software routines needed for the injector commissioning and operation are
listed in this section. Some of these routines will be delivered by linac
and booster vendors, others have to be developed by ourselves.

see Injector HLA specifications `<http://www.bnl.gov/>`_

- Linac
    - Diagnostics calibration
    - Routines for optimization of linac performance
    - Energy feedback
    - Charge feedback
    - Specification of bunch train format    
    - Beam loading compensation      
    - Energy measurement     
    - Energy spread measurement      
    - Emittance measurement (3 screens)      
    - Emittance measurement (quad scans)     
    - Matching of Twiss parameters into booster septum       
    - Beam stacking  
    - Beam transmission optimization 
    - TL quad centering      
    - Integration of safety devices/interlocks       

- Booster
    - Diagnostics calibration       
    - Orbit correction       
    - Tune measurement system
    - Energy measurement     
    - Momentum compaction measurement
    - Emittance measurements 
    - Beam stacking  
    - Extraction optimization
    - Ramp optimization      
    - LOCO-type machine characterization     
    - MIA in transport line -    - booster acceptance testing
    - Orbit feedback 
    - Synchrotron Radiation diagnostics      
    - Bunch cleaning system  
    - TL quad centering      
    - Integration of safety devices/interlocks       


Beam Based Alignment (BBA) (L.Yang)
-------------------------------------------

BBA use a list of correctors, BPMs and nearby quadrupoles, to steer the
beam through center of these quadrupoles. The input is a list of
corrector-BPM-quadrupole triplets.  The BPMs in corrector-BPM-quadrupole
triplet is a subset of live BPM.  This needs to get the golden orbit, set
the golden orbit, line fitting, step the quadrupole, step the corrector
(this can be a "macro step", e.g. 10 times than normal step size). Many
raw data needs to be saved in certain format: Python binary, HDF5 or
Matlab.

We would prefer to have all data saved, corrector settings/readings, BPM
readings and Quadrupole settings/readings.

The measurement and analysis can be separated conceptually, which makes
the post processing< easier, i.e. we can analyze any historical data,
and replay them.

It should work on separate set of quadrupoles, and combine data with
previous measurement.

Linear Lattice Fitting (LOCO) (J.Choi)
---------------------------------------------

- analyze quadrupole gradient/tilt error.
- analyze BPM gain/tilt error.

It requires:

- Designed orbit response matrix (ROM)
- change specified correctors 
- get closed orbit change at specified BPM
- :hladone:`Simulator and interface to Python`. This is required for online
  lattice fitting, e.g. LOCO. Tacy-v3 will be a choice.



Measure TWISS Parameters (L.Yang)
----------------------------------------

- measure beta functions
- measure dispersion
- measure chromaticity
- measure coupling
- measure coupling response matrix
- Measure and adjust tune. (tune scan ?)
- Measure and correct the chromaticity (linear and nonlinear). 
- Measure beam optics including phase advance, beta functions, dispersion.
- Dispersion measurement and correction, optimal set of quads



Insertion Device Related (Matching)
-------------------------------------------

- get/correct closed orbit distortion
- get/correct phase distortion
- get/correct coupling distortion



Beam Commissioning Activities
------------------------------

As a check, these activities will use HLA implemented above.

- Injection
    - Closed bump optimization: A and t
    - Simultaneous measurements of injected/stored beam orbits

- Hardware/Control checking and testing
    - Check polarity of all magnets.
    - Orbit corrector polarity and strength test, 
    - Magnetic field measurement and modeling, determine calibration
    - Verify named devices in control system, control proper hardware
    - Complete survey of magnetic elements
    - Test diagnostic equipment without beam
    - BTS transport line
	- Obtain good transmission through septum and good transverse phase
	  space match, set timing of pulsed magnets.

- Insertion Device
    - When necessary compensate the linear optics for ID
    - Observe orbit and tune shift vs gap
    - Measure lifetime vs gap
    - Observe beam stability vs current
    - Measure change in impedance due to ID chamber
    - Prepare look-up tables for feed forward orbit correction coils.
    - Measure effect on tune shift with amplitude, chromaticity, and emittance
      coupling.
    - Measure impedance vs gap for IVUs
    - Commission undulator gap control for users
    - Measure flux and brightness

- Misc
    - Test fast orbit feedback system.
    - Look for magnet errors that may have been missed in testing.
    - Obtain first turn in storage ring using single kicker
    - Use flag to obtain beam size information at injection point and
      after one turn.
    - Beam based alignment of sextupoles.
    - Develop lattice model using measured fields, linear/nonlinear optics.
    - Reduce beta beat
    - Correct coupling using skew quadrupoles, local and global.
    - Analysis on nonlinear dynamics.
    - Use pinger to measure tune shift with amplitude, dynamic aperture
      and characterize sextupole distribution
    - Wakefield modeling and tracking studies, develop model for
      impedance and wakefields, caculation and measurement, estimate
      instability thresholds, simulate bunch-by-bunch feedback with
      realistic bunches and wakefields.
    - Characterize ring impedance using beam.
    - Commission loss control minitoring system
    - Use visible synchrotron light monitor to study transverse beam
      profile and disturbance due to kickers. *getBeamProfile*
    - Study lifetime versus vacuum pressure, vertical beam size, scraper,
      dynamic aperture.
    - Commission transverse bunch-by-bunch feedback
    - Measure variation of coherent tune with current
    - Study increasing chromaticity from +2/+2 to +5/+5
    - Commission undulator gap control in control room
    - Calibration/Testing of Equipment Protection Interlock System
	- Center photon beam in exit slot
	- Verify gap open/close status is properly reported to interlock system
	- Measure interlock BPM offset and scale factors.
	- Adjust the hardware trip points on the local logic chassis
	- Verify beam is dumped at the specified position offsets.
	- Set the values in the interlock test file
	- Verify the proper operation of the interlock test
    - Top-off Injection
	- Check position of apertures in ring and beamline
	- Test interlocks
	- Characterize injection transient on transverse orbit, contribution
	  from septum and kickers.
	- Test transverse feedback with injection transient
    - Concerns: accuracy of magnet calibration-two types of dipoles, magnetic
      field quality (IRMIS data).
    - PBPM matching. Read both BPM and PBPM, and use BPM to benchmark the
      PBPM values.
    - Get groud motion and chamber motion if there are available readings.
    - Monitor beam loss. Get loss monitor readings from beam containment
      system (beam loss monitor).
    - Identify MPS (magnet power sypply) ripples.
    - Mechanical utilities status and controls
    - Electrical utilities status and controls
    - Equipment enclosure monitor
    - Controls network monitor

