# Add C29 SXN/ARI EPUs to aphla v2 Database

Detailed PV mappings, archive recommendations, MASAR scope, and implementation
reference material are maintained in
[`C29_SXN_ARI_REFERENCE.md`](C29_SXN_ARI_REFERENCE.md).

## Parameters

| Parameter | Value |
|-----------|-------|
| Cell number | 29 |
| Elements added | `epu50g1c29u`, `epu70g1c29d`, `pu1g1c29a`, `pu2g1c29a`, `pu3g1c29a`, `pu4g1c29a` |
| Date started | 2026-06-23 |

## Element positions (from LTE; straight_sc = SR_CIRCUMF / 30 * 29)

From LTE script (`target_dse`/`target_dsc`); straight_sc = SR_CIRCUMF / 30 * 29.
(Straight center is 3.300 m from straight start in the ELEGANT lattice.)

| Element     | se from straight start [m] | L [m] | sc offset from straight_sc [m] | devname   |
|-------------|---------------------------|-------|-------------------------------|-----------|
| pu1g1c29a   | 1.056                     | 0     | -2.244 (target_dse)           | C29-BPM7  |
| epu50g1c29u | 3.076                     | 1.800 | -1.124 (target_dsc)           | —         |
| pu2g1c29a   | 3.296                     | 0     | -0.004 (target_dse)           | C29-BPM8  |
| pu3g1c29a   | 3.439                     | 0     | +0.139 (target_dse)           | C29-BPM9  |
| epu70g1c29d | 5.469                     | 1.820 | +1.259 (target_dsc)           | —         |
| pu4g1c29a   | 5.679                     | 0     | +2.379 (target_dse)           | C29-BPM10 |

## Confirmed inputs before implementation

For each EPU (EPU50 and EPU70):

**Gap axis**
- Gap setpoint, readback, trigger, and speed PVs — collected.
- Hi/lo nominal gap readback PVs and values — collected.
- Gap/phase moving-status readback PVs — collected:
  `SR:C29-ID:G1:{EPU50:1}:STATE` and
  `SR:C29-ID:G1:{EPU70:2}:STATE`. Value 1 is idle; value 2 is moving, for
  either gap or phase motion.
- (Hi/lo limits derived from setpoint `.DRVH`/`.DRVL`)

**Phase axis**
- Phase setpoint and readback PVs — collected.
- The gap trigger also starts phase motion, although phase begins moving later.
  No dedicated phase-speed PV exists; use the gap speed PV for phase speed.

**EPU mode (mechanical)**
- Mode setpoint and readback PVs — collected.
- C29 enum values are 0=`None`, 1=`Parallel TOBI`, 2=`Parallel TIBO`,
  3=`Antiparallel TOBI`, and 4=`Antiparallel TIBO`. Values 1–4 are the four
  valid operating modes; value 0 is the inactive/unlabeled state.

**Corrector channels** (cch0–cch3)
- Current setpoint and readback PVs — collected for four channels per EPU.

**Orbit feedforward** (orbff0–orbff3)
- Enable, gap/phase/current lookup-table, and output PV patterns — proposed
  from existing C02/C21/C23 mappings. Orbit uses `-FF:<i>`; current strips
  use `-FFCS:<i>`. Both use suffixes `.F/.G/.H`, `.I/.J/.K`, `.L/.M/.N`,
  `.O/.P/.Q` for slots `m0`–`m3`.
- The `.C/.D` pattern seen for one-dimensional devices is the gap/current
  layout. The `.F/.G/.H` pattern is used when there are two lookup
  coordinates, such as EPU gap/phase or IVU gap/taper. This distinction is
  independent of orbit versus current-strip feedforward.
- C29 mode readback mapping: value 1 selects `.F/.G/.H`, value 2 selects
  `.I/.J/.K`, value 3 selects `.L/.M/.N`, and value 4 selects `.O/.P/.Q`.
- The feedforward IOC owner accepted the proposed C29 PV names.

**Current strips** (cs0–cs19; 20 channels per EPU)
- Setpoint and readback PVs — collected for 20 channels per EPU using
  one-based C29 fields `csch1`–`csch20`.

**Current strip feedforward** (csff*)
- PV naming pattern proposed; current-strip controller indices are `FFCS:0`–
  `FFCS:19`, corresponding to `csch1`–`csch20`.

**unitconv type**
- Gap/phase PVs are in µm; both EPUs use type 2.

## Progress

The database implementation, production update, JSON regeneration, and live
aphla validation are complete. Pending current-strip power-supply limits are
needed for MASAR CID 85, not for the C29 database mapping. Archiver
registration and the later controlled-motion test are external follow-ups.

- [x] Step 1 — Gather parameters
- [x] Step 2 — Back up production files
- [x] Step 3 — Sync JSON snapshot (if needed) — verified in sync, skipped
- [x] Step 4 (skeleton) — Write update function — add_C29_SXN_ARI_IDs(); EPU PVs intentionally deferred during data collection
- [x] Step 5 — Add to `_FUNCTIONS` and run — initial skeleton added 2026-06-23; complete PV mapping run with `exist_ok=True` on 2026-09-10
- [x] Step 6 — Add unit conversion entries
- [x] Step 7 — Run update script
- [x] Step 8 — Copy unitconv to production
- [x] Step 9 — Regenerate JSON snapshot
- [x] Step 10 — Commit

## Notes

- 2026-08-28 — Resumed to fill `id_pvs` (the skeleton was `{}` at that time,
  before the September completion). Detailed
  PV mappings and the implementation reference are maintained in
  `db_update/C29_SXN_ARI_REFERENCE.md`.

- 2026-09-09 — Began read-only PV data collection before implementation.
  Verified gap and phase PVs for SXN/ARI, including limits, speeds, and nominal
  gap values. Verified mode labels: 1=`Parallel TOBI`, 2=`Parallel TIBO`,
  3=`Antiparallel TOBI`, and 4=`Antiparallel TIBO`; 0 is the unlabeled
  inactive state. Corrector and SXN current-strip
  setpoint limit fields currently return zero; the authoritative orbit
  corrector limits were later confirmed as -10 A to +10 A, while current-strip
  limits remain unknown.
  Confirmed existing aphla current-strip indexing is hardware-dependent: C02
  and C21 use `csch1`–`csch18`, while C23 uses `csch0`–`csch19`. C29 will use
  the one-based convention `csch1`–`csch20`; both SXN and ARI collections are
  complete.

- 2026-09-09 — Clarified mechanical EPU enum values versus feedforward table
  slots. In the aphla/feedforward configuration, `m0`–`m3` are generic
  feedforward table-slot indices; they are not guaranteed to equal the EPICS
  `SET_MODE` enum values. Existing configurations allow device-specific
  subsets: C02 `[1, 2]`, C07 `[0, 1, 2, 3]`, C21 upstream `[1]`, C21
  downstream `[1, 2]`, and C23 upstream/downstream `[0, 1, 2, 3]`.
  C29’s EPICS labels are value 0=`None`, 1=`Parallel TOBI`, 2=`Parallel TIBO`,
  3=`Antiparallel TOBI`, and 4=`Antiparallel TIBO`. The corresponding
  lookup-table sets are `.F/.G/.H`, `.I/.J/.K`, `.L/.M/.N`, and `.O/.P/.Q`.

- 2026-09-09 — Documented the feedforward control inputs. For SXN, the
  feedforward system should use gap readback
  `SR:C29-ID:G1:{EPU50:1}:GAP:ACT` and phase readback
  `SR:C29-ID:G1:{EPU50:1}:PHASE:RBV`. For ARI, use gap readback
  `SR:C29-ID:G1:{EPU70:2}:GAP:ACT` and phase readback
  `SR:C29-ID:G1:{EPU70:2}:PHASE:RBV`. These readbacks are the independent
  variables used to select or interpolate the corrector and current-strip
  current setpoints; the command/setpoint PVs are not the feedback inputs.

- 2026-09-09 — Confirmed the mode readback PVs and lookup-table selection.
  SXN uses `SR:C29-ID:G1:{EPU50:1}:PHASE:STATE`; ARI uses
  `SR:C29-ID:G1:{EPU70:2}:PHASE:STATE`. Readback values 1, 2, 3, and 4 select
  the first, second, third, and fourth lookup-table sets (`.F/.G/.H`,
  `.I/.J/.K`, `.L/.M/.N`, and `.O/.P/.Q`), respectively.

- 2026-09-09 — Confirmed the orbit-corrector power-supply current limits:
  -10 A to +10 A for all four channels on both C29 EPUs. Current-strip
  power-supply limits remain unknown.

- 2026-09-10 — Confirmed the C29 moving-status behavior. `STATE` is 1 while
  idle and 2 while either gap or phase is moving. The same motion trigger
  starts both axes, with phase motion delayed relative to gap motion. No
  dedicated phase-speed PV was found; phase uses the gap speed PV.

- 2026-09-10 — The ID expert adjusted readback update rates to 10 Hz while
  moving and 2 Hz while idle. A phase readback of zero has a frozen timestamp;
  nonzero phase readbacks continue updating. These IOC update rates are the
  initial archive targets; a controlled C29 motion test should verify the
  effective archive behavior after registration.

- 2026-09-10 — Inspected the `aphla-id-orb-fdfrwrd` repository.
  The measurement/table-generation code uses gap and phase readbacks,
  configured triggers, readback tolerances, and fixed settling delays; it does
  not reference an ID moving-status PV. The live feedforward IOC itself is not
  present in that repository. The feedforward IOC owner accepted the proposed
  C29 PV names.

- 2026-09-10 — Direct `arget` archive checks found archive records for the C29
  SXN and ARI gap readbacks, but no points for the sampled C29 phase,
  corrector, or current-strip readbacks over seven days. Moving the C29 IDs
  will not create archive coverage for PVs that are not configured in the
  archiver; archiver registration must be handled first.
- 2026-09-10 — Archiver channel search found only the C29 `GAP:ACT` channel
  under the collected C29 ID namespaces. The other collected C29 ID scalar
  channels, corrector channels, current-strip channels, and feedforward enable
  channels were not found. Lookup-table channels were intentionally excluded
  because MASAR stores them.
- 2026-09-10 — Existing-device archive checks showed sparse idle behavior: C21
  gap and phase readbacks each had one point in the sampled 24-hour window; a
  C21 feedforward enable had records. C21 current-strip setpoints/readbacks
  are registered in the archive (`SR:C20-MG{PS:EPU_1}U1-I-SP` and
  `SR:C20-MG{PS:EPU_1}U1-I-I`, with the analogous U1–U6 channels for its
  current strips). The optional `U<n>-V-I` voltage readbacks may also be
  archived for electrical-engineering purposes. Lookup-table PVs are
  intentionally not archive targets
  because MASAR captures their values. A C23 current-strip readback returned
  only a disconnect record and one value, but C23 current strips are not used
  operationally and are not a useful C29 precedent. The word “sampled” means
  that only representative PVs were queried, not every C29 PV.
- 2026-09-10 — Archive scope was clarified: all new setpoint PVs should be
  archived on change; lookup-table PVs should not be archived because MASAR
  captures their values. Readback PVs require rate/storage recommendations
  based on moving and idle behavior.
- 2026-09-10 — Existing-ID comparison found C21 scalar axis, corrector, and
  feedforward-enable channels registered in the archiver. C21 current-strip
  setpoints/readbacks are also registered using `U<n>-I-SP` and `U<n>-I-I`.
  The optional `U<n>-V-I` voltage readbacks may also be archived for
  electrical-engineering purposes, but `U<n>-I-I` is the operations and
  accelerator-physics current readback.
  C23 current-strip setpoints/readbacks are also registered, but those channels
  are not used operationally. The C29 archive-registration matrix should
  therefore use C21 as the main precedent and C23 only as a
  channel-registration reference.
- 2026-09-10 — MASAR scope was identified: update CID 85
  (`ID_MPS_Limits_20210212`) for all orbit-corrector/current-strip power
  supply `.DRVH`/`.DRVL` limits; CID 74 (`Orbit_Feedforward`) for C29 orbit
  lookup tables; and CID 73 (`CS_FeedForward`) for C29 current-strip lookup
  tables. No additional required MASAR config was found in the available
  repositories. Current-strip limits remain pending from the ID Group.

- 2026-09-10 — Ran `add_C29_SXN_ARI_IDs(exist_ok=True)` from the `v2` branch,
  which updated both production `.pgz` variants. Copied the updated
  `nsls2sr_unitconv.yaml` to production and regenerated the repository JSON
  snapshot. The generated snapshot contains both C29 EPUs with the expected
  scalar, corrector, orbit-feedforward, current-strip, and current-strip
  feedforward mappings.

- 2026-09-10 — Verified live C29 aphla reads after correcting the EPU IOC PV
  prefix: a missing colon after each closing EPU brace was corrected before the
  successful rerun. Gap/phase scalar values, limits, speeds, and orbit-feedforward
  coordinate tables support `unitsys="phy"` in mm. For feedforward
  measurement/table generation, corrector/current-strip fields and current
  lookup tables are intentionally used with `unitsys=None`; their raw current
  units can vary by device. The resulting missing `None`-to-`phy` conversion
  is expected and does not block that workflow.

- 2026-09-10 — Added the manual live-EPICS validation command
  `pixi run python tests/live_test_c29.py`. It tests all supported C29
  readback/setpoint combinations and reports totals and failures only.
  Current-strip feedforward channels are included by default; while they are
  offline, `--exclude-csff` produced 348 passes, 520 CSFF skips, 156 expected
  raw-only (`no-phy`) skips, and no failures. Run the full test after CSFF
  channels are online.
