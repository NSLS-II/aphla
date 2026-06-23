# Add C29 SXN/ARI EPUs to aphla v2 Database

## Parameters

| Parameter | Value |
|-----------|-------|
| Cell number | 29 |
| Elements added | `epu50g1c29u`, `epu70g1c29d`, `pu1g1c29a`, `pu2g1c29a`, `pu3g1c29a`, `pu4g1c29a` |
| Date started | 2026-06-23 |

## Element positions (from LTE; straight_sc = SR_CIRCUMF / 30 * 29)

From LTE script (`target_dse`/`target_dsc`); straight_sc = SR_CIRCUMF / 30 * 29.
(Straight center is 3.300 m from straight start in the ELEGANT lattice.)

| Element     | se from straight start [m] | L [m] | sc offset from straight_sc [m] |
|-------------|---------------------------|-------|-------------------------------|
| pu1g1c29a   | 1.056                     | 0     | -2.244 (target_dse)           |
| epu50g1c29u | 3.076                     | 1.800 | -1.124 (target_dsc)           |
| pu2g1c29a   | 3.296                     | 0     | -0.004 (target_dse)           |
| pu3g1c29a   | 3.439                     | 0     | +0.139 (target_dse)           |
| epu70g1c29d | 5.469                     | 1.820 | +1.259 (target_dsc)           |
| pu4g1c29a   | 5.679                     | 0     | +2.379 (target_dse)           |

## Unknowns still needed

For each EPU (EPU50 and EPU70):

**Gap axis**
- Gap setpoint PV
- Gap readback PV
- Gap trigger ("start moving") PV
- Gap speed setpoint PV
- Gap speed readback PV
- Hi/lo nominal gap readback PVs
- Gap ramping status readback PV
- (Hi/lo limits derived from setpoint `.DRVH`/`.DRVL`)

**Phase axis**
- Phase setpoint PV
- Phase readback PV
- Phase trigger PV
- Phase speed setpoint PV
- Phase speed readback PV

**EPU mode (mechanical)**
- Mode setpoint PV (enum, e.g. 4 modes)
- Mode readback PV (enum)

**Corrector channels** (cch0–cch3)
- Current setpoint PV (per channel)
- Current readback PV (per channel)

**Orbit feedforward** (orbff0–orbff3)
- Enable setpoint PV
- Gap lookup table slot PV (`L2-Calc_` field letter varies by beamline)
- Phase lookup table slot PV
- Current setpoint PV (same as cch setpoint)

**Current strips** (cs0–cs19; 20 channels per EPU)
- Setpoint PV (per channel)
- Readback PV (per channel)

**Current strip feedforward** (csff*)
- PV names for feedforward table channels

**unitconv type**
- Are gap/phase PVs in mm (type1) or µm (type2)?

## Progress

- [ ] Step 1 — Gather parameters
- [x] Step 2 — Back up production files
- [x] Step 3 — Sync JSON snapshot (if needed) — verified in sync, skipped
- [ ] Step 4 — Write update function
- [ ] Step 5 — Flip if/elif block
- [ ] Step 6 — Add unit conversion entries
- [ ] Step 7 — Run update script
- [ ] Step 8 — Copy unitconv to production
- [ ] Step 9 — Regenerate JSON snapshot
- [ ] Step 10 — Commit

## Notes
