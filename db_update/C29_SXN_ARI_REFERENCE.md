# C29 SXN/ARI EPU Database Reference

Detailed technical reference for the work tracked in
`db_update/PROGRESS_add_C29_SXN_ARI.md`.

## Reference status

- Skeletons for `epu50g1c29u`, `epu70g1c29d` + 4 UBPMs already committed
  (`df7ccc6`), `id_pvs={}` for both EPUs.
- Progress checklist: Steps 1–5, 9 done. Steps 6, 7, 8, 10 remain, and Step 4
  needs a follow-up edit (fill `id_pvs`, then re-run with `exist_ok=True`).
- The database implementation files remain unchanged in this documentation
  phase.
- Data collection is complete enough to begin implementation. Current-strip
  power-supply limits remain pending for MASAR CID 85 only; archiver
  registration and the later controlled motion test are external follow-ups
  and do not block the database changes.

## Collected PV names and implementation status

For **each** EPU — `epu50g1c29u` (SXN) and `epu70g1c29d` (ARI) — separately:

### Gap axis
- Setpoint PV, Readback PV
  - SXN (upstream) - SR:C29-ID:G1:{EPU50:1}:CMD:MOVE_GAP (unit: um), SR:C29-ID:G1:{EPU50:1}:GAP:ACT (unit: um)
  - ARI (downstream) - SR:C29-ID:G1:{EPU70:2}:CMD:MOVE_GAP (unit: um), SR:C29-ID:G1:{EPU70:2}:GAP:ACT (unit: um)
- Trigger ("start moving") PV
  - SXN (upstream) - SR:C29-ID:G1:{EPU50:1}:CMD:MOTION
  - ARI (downstream) - SR:C29-ID:G1:{EPU70:2}:CMD:MOTION
- Speed setpoint PV, Speed readback PV
  - SXN (upstream) - SR:C29-ID:G1:{EPU50:1}:CMD:SET_VELOCITY (unit: um/s), SR:C29-ID:G1:{EPU50:1}:CMD:SET_VELOCITY:RBV (unit: um/s)
  - ARI (downstream) - SR:C29-ID:G1:{EPU70:2}:CMD:SET_VELOCITY (unit: um/s), SR:C29-ID:G1:{EPU70:2}:CMD:SET_VELOCITY:RBV (unit: um/s)
- Hi/lo nominal gap readback PVs
  - SXN: `SR:C29-1-ID:NomOpen-Sp` = 220000 um and
    `SR:C29-1-ID:NomClose-Sp` = 12000 um.
  - ARI: `SR:C29-2-ID:NomOpen-Sp` = 220000 um and
    `SR:C29-2-ID:NomClose-Sp` = 11500 um.
- Ramping status readback PV
  - Confirmed moving-status PVs:
    - SXN - `SR:C29-ID:G1:{EPU50:1}:STATE`
    - ARI - `SR:C29-ID:G1:{EPU70:2}:STATE`
  - These are `1` when idle and `2` when moving. They report moving when
    either gap or phase, or both, are moving. Use these as the common
    gap/phase ramping-status PVs; there is no separate phase-ramping PV.
- (Hi/lo limits auto-derived from setpoint `.DRVH`/`.DRVL` — no need to supply)

### Phase axis
- Setpoint PV, Readback PV
  - SXN (upstream) - SR:C29-ID:G1:{EPU50:1}:CMD:SET_PHASE (unit: um), SR:C29-ID:G1:{EPU50:1}:PHASE:RBV (unit: um)
  - ARI (downstream) - SR:C29-ID:G1:{EPU70:2}:CMD:SET_PHASE (unit: um), SR:C29-ID:G1:{EPU70:2}:PHASE:RBV (unit: um)
- Trigger PV
  - Confirmed: the gap trigger PVs also start phase motion. Phase motion can
    begin noticeably later than gap motion after the trigger.
- Speed setpoint PV, Speed readback PV
  - No dedicated phase-speed PVs were found. Working mapping: use the same
    speed PVs as gap speed for phase speed.

### Mode (mechanical, enum)
- Setpoint PV, Readback PV
  - SXN (upstream) - SR:C29-ID:G1:{EPU50:1}:CMD:PHASE:SET_MODE, SR:C29-ID:G1:{EPU50:1}:PHASE:STATE
  - ARI (downstream) - SR:C29-ID:G1:{EPU70:2}:CMD:PHASE:SET_MODE, SR:C29-ID:G1:{EPU70:2}:PHASE:STATE
- Confirm number/names of enum states (e.g. 4 modes)
  - Confirmed enum values are 0=`None`/unlabeled, 1=`Parallel TOBI`,
    2=`Parallel TIBO`, 3=`Antiparallel TOBI`, and 4=`Antiparallel TIBO`.
    Values 1–4 are the four valid operating modes; value 0 is the inactive or
    unlabeled state.

### Corrector channels (cch0–cch3)
- Power supply PV identifier (`<PS_PV>` in template, e.g. `zPSC1`) for each EPU
- Confirm 4 channels each, per-channel setpoint/readback pattern matches
  `SR:C##-MG{<PS_PV>:ChanN}I-sp` / `SR:C##-MG{<PS_PV>}dcct1ADC:ChanN`

- SXN upstream (SP , RB)
  - SR:C29-MG{PS:EPU1-CRR}Chan1:DAC_SetPt-SP , SR:C29-MG{PS:EPU1-CRR}Chan1:DCCT1-I
  - SR:C29-MG{PS:EPU1-CRR}Chan2:DAC_SetPt-SP , SR:C29-MG{PS:EPU1-CRR}Chan2:DCCT1-I
  - SR:C29-MG{PS:EPU1-CRR}Chan3:DAC_SetPt-SP , SR:C29-MG{PS:EPU1-CRR}Chan3:DCCT1-I
  - SR:C29-MG{PS:EPU1-CRR}Chan4:DAC_SetPt-SP , SR:C29-MG{PS:EPU1-CRR}Chan4:DCCT1-I
- ARI downstream (SP , RB)
  - Same as SXN upstream except that "EPU1" must be replaced with "EPU2".
- All units are A (Ampere) for the PVs right above.
- Orbit-corrector power-supply current limits are confirmed to be -10 A to
  +10 A for all four channels on each EPU.
- Current-strip power-supply current limits are not yet available.
- The measurement/table-generation repository `aphla-id-orb-fdfrwrd` was inspected. It uses gap/phase readbacks, configured trigger PVs, readback tolerances, and fixed settling delays; it does not use an ID moving-status PV. The live feedforward IOC is not in that repository, so no feedforward-code change is indicated by this investigation.
- Also, we need to add the following step in this skill. MASAR CID 85 (ID_MPS_Limits_20210212) needs an update whenever we add the dedicated power supplies (PS) for orbit/current strip correction for new IDs like this case. Basically for each PS channel, I need to know the ".DRVH" and ".DRVL" values (must get them from ID Group). Then ask Yong Hu (or whoever in charge of the MASAR config update) to add these new DRV PVs to the MASAR config and capture the currently set values after I make sure the values are all correctly applied.
- The archive-registration request is an external follow-up. It does not block database implementation. After registration, perform a controlled C29 motion test to verify the effective archive behavior.

### Orbit feedforward (orbff0–orbff3)
- Enable setpoint PV
- Gap, phase, and current lookup-table PVs — use the verified EPU mapping
  `.F/.G/.H` for table slot `m0`, `.I/.J/.K` for `m1`, `.L/.M/.N` for `m2`,
  and `.O/.P/.Q` for `m3`.
- The orbit and current-strip suffix letters are the same. The namespaces are
  different: orbit uses `-FF:<i>`, while current strips use `-FFCS:<i>`.
- Existing aphla mappings for C02, C21, and C23 confirm this same suffix
  mapping for both namespaces.
- The alphabet layout reflects lookup dimensionality, not the orbit versus
  current-strip subsystem: one-dimensional gap/current tables use `.C` for
  gap and `.D` for current, while two-dimensional EPU gap/phase or IVU
  gap/taper tables use `.F` for the first coordinate, `.G` for the second,
  and `.H` for current. Additional table slots continue as `.I/.J/.K`,
  `.L/.M/.N`, and `.O/.P/.Q`.
- Beamline acronyms for C29 remain SXN and ARI as shown in the proposed
  prefixes below.

### Proposed C29 feedforward PV naming

This proposal is based on the loaded aphla mappings for existing EPUs. The
feedforward IOC owner accepted it for creating the C29 PVs.

There are two distinct feedforward namespaces:

- Orbit feedforward uses `-FF:<i>` and has four channels, indexed `i = 0..3`.
- Current-strip feedforward uses `-FFCS:<i>` and has twenty channels, indexed
  `i = 0..19`.

The FFCS index is zero-based even though C29 current-strip fields will be
one-based: `FFCS:0` corresponds to `csch1`, and `FFCS:19` corresponds to
`csch20`. Existing aphla mappings confirm this zero-based FFCS convention for
both 18-channel and 20-channel EPUs.

For orbit feedforward, use these prefixes:

```text
SXN: SR:C29-ID:G1A{EPU:1-FF:<i>}
ARI: SR:C29-ID:G1A{EPU:2-FF:<i>}
```

For each `i = 0..3`, create an enable PV and the feedforward-table lookup PVs.

Important: `m0`–`m3` are feedforward table-slot indices in the aphla
database. They must not be assumed to equal the EPICS mechanical-mode enum
values. The valid mechanical enum values are device-specific. The
feedforward IOC owner accepted the proposed C29 PV names and the mapping of
  mechanical modes 1–4 to the four table slots. Before commissioning, the
  live IOC behavior should still be tested against the actual readbacks:

```text
<prefix>Ena-Sel
<prefix>L2-Calc_.F   # m0 gap table slot
<prefix>L2-Calc_.G   # m0 phase table slot
<prefix>L2-Calc_.H   # m0 current table slot
<prefix>L2-Calc_.I   # m1 gap table slot
<prefix>L2-Calc_.J   # m1 phase table slot
<prefix>L2-Calc_.K   # m1 current table slot
<prefix>L2-Calc_.L   # m2 gap table slot
<prefix>L2-Calc_.M   # m2 phase table slot
<prefix>L2-Calc_.N   # m2 current table slot
<prefix>L2-Calc_.O   # m3 gap table slot
<prefix>L2-Calc_.P   # m3 phase table slot
<prefix>L2-Calc_.Q   # m3 current table slot
```

The orbit output fields should write to the four C29 corrector setpoints:

```text
SXN orbff0_output: SR:C29-MG{PS:EPU1-CRR}Chan1:DAC_SetPt-SP
SXN orbff1_output: SR:C29-MG{PS:EPU1-CRR}Chan2:DAC_SetPt-SP
SXN orbff2_output: SR:C29-MG{PS:EPU1-CRR}Chan3:DAC_SetPt-SP
SXN orbff3_output: SR:C29-MG{PS:EPU1-CRR}Chan4:DAC_SetPt-SP

ARI orbff0_output: SR:C29-MG{PS:EPU2-CRR}Chan1:DAC_SetPt-SP
ARI orbff1_output: SR:C29-MG{PS:EPU2-CRR}Chan2:DAC_SetPt-SP
ARI orbff2_output: SR:C29-MG{PS:EPU2-CRR}Chan3:DAC_SetPt-SP
ARI orbff3_output: SR:C29-MG{PS:EPU2-CRR}Chan4:DAC_SetPt-SP
```

The feedforward systems should use the actual gap and phase readbacks as their
independent variables when selecting or interpolating the current setpoints:

| EPU | Gap readback | Phase readback |
|---|---|---|
| SXN (`epu50g1c29u`) | `SR:C29-ID:G1:{EPU50:1}:GAP:ACT` | `SR:C29-ID:G1:{EPU50:1}:PHASE:RBV` |
| ARI (`epu70g1c29d`) | `SR:C29-ID:G1:{EPU70:2}:GAP:ACT` | `SR:C29-ID:G1:{EPU70:2}:PHASE:RBV` |

For each EPU, the feedforward logic should read the corresponding gap and
phase readbacks, then determine the required corrector or current-strip
currents from the selected feedforward tables. The command/setpoint PVs are
not the feedback inputs for this purpose.

The mechanical-mode readback PVs are:

- SXN: `SR:C29-ID:G1:{EPU50:1}:PHASE:STATE`
- ARI: `SR:C29-ID:G1:{EPU70:2}:PHASE:STATE`

Lookup-table selection is:

- Mode readback `1` (`Parallel TOBI`): first set, `.F/.G/.H`.
- Mode readback `2` (`Parallel TIBO`): second set, `.I/.J/.K`.
- Mode readback `3` (`Antiparallel TOBI`): third set, `.L/.M/.N`.
- Mode readback `4` (`Antiparallel TIBO`): fourth set, `.O/.P/.Q`.

For current-strip feedforward, use:

```text
SXN: SR:C29-ID:G1A{EPU:1-FFCS:<i>}
ARI: SR:C29-ID:G1A{EPU:2-FFCS:<i>}
```

with `i = 0..19`. Each prefix gets `Ena-Sel` and the same `L2-Calc_` suffix
mapping above. The corresponding aphla fields are `csff<i>_on`,
`csff<i>_m<slot>_gap`, `csff<i>_m<slot>_phase`, and `csff<i>_m<slot>_I`,
where the table set is selected by the mechanical-mode readback as described
above.

### Mechanical enum versus feedforward table slots

Existing feedforward configurations confirm that valid mechanical modes are
device-specific, while the database/feedforward field naming remains generic
with slots `m0`–`m3`:

- C02 EPU: valid mechanical modes `[1, 2]`.
- C07 EPU: valid mechanical modes `[0, 1, 2, 3]`.
- C21 upstream EPU: valid mechanical mode `[1]`.
- C21 downstream EPU: valid mechanical modes `[1, 2]`.
- C23 upstream and downstream EPUs: valid mechanical modes `[0, 1, 2, 3]`.
- C29 SXN and ARI: EPICS enum labels show value 0=`None`, 1=`Parallel TOBI`,
  2=`Parallel TIBO`, 3=`Antiparallel TOBI`, and 4=`Antiparallel TIBO`.

C02 is a direct precedent for an EPU whose usable mechanical enum values are
only a subset of the available lookup-table sets. For C29, enum values 1–4
select all four lookup-table sets as documented above.

### Feedforward repository investigation

The local repository `/nsls2/users/yhidaka/git_repos/aphla-id-orb-fdfrwrd`
was inspected. It is primarily measurement, table-generation, and validation
code rather than the live feedforward IOC implementation.

- It obtains gap and phase values through aphla readbacks and waits for
  readback tolerances after state changes.
- It uses fixed `extra_ID_state_change_wait` delays (existing configurations
  range from 0 to 10 seconds) and does not reference an ID moving-status PV.
- The measurement code uses the configured gap/phase trigger fields; C29's
  single motion trigger is therefore appropriate for both axes.
- The new C29 `STATE` PVs are useful as the database `gap_ramping` status
  fields, but no evidence was found that this repository requires them.
- The delayed phase response means C29 commissioning should verify that the
  fixed settling delay is long enough after a combined gap/phase move.

### Current strips (cs0–cs19, 20 channels per EPU)
- Confirm channel count (may not be 20 for both)
  - 20 channels for both SXN and ARI.
- Setpoint PV + readback PV per channel, per EPU
  - SXN upstream
    - Coil 1 - SR:C29-MG{PS:EPU1-S1}Chan1:DAC_SetPt-SP , SR:C29-MG{PS:EPU1-S1}Chan1:DCCT1-I
    - Coil 2 - SR:C29-MG{PS:EPU1-S1}Chan2:DAC_SetPt-SP , SR:C29-MG{PS:EPU1-S1}Chan2:DCCT1-I
    - ...
    - Coil 4 - SR:C29-MG{PS:EPU1-S1}Chan4:DAC_SetPt-SP , SR:C29-MG{PS:EPU1-S1}Chan4:DCCT1-I
    - Coil 5 - SR:C29-MG{PS:EPU1-S2}Chan1:DAC_SetPt-SP , SR:C29-MG{PS:EPU1-S2}Chan1:DCCT1-I
    - ...
    - Coil 8 - (S2-Chan4)
    - Coil 9 - (S3-Chan1)
    - ...
    - Coil 12 - (S3-Chan4)
    - Coil 13 - (S4-Chan1)
    - ...
    - Coil 16 - (S4-Chan4)
    - Coil 17 - (S5-Chan1)
    - ...
    - Coil 20 - (S5-Chan4)
  - ARI downstream
    - Same pattern, with `EPU2` replacing `EPU1`; the 20 ARI readbacks were
      also collected.

All units are A (Ampere) for the PVs right above.

### Current strip feedforward (csff*)
- Proposed PV pattern is documented in the “Proposed C29 feedforward PV
  naming” section above; it follows the existing `FFCS:0..19` convention.

### Unit conversion type (Step 6, `v2tests/nsls2sr_unitconv.yaml`)
- Both C29 EPUs use microns (um), so both belong in the type-2 conversion
  entries.

### Readback update and archive observations

- The ID expert changed moving gap/phase readbacks to update at 10 Hz
  (0.1-second period), slowing to 2 Hz (0.5-second period) while idle.
- A phase readback equal to zero does not update and its timestamp remains
  frozen; nonzero phase values continue to update at the observed idle rate.
  This needs to be considered when validating phase-readback freshness.
- Existing-ID archive queries were performed with `arget`. The observed archive
  behavior is event/update driven rather than a simple fixed-rate stream:
  idle gap readbacks can be sparse, while active current readbacks can appear
  near 10 Hz. The initial C29 request should follow the confirmed IOC behavior:
  10 Hz while moving and 2 Hz while idle for ID readbacks, with about 10 Hz
  while changing and a lower idle rate for corrector/current-strip readbacks.
  A controlled C29 motion test should verify the effective rates after the
  archiver owner registers the PVs.

- Archive scope clarification: lookup-table PVs are not scalar operating data
  and must not be archived. Their values are captured with MASAR instead.
- All new setpoint PVs should be archived on change, including the C29 ID,
  corrector, current-strip, and feedforward control setpoints. Readback PVs
  require a separate rate/storage decision.

- 2026-09-10 — Direct `arget` checks of the live archive showed that C29 SXN
  and ARI gap readbacks each have archive data, but the sampled C29 phase
  readbacks and sampled C29 corrector/current-strip readbacks returned no
  points in the seven-day query. Moving C29 cannot by itself create archive
  coverage for PVs that are not configured in the archiver.
- 2026-09-10 — Archiver channel search narrowed that result: for both C29
  EPUs, the only matching ID channel found under the collected ID namespace
  was `GAP:ACT`. No collected C29 ID setpoint, phase, motion/status, mode,
  corrector, current-strip, or feedforward-enable channel was found by the
  search. The feedforward lookup-table channels were intentionally excluded
  from this search because MASAR, not the archiver, stores them.
- 2026-09-10 — Existing-device comparison: C21 gap/phase scalar setpoints,
  readbacks, and related scalar axis fields are registered; its orbit and
  current-strip feedforward enable PVs are registered, while lookup-table PVs
  are not. C21 corrector and current-strip setpoint/readback channels are
  registered. C23 current-strip setpoint/readback channels are also
  registered, although their sparse activity is not a useful operational
  precedent for C29.
- 2026-09-10 — Representative existing-device checks showed sparse idle
  records: C21 gap and phase readbacks each had only one point in the sampled
  24-hour window. Here, “representative” means only selected PVs were queried,
  not that every C29 PV was checked. A C21 feedforward enable PV had records;
  its lookup-table current PV is intentionally outside the archive scope. A
  C23 current-strip readback returned a disconnect record and one value, but
  C23 current strips are not used operationally and are not a useful precedent
  for C29. These observations are evidence about effective archive behavior,
  not proof of the configured capture period.
- 2026-09-10 — The site `arget` client was used directly because the repository
  `aphla.getArchiverData()` helper currently fails under Python 3 when writing
  its temporary PV list.

### Archive inventory and recommendations

The archive target is every collected scalar setpoint PV and every
collected hardware readback PV. Lookup-table PVs are excluded and are saved by
MASAR. The feedforward `*_output` fields are mappings to hardware setpoints,
not additional PVs.

| C29 category | Current archive result | Initial recommendation |
|---|---|---|
| ID gap/phase and motion scalar setpoints | Only `GAP:ACT` was found; other collected channels were not found | Register all setpoints on change; register readbacks with motion-aware rate |
| ID gap/phase readbacks | Gap readback found; phase readbacks not found | 10 Hz while moving, 2 Hz while idle, subject to storage review |
| ID state/mode/status readbacks | Not found | State/mode on change; motion status on change (or low-rate while moving) |
| Orbit-corrector setpoints/readbacks | Not found | Setpoints on change; readbacks 10 Hz while changing and lower idle rate |
| Current-strip setpoints/readbacks | Not found | Setpoints on change; readbacks 10 Hz while changing and lower idle rate |
| Feedforward enable PVs | Not found | Archive on change |
| Feedforward lookup tables | Excluded by design | Capture with MASAR |

### Full C29 archive-registration inventory (grouped)

`FOUND` means the exact PV was found by the live archiver channel search. `NOT FOUND` means it should be sent to the archiver owner for registration. The status applies to the entire block unless stated otherwise. Lookup-table PVs are omitted because MASAR stores them. `.DRVH`/`.DRVL` limit metadata is not included as an operational archive target.

#### SXN — ID setpoints
Status: NOT FOUND. Recommendation: archive on change.
```text
SR:C29-ID:G1:{EPU50:1}:CMD:MOVE_GAP
SR:C29-ID:G1:{EPU50:1}:CMD:MOTION
SR:C29-ID:G1:{EPU50:1}:CMD:SET_VELOCITY
SR:C29-ID:G1:{EPU50:1}:CMD:SET_PHASE
SR:C29-ID:G1:{EPU50:1}:CMD:PHASE:SET_MODE
SR:C29-1-ID:NomOpen-Sp
SR:C29-1-ID:NomClose-Sp
```

#### SXN — ID readbacks
Recommendation: gap/phase readbacks at 10 Hz while moving and 2 Hz while idle; status/mode readbacks on change.
```text
SR:C29-ID:G1:{EPU50:1}:GAP:ACT  # FOUND
SR:C29-ID:G1:{EPU50:1}:CMD:SET_VELOCITY:RBV
SR:C29-ID:G1:{EPU50:1}:STATE
SR:C29-ID:G1:{EPU50:1}:PHASE:RBV
SR:C29-ID:G1:{EPU50:1}:PHASE:STATE
```

#### SXN — orbit-corrector setpoints
Status: NOT FOUND. Recommendation: archive on change.
```text
SR:C29-MG{PS:EPU1-CRR}Chan1:DAC_SetPt-SP
SR:C29-MG{PS:EPU1-CRR}Chan2:DAC_SetPt-SP
SR:C29-MG{PS:EPU1-CRR}Chan3:DAC_SetPt-SP
SR:C29-MG{PS:EPU1-CRR}Chan4:DAC_SetPt-SP
```

#### SXN — orbit-corrector readbacks
Status: NOT FOUND. Recommendation: archive at a rate appropriate for changing currents; use 10 Hz while changing as the initial target.
```text
SR:C29-MG{PS:EPU1-CRR}Chan1:DCCT1-I
SR:C29-MG{PS:EPU1-CRR}Chan2:DCCT1-I
SR:C29-MG{PS:EPU1-CRR}Chan3:DCCT1-I
SR:C29-MG{PS:EPU1-CRR}Chan4:DCCT1-I
```

#### SXN — current-strip setpoints
Status: NOT FOUND. Recommendation: archive on change.
```text
SR:C29-MG{PS:EPU1-S1}Chan1:DAC_SetPt-SP
SR:C29-MG{PS:EPU1-S1}Chan2:DAC_SetPt-SP
SR:C29-MG{PS:EPU1-S1}Chan3:DAC_SetPt-SP
SR:C29-MG{PS:EPU1-S1}Chan4:DAC_SetPt-SP
SR:C29-MG{PS:EPU1-S2}Chan1:DAC_SetPt-SP
SR:C29-MG{PS:EPU1-S2}Chan2:DAC_SetPt-SP
SR:C29-MG{PS:EPU1-S2}Chan3:DAC_SetPt-SP
SR:C29-MG{PS:EPU1-S2}Chan4:DAC_SetPt-SP
SR:C29-MG{PS:EPU1-S3}Chan1:DAC_SetPt-SP
SR:C29-MG{PS:EPU1-S3}Chan2:DAC_SetPt-SP
SR:C29-MG{PS:EPU1-S3}Chan3:DAC_SetPt-SP
SR:C29-MG{PS:EPU1-S3}Chan4:DAC_SetPt-SP
SR:C29-MG{PS:EPU1-S4}Chan1:DAC_SetPt-SP
SR:C29-MG{PS:EPU1-S4}Chan2:DAC_SetPt-SP
SR:C29-MG{PS:EPU1-S4}Chan3:DAC_SetPt-SP
SR:C29-MG{PS:EPU1-S4}Chan4:DAC_SetPt-SP
SR:C29-MG{PS:EPU1-S5}Chan1:DAC_SetPt-SP
SR:C29-MG{PS:EPU1-S5}Chan2:DAC_SetPt-SP
SR:C29-MG{PS:EPU1-S5}Chan3:DAC_SetPt-SP
SR:C29-MG{PS:EPU1-S5}Chan4:DAC_SetPt-SP
```

#### SXN — current-strip readbacks
Status: NOT FOUND. Recommendation: archive at a rate appropriate for changing currents; use 10 Hz while changing as the initial target.
```text
SR:C29-MG{PS:EPU1-S1}Chan1:DCCT1-I
SR:C29-MG{PS:EPU1-S1}Chan2:DCCT1-I
SR:C29-MG{PS:EPU1-S1}Chan3:DCCT1-I
SR:C29-MG{PS:EPU1-S1}Chan4:DCCT1-I
SR:C29-MG{PS:EPU1-S2}Chan1:DCCT1-I
SR:C29-MG{PS:EPU1-S2}Chan2:DCCT1-I
SR:C29-MG{PS:EPU1-S2}Chan3:DCCT1-I
SR:C29-MG{PS:EPU1-S2}Chan4:DCCT1-I
SR:C29-MG{PS:EPU1-S3}Chan1:DCCT1-I
SR:C29-MG{PS:EPU1-S3}Chan2:DCCT1-I
SR:C29-MG{PS:EPU1-S3}Chan3:DCCT1-I
SR:C29-MG{PS:EPU1-S3}Chan4:DCCT1-I
SR:C29-MG{PS:EPU1-S4}Chan1:DCCT1-I
SR:C29-MG{PS:EPU1-S4}Chan2:DCCT1-I
SR:C29-MG{PS:EPU1-S4}Chan3:DCCT1-I
SR:C29-MG{PS:EPU1-S4}Chan4:DCCT1-I
SR:C29-MG{PS:EPU1-S5}Chan1:DCCT1-I
SR:C29-MG{PS:EPU1-S5}Chan2:DCCT1-I
SR:C29-MG{PS:EPU1-S5}Chan3:DCCT1-I
SR:C29-MG{PS:EPU1-S5}Chan4:DCCT1-I
```

#### SXN — feedforward enable setpoints
Status: NOT FOUND. Recommendation: archive on change. Lookup-table PVs are intentionally excluded and belong in MASAR.
```text
SR:C29-ID:G1A{EPU:1-FF:0}Ena-Sel
SR:C29-ID:G1A{EPU:1-FF:1}Ena-Sel
SR:C29-ID:G1A{EPU:1-FF:2}Ena-Sel
SR:C29-ID:G1A{EPU:1-FF:3}Ena-Sel
SR:C29-ID:G1A{EPU:1-FFCS:0}Ena-Sel
SR:C29-ID:G1A{EPU:1-FFCS:1}Ena-Sel
SR:C29-ID:G1A{EPU:1-FFCS:2}Ena-Sel
SR:C29-ID:G1A{EPU:1-FFCS:3}Ena-Sel
SR:C29-ID:G1A{EPU:1-FFCS:4}Ena-Sel
SR:C29-ID:G1A{EPU:1-FFCS:5}Ena-Sel
SR:C29-ID:G1A{EPU:1-FFCS:6}Ena-Sel
SR:C29-ID:G1A{EPU:1-FFCS:7}Ena-Sel
SR:C29-ID:G1A{EPU:1-FFCS:8}Ena-Sel
SR:C29-ID:G1A{EPU:1-FFCS:9}Ena-Sel
SR:C29-ID:G1A{EPU:1-FFCS:10}Ena-Sel
SR:C29-ID:G1A{EPU:1-FFCS:11}Ena-Sel
SR:C29-ID:G1A{EPU:1-FFCS:12}Ena-Sel
SR:C29-ID:G1A{EPU:1-FFCS:13}Ena-Sel
SR:C29-ID:G1A{EPU:1-FFCS:14}Ena-Sel
SR:C29-ID:G1A{EPU:1-FFCS:15}Ena-Sel
SR:C29-ID:G1A{EPU:1-FFCS:16}Ena-Sel
SR:C29-ID:G1A{EPU:1-FFCS:17}Ena-Sel
SR:C29-ID:G1A{EPU:1-FFCS:18}Ena-Sel
SR:C29-ID:G1A{EPU:1-FFCS:19}Ena-Sel
```

#### ARI — ID setpoints
Status: NOT FOUND. Recommendation: archive on change.
```text
SR:C29-ID:G1:{EPU70:2}:CMD:MOVE_GAP
SR:C29-ID:G1:{EPU70:2}:CMD:MOTION
SR:C29-ID:G1:{EPU70:2}:CMD:SET_VELOCITY
SR:C29-ID:G1:{EPU70:2}:CMD:SET_PHASE
SR:C29-ID:G1:{EPU70:2}:CMD:PHASE:SET_MODE
SR:C29-2-ID:NomOpen-Sp
SR:C29-2-ID:NomClose-Sp
```

#### ARI — ID readbacks
Recommendation: gap/phase readbacks at 10 Hz while moving and 2 Hz while idle; status/mode readbacks on change.
```text
SR:C29-ID:G1:{EPU70:2}:GAP:ACT  # FOUND
SR:C29-ID:G1:{EPU70:2}:CMD:SET_VELOCITY:RBV
SR:C29-ID:G1:{EPU70:2}:STATE
SR:C29-ID:G1:{EPU70:2}:PHASE:RBV
SR:C29-ID:G1:{EPU70:2}:PHASE:STATE
```

#### ARI — orbit-corrector setpoints
Status: NOT FOUND. Recommendation: archive on change.
```text
SR:C29-MG{PS:EPU2-CRR}Chan1:DAC_SetPt-SP
SR:C29-MG{PS:EPU2-CRR}Chan2:DAC_SetPt-SP
SR:C29-MG{PS:EPU2-CRR}Chan3:DAC_SetPt-SP
SR:C29-MG{PS:EPU2-CRR}Chan4:DAC_SetPt-SP
```

#### ARI — orbit-corrector readbacks
Status: NOT FOUND. Recommendation: archive at a rate appropriate for changing currents; use 10 Hz while changing as the initial target.
```text
SR:C29-MG{PS:EPU2-CRR}Chan1:DCCT1-I
SR:C29-MG{PS:EPU2-CRR}Chan2:DCCT1-I
SR:C29-MG{PS:EPU2-CRR}Chan3:DCCT1-I
SR:C29-MG{PS:EPU2-CRR}Chan4:DCCT1-I
```

#### ARI — current-strip setpoints
Status: NOT FOUND. Recommendation: archive on change.
```text
SR:C29-MG{PS:EPU2-S1}Chan1:DAC_SetPt-SP
SR:C29-MG{PS:EPU2-S1}Chan2:DAC_SetPt-SP
SR:C29-MG{PS:EPU2-S1}Chan3:DAC_SetPt-SP
SR:C29-MG{PS:EPU2-S1}Chan4:DAC_SetPt-SP
SR:C29-MG{PS:EPU2-S2}Chan1:DAC_SetPt-SP
SR:C29-MG{PS:EPU2-S2}Chan2:DAC_SetPt-SP
SR:C29-MG{PS:EPU2-S2}Chan3:DAC_SetPt-SP
SR:C29-MG{PS:EPU2-S2}Chan4:DAC_SetPt-SP
SR:C29-MG{PS:EPU2-S3}Chan1:DAC_SetPt-SP
SR:C29-MG{PS:EPU2-S3}Chan2:DAC_SetPt-SP
SR:C29-MG{PS:EPU2-S3}Chan3:DAC_SetPt-SP
SR:C29-MG{PS:EPU2-S3}Chan4:DAC_SetPt-SP
SR:C29-MG{PS:EPU2-S4}Chan1:DAC_SetPt-SP
SR:C29-MG{PS:EPU2-S4}Chan2:DAC_SetPt-SP
SR:C29-MG{PS:EPU2-S4}Chan3:DAC_SetPt-SP
SR:C29-MG{PS:EPU2-S4}Chan4:DAC_SetPt-SP
SR:C29-MG{PS:EPU2-S5}Chan1:DAC_SetPt-SP
SR:C29-MG{PS:EPU2-S5}Chan2:DAC_SetPt-SP
SR:C29-MG{PS:EPU2-S5}Chan3:DAC_SetPt-SP
SR:C29-MG{PS:EPU2-S5}Chan4:DAC_SetPt-SP
```

#### ARI — current-strip readbacks
Status: NOT FOUND. Recommendation: archive at a rate appropriate for changing currents; use 10 Hz while changing as the initial target.
```text
SR:C29-MG{PS:EPU2-S1}Chan1:DCCT1-I
SR:C29-MG{PS:EPU2-S1}Chan2:DCCT1-I
SR:C29-MG{PS:EPU2-S1}Chan3:DCCT1-I
SR:C29-MG{PS:EPU2-S1}Chan4:DCCT1-I
SR:C29-MG{PS:EPU2-S2}Chan1:DCCT1-I
SR:C29-MG{PS:EPU2-S2}Chan2:DCCT1-I
SR:C29-MG{PS:EPU2-S2}Chan3:DCCT1-I
SR:C29-MG{PS:EPU2-S2}Chan4:DCCT1-I
SR:C29-MG{PS:EPU2-S3}Chan1:DCCT1-I
SR:C29-MG{PS:EPU2-S3}Chan2:DCCT1-I
SR:C29-MG{PS:EPU2-S3}Chan3:DCCT1-I
SR:C29-MG{PS:EPU2-S3}Chan4:DCCT1-I
SR:C29-MG{PS:EPU2-S4}Chan1:DCCT1-I
SR:C29-MG{PS:EPU2-S4}Chan2:DCCT1-I
SR:C29-MG{PS:EPU2-S4}Chan3:DCCT1-I
SR:C29-MG{PS:EPU2-S4}Chan4:DCCT1-I
SR:C29-MG{PS:EPU2-S5}Chan1:DCCT1-I
SR:C29-MG{PS:EPU2-S5}Chan2:DCCT1-I
SR:C29-MG{PS:EPU2-S5}Chan3:DCCT1-I
SR:C29-MG{PS:EPU2-S5}Chan4:DCCT1-I
```

#### ARI — feedforward enable setpoints
Status: NOT FOUND. Recommendation: archive on change. Lookup-table PVs are intentionally excluded and belong in MASAR.
```text
SR:C29-ID:G1A{EPU:2-FF:0}Ena-Sel
SR:C29-ID:G1A{EPU:2-FF:1}Ena-Sel
SR:C29-ID:G1A{EPU:2-FF:2}Ena-Sel
SR:C29-ID:G1A{EPU:2-FF:3}Ena-Sel
SR:C29-ID:G1A{EPU:2-FFCS:0}Ena-Sel
SR:C29-ID:G1A{EPU:2-FFCS:1}Ena-Sel
SR:C29-ID:G1A{EPU:2-FFCS:2}Ena-Sel
SR:C29-ID:G1A{EPU:2-FFCS:3}Ena-Sel
SR:C29-ID:G1A{EPU:2-FFCS:4}Ena-Sel
SR:C29-ID:G1A{EPU:2-FFCS:5}Ena-Sel
SR:C29-ID:G1A{EPU:2-FFCS:6}Ena-Sel
SR:C29-ID:G1A{EPU:2-FFCS:7}Ena-Sel
SR:C29-ID:G1A{EPU:2-FFCS:8}Ena-Sel
SR:C29-ID:G1A{EPU:2-FFCS:9}Ena-Sel
SR:C29-ID:G1A{EPU:2-FFCS:10}Ena-Sel
SR:C29-ID:G1A{EPU:2-FFCS:11}Ena-Sel
SR:C29-ID:G1A{EPU:2-FFCS:12}Ena-Sel
SR:C29-ID:G1A{EPU:2-FFCS:13}Ena-Sel
SR:C29-ID:G1A{EPU:2-FFCS:14}Ena-Sel
SR:C29-ID:G1A{EPU:2-FFCS:15}Ena-Sel
SR:C29-ID:G1A{EPU:2-FFCS:16}Ena-Sel
SR:C29-ID:G1A{EPU:2-FFCS:17}Ena-Sel
SR:C29-ID:G1A{EPU:2-FFCS:18}Ena-Sel
SR:C29-ID:G1A{EPU:2-FFCS:19}Ena-Sel
```

### MASAR-controlled C29 PVs

The collected work identifies three required MASAR configuration updates. No
additional required MASAR configuration was found in this repository or in
the feedforward measurement repository.

#### CID 85 — `ID_MPS_Limits_20210212`

Add the `.DRVH` and `.DRVL` limit PVs for every new orbit-corrector and
current-strip power-supply channel:

```text
SR:C29-MG{PS:EPU1-CRR}Chan1:DAC_SetPt-SP.DRVH
SR:C29-MG{PS:EPU1-CRR}Chan1:DAC_SetPt-SP.DRVL
SR:C29-MG{PS:EPU1-CRR}Chan2:DAC_SetPt-SP.DRVH
SR:C29-MG{PS:EPU1-CRR}Chan2:DAC_SetPt-SP.DRVL
SR:C29-MG{PS:EPU1-CRR}Chan3:DAC_SetPt-SP.DRVH
SR:C29-MG{PS:EPU1-CRR}Chan3:DAC_SetPt-SP.DRVL
SR:C29-MG{PS:EPU1-CRR}Chan4:DAC_SetPt-SP.DRVH
SR:C29-MG{PS:EPU1-CRR}Chan4:DAC_SetPt-SP.DRVL
SR:C29-MG{PS:EPU2-CRR}Chan1:DAC_SetPt-SP.DRVH
SR:C29-MG{PS:EPU2-CRR}Chan1:DAC_SetPt-SP.DRVL
SR:C29-MG{PS:EPU2-CRR}Chan2:DAC_SetPt-SP.DRVH
SR:C29-MG{PS:EPU2-CRR}Chan2:DAC_SetPt-SP.DRVL
SR:C29-MG{PS:EPU2-CRR}Chan3:DAC_SetPt-SP.DRVH
SR:C29-MG{PS:EPU2-CRR}Chan3:DAC_SetPt-SP.DRVL
SR:C29-MG{PS:EPU2-CRR}Chan4:DAC_SetPt-SP.DRVH
SR:C29-MG{PS:EPU2-CRR}Chan4:DAC_SetPt-SP.DRVL
```

For current strips, add the analogous `.DRVH` and `.DRVL` PVs for
`PS:EPU1-S1` through `PS:EPU1-S5` and `PS:EPU2-S1` through `PS:EPU2-S5`,
for `Chan1` through `Chan4`. The orbit-corrector limits are confirmed as
`-10 A` to `+10 A`; current-strip limits are still pending from the ID Group.

#### CID 74 — `Orbit_Feedforward`

Add the orbit feedforward lookup-table PVs for both EPUs, `i = 0..3`:

```text
SR:C29-ID:G1A{EPU:1-FF:i}L2-Calc_.F
SR:C29-ID:G1A{EPU:1-FF:i}L2-Calc_.G
SR:C29-ID:G1A{EPU:1-FF:i}L2-Calc_.H
SR:C29-ID:G1A{EPU:1-FF:i}L2-Calc_.I
SR:C29-ID:G1A{EPU:1-FF:i}L2-Calc_.J
SR:C29-ID:G1A{EPU:1-FF:i}L2-Calc_.K
SR:C29-ID:G1A{EPU:1-FF:i}L2-Calc_.L
SR:C29-ID:G1A{EPU:1-FF:i}L2-Calc_.M
SR:C29-ID:G1A{EPU:1-FF:i}L2-Calc_.N
SR:C29-ID:G1A{EPU:1-FF:i}L2-Calc_.O
SR:C29-ID:G1A{EPU:1-FF:i}L2-Calc_.P
SR:C29-ID:G1A{EPU:1-FF:i}L2-Calc_.Q
```

For SXN use `EPU:1`; for ARI use `EPU:2`. These table PVs are MASAR
controlled and are not archiver targets.

#### CID 73 — `CS_FeedForward`

Add the same twelve lookup-table PVs for both EPUs, with `i = 0..19` and the
`FFCS` namespace:

```text
SR:C29-ID:G1A{EPU:1-FFCS:i}L2-Calc_.F
SR:C29-ID:G1A{EPU:1-FFCS:i}L2-Calc_.G
SR:C29-ID:G1A{EPU:1-FFCS:i}L2-Calc_.H
SR:C29-ID:G1A{EPU:1-FFCS:i}L2-Calc_.I
SR:C29-ID:G1A{EPU:1-FFCS:i}L2-Calc_.J
SR:C29-ID:G1A{EPU:1-FFCS:i}L2-Calc_.K
SR:C29-ID:G1A{EPU:1-FFCS:i}L2-Calc_.L
SR:C29-ID:G1A{EPU:1-FFCS:i}L2-Calc_.M
SR:C29-ID:G1A{EPU:1-FFCS:i}L2-Calc_.N
SR:C29-ID:G1A{EPU:1-FFCS:i}L2-Calc_.O
SR:C29-ID:G1A{EPU:1-FFCS:i}L2-Calc_.P
SR:C29-ID:G1A{EPU:1-FFCS:i}L2-Calc_.Q
```

The controller index remains zero-based: `FFCS:0` maps to `csch1` and
`FFCS:19` maps to `csch20`.

## Implementation steps to close out

1. **Step 4 (redo)** — edit `add_C29_SXN_ARI_IDs()` in
   `db_update/update_apv2_db.py`: fill `id_pvs` for both EPUs per the
   Pattern-A template (gap/gap_trig/gap_go/gap_hinominal/gap_lonominal/
   gap_ramping/gap_speed/gap_hilim/gap_lolim, plus phase/phase_trig/
   phase_speed/phase_hilim/phase_lolim, mode, cch0-3, cch[0-3], orbff0-3
   variants for all four table slots, current strips, and csff).
2. Add back to `_FUNCTIONS`:
   `"add_C29_SXN_ARI_IDs": lambda: add_C29_SXN_ARI_IDs(exist_ok=True)`
3. **Step 6** — edit `v2tests/nsls2sr_unitconv.yaml`: append
   `epu50g1c29u`/`epu70g1c29d` to the type-2 µm blocks (including the
   corresponding `_readonly` and `_speed` blocks), and to the
   right `ID_orb_cor_channel` entry.
4. **Step 7** — back up production files again (Step 2 pattern), then:
   `pixi run python db_update/update_apv2_db.py --run add_C29_SXN_ARI_IDs`
5. **Step 8** — `cp v2tests/nsls2sr_unitconv.yaml /epics/aphla/apconf_v2/nsls2/nsls2sr_unitconv.yaml`
6. **Step 9 (rerun)** — regenerate JSON snapshot:
   `pixi run python db_update/update_apv2_db.py --run save_pgz_db_contents_to_json`
7. **Step 10** — commit `update_apv2_db.py`, `nsls2sr_unitconv.yaml`,
   `nsls2_sr_elems_pvs_mvs.json`, `PROGRESS_add_C29_SXN_ARI.md` together.
   Message: `Add epu50g1c29u, epu70g1c29d PVs to aphla v2 database` (or similar
   — UBPMs already committed, so scope this commit to the PV fill-in).

## Notes for future sessions

- Update `db_update/PROGRESS_add_C29_SXN_ARI.md` checklist/notes as each step
  above completes — it's the durable record, committed alongside code.
- If any PV pattern here doesn't match what's actually in the IOC, verify with
  `caget` before committing (per skill's "Verify after writing" note).
- Keep this reference document with the database integration history. It is
  the durable home for the detailed PV, archive, MASAR, and implementation
  reference material.

## Data-collection findings (2026-09-09)

- Gap-axis PVs verified for both EPUs.
  - SXN: setpoint/readback 220000/220000 um, speed 5000 um/s, limits
    10980–220500 um, nominal close/open 12000/220000 um.
  - ARI: setpoint/readback 220000/220001 um, speed 5000 um/s, limits
    10980–220500 um, nominal close/open 11500/220000 um.
  - Both motion PVs returned 1.
- Phase-axis PVs verified for both EPUs: setpoint/readback 0/0 um and
  limits -35500–35500 um.
- Mode PVs connect for both EPUs. Enum labels are: value 0 `None`, value 1
  `Parallel TOBI`, value 2 `Parallel TIBO`, value 3 `Antiparallel TOBI`, and
  value 4 `Antiparallel TIBO`. Current mode readbacks are `None`/invalid.
- Corrector channel PVs (`cch0`–`cch3`) connect for both EPUs. Setpoints are
  zero and readbacks are near zero. Their `.DRVH` and `.DRVL` fields return
  zero, as do `.HOPR` and `.LOPR` for the checked representative channels;
  the authoritative orbit-corrector limits are confirmed separately as
  -10 A to +10 A. Current-strip limits remain unresolved.
- SXN and ARI current-strip PVs for 20 physical coils were collected. All
  setpoints and reported drive limits returned zero; readbacks are present.
- C29 will use the newer one-based aphla current-strip convention:
  `csch1`–`csch20`, mapped sequentially from S1-Chan1 through S5-Chan4.
  This is independent of the zero-based feedforward controller index:
  `FFCS:0` corresponds to `csch1`, and `FFCS:19` to `csch20`.
- The aphla inspection pattern is:
  `ap.machines.loadfast("nsls2", "SR")`, then
  `elem.pv(field="cschN", handle="setpoint"/"readback")` after retrieving
  the element with `ap.getElements(name)[0]`.
