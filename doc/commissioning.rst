NSLS2 Beam Commissioning Plan and Tools
========================================

.. role:: hlawarn
.. role:: hla
.. role:: hladone
.. role:: hladetails

Without Beam
------------

    - Measure magnets to determine field quality
    - Determine calibration
    - Develop lattice model using measured fields.

       - Linear optics
       - Nonlinear optics

    - Inspect radiation shielding
    - Test personnel protection system
    - Test loss control monitoring system
    - Prepare, review, sign safety documentation
    - :hla:`Complete staff training`
    - :hla:`Verify that named devices in control system control proper hardware`
    - Check polarity of all magnets
    - :hlawarn:`Complete survey of magnetic elements`
    - Test diagnostic equipment without beam

Phase 1 - without ID
--------------------

    - Commission BTS transport line
        - obtain good transmission ghrough septum
 	- good transverse phase space match
	- set timing of pulsed magnets
	
    - Obtain first turn in storage ring using single/multiple kicker
        - :hla:`center beam in single downstream kicker`
	- :hla:`adjust kicker strength to place beam on design orbit`
	- :hla:`use single turn bpms to steer beam trajectory around ring and estimate linear optics and tune`
	- :hla:`use flag to obtain beam size information at injection point and after one turn`
	
    - look for magnet errors that may have been missed in testing.
    - achieve additional turns around ring
    - achieve circulating beam (hundreds of turns)
    - measure and improve orbit and tune
    - achieve RF capture (lifetime seconds to minutes)
    - measure and improve orbit and tune
    - obtain circulating beam using four kicker magnets to make local injection bump
    - achieve 1Hz accumulation of injected bunches into ring
    - commission loss control monitoring system
        - Monitor beam loss. :hladetails:`Get loss monitor readings from beam containment
          system (beam loss monitor)`.
    - use visible synchrotron light monitor to study transverse beam profile and disturbance due to kickers.
    - improve injection efficiency and RF capture
    - reduce beam loss due to kicker excitation
    - improve orbit and tune
    - improve lifetime
    - use pinhole camera to determine transverse profile energy spread.
        - beam emittance measurement.(subsystem)

    - measure orbit response matrix
    - use LOCO to characterize linear optics.
    - condition vacuum chamber with beam
    - achieve 25mA stored beam
    - study lifetime & vacuum pressure vs. amp-hrs
    - correct coupling using skew quadrupoles.
    - Measure dependence of lifetime on vertical beam size
    - using pinhole camera—estimate Touschek lifetime
    - Measure dependence of lifetime on position of beam scrapers to get information on physical and dynamic aperture
    - Refine LOCO characterization of linear optics
    - Carry out beam based alignment of BPMs
    - Test fast orbit feedback system
    - Characterize nonlinear optics
        - Determine nonlinear dispersion and chromaticity
	- Use Pinger to measure tune shift with amplitude, dynamic aperture and characterize sextupole distribution

    - Increase current
        - Study instability thresholds
	- Commission transverse bunch-by-bunch feedback
	- Measure variation of coherent tune with current
	- Characterize ring impedance using beam
	- Study increasing chromaticity from +2/+2 to +5/+5
	
    - Compare optics and wakefield models with measurements
        - Wakefield modeling and tracking studies, develop model for impedance
    	  and wakefields, caculation and measurement, estimate instability
    	  thresholds, simulate bunch-by-bunch feedback with realistic bunches
    	  and wakefields. (unknown to HLA yet)


Phase 2 - with IDs
---------------------

    - insertion device commissioning
        - Bake beamline equipment
	- Survey front end fiducial marks on the ID beamline
	- Commission undulator gap control in control room
	- Establish and save reference orbit (low current ~5mA)
	- ID front end radiation survey at low current (gap open)
	- ID front end radiation survey opening mask and valve
	- ID front end radiation survey increasing current (gap open)
	- ID front end radiation survey at intervals during vacuum conditioning of safety shutter
	- Establish ID elevation

    - Calibration/testing of  Equipment Protection Interlock System
        - Center photon beam in exit slot
	- Verify gap open/close status is properly reported to interlock system
	- Measure interlock BPM offset and scale factors
	- Adjust the hardware trip points on the local logic chassis
	- Verify beam is dumped at the specified position offsets
	- Set the values in the interlock test file
	- :hlawarn:`Set the values in the micro`
	- Verify the proper operation of the interlock test
	- ID front end radiation survey with gap closed (low current ~5mA)
	- When necessary, compensate linear optics for ID (orbit/tune correction, feedforward table, coupling)
	- Radiation survey with closed gap at progressively higher current—check for component heating
	- Observe orbit and tune shift vs gap
	- Measure lifetime vs gap
	- Observe beam stability vs current
	- Measure change in impedance due to ID chamber
	- Prepare look-up tables for feed forward orbit correction coils
	- Measure effect on tune shift with amplitude, chromaticity and emittance coupling
	- Measure impedance vs gap for IVUs
	- Commission undulator gap control for users
	- Measure undulator spectra vs gap
	- Measure flux and brightness

- Top-off Injection
    - Check position of apertures in ring and beamline
    - Test interlocks
    - Radiation survey with shutters open
    - Characterize injection transient on transverse orbit
        - Contribution from septum
        - Contribution from kickers
    - Test transverse feedback with injection transient


Misc 
------

:hladetails:`Some more work ...`

    - Closed bump optimization.
    - Simultaneous measurement of injected/stored beam orbits
    - Identify MPS (magnet power sypply) ripples.
    - Beam based alignment of sextupoles. 
    - Reduce beta beat.
    - PBPM matching. Read both BPM and PBPM, and use BPM to benchmark the
      PBPM values.
    - Concerns: accuracy of magnet calibration-two types of dipoles, magnetic
      field quality (IRMIS data).
    - Get groud motion and chamber motion if there are available readings.
    - Mechanical utilities status and controls
    - Electrical utilities status and controls
    - Equipment enclosure monitor
    - Controls network monitor

