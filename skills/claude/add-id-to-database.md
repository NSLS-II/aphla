---
name: add-id-to-database
description: "Interactive guide for adding a new insertion device (ID) and its BPMs to the NSLS2 aphla v2 database. Steps through the update_apv2_db.py workflow one phase at a time."
---

# Add Insertion Device to aphla v2 Database

Guide the user through adding a new insertion device (ID) and/or BPM elements
to the aphla v2 database. This workflow modifies
`db_update/update_apv2_db.py`, `v2tests/nsls2sr_unitconv.yaml`, and the
production `.pgz` database files at `/epics/aphla/apconf_v2/nsls2/`.

## When to Use

- New ID and/or BPMs have been added to the storage ring LTE (via
  `add-id-to-lte`) and now need to be added to the aphla v2 database
- New element types (XBPM, skew quad, etc.) need to be added for an existing
  straight cell
- Unit conversion entries are missing for elements already in the database

## Reference Functions

Existing update functions to model from (most recent first):

| Function | Elements added | Commit |
|----------|----------------|--------|
| `add_C09_XBPM_and_4_new_skew_quads()` | XBPM + 4 SQ3H skew quads | `7c9492e` (2025-12) |
| `update_C09_straight()` | C09 IVU18 (CDI) + 2 UBPMs | `cc98e81` (2025-09) |
| `update_C20_straight()` | C20 OVU68 (IFE) + 2 UBPMs | `381e328` (2023-09) |

Always model the new function on the **most relevant** existing function.

---

## Step 0 — Create a Progress File

Create a progress log for this specific run. This file serves as a record of
what was done and when.

**Filename convention:** `db_update/PROGRESS_add_C{##}_{NAME}.md`

Example for C29 SXN/ARI EPUs: `db_update/PROGRESS_add_C29_SXN_ARI.md`

Suggested initial content:

```markdown
# Add C## <NAME> to aphla v2 Database

## Parameters

| Parameter | Value |
|-----------|-------|
| Cell number | ## |
| Elements added | |
| Date started | YYYY-MM-DD |

## Progress

- [ ] Step 1 — Gather parameters
- [ ] Step 2 — Back up production files
- [ ] Step 3 — Sync JSON snapshot (if needed)
- [ ] Step 4 — Write update function
- [ ] Step 5 — Flip if/elif block
- [ ] Step 6 — Add unit conversion entries
- [ ] Step 7 — Run update script
- [ ] Step 8 — Copy unitconv to production
- [ ] Step 9 — Regenerate JSON snapshot
- [ ] Step 10 — Commit
```

Check off each step as it completes. Add notes, PV names, and any decisions or
surprises inline. This file is committed alongside the code changes as a
permanent record.

---

## Step 1 — Gather Parameters

Before writing the update function, confirm these values with the user:

1. **Cell number** — integer (e.g. 29 for C29)
2. **New element names** — e.g. `epu50g1c29u`, `pu1g1c29a`, `pu4g1c29a`
3. **Element types** — `IVU`, `EPU`, `OVU`, `UBPM`, `XBPM_`, `SKQUAD`, etc.
4. **Function pattern** to use:
   - **Pattern A** — ID + UBPMs added together: model on `update_C09_straight()`
   - **Pattern B** — XBPM or other element type added separately: model on
     `add_C09_XBPM()` or `add_C09_XBPM_and_4_new_skew_quads()`
5. **Element positions** — `sc` offsets from `straight_sc`. Read these directly
   from the LTE script (`target_dsc` for IDs, `target_dse` for BPMs with L=0).
   Do not approximate from `se` values; the LTE script targets are authoritative.
6. **PV names** — from control system specs (SP and RB for each):
   - Gap: setpoint, readback, trigger, speed, hi/lo nominal, ramping status (hi/lo limits derived from setpoint `.DRVH`/`.DRVL`)
   - **EPU only** — Phase: setpoint, readback, trigger, speed
   - **EPU only** — Mode (mechanical, enum): setpoint, readback
   - **EPU only** — Current strips (cs0–csN, confirm channel count): setpoint + readback per channel
   - **EPU only** — Current strip feedforward (csff\*): feedforward table PVs
   - Correctors: cch0–cch3 setpoint + readback
   - Orbit feedforward: orbff0–orbff3 (enable, gap slot, phase slot if EPU, current setpoint)
7. **Unit conversion group** — which existing YAML group to append the new
   element to, or whether a new group is needed

---

## Step 2 — Back Up Production Files

**Always do this first.** The update script writes directly to production.

```bash
cd /epics/aphla/apconf_v2/nsls2
cp nsls2_sr_elems_pvs_mvs.pgz        nsls2_sr_elems_pvs_mvs.pgz.arch$(date +%Y%m%d)
cp nsls2_sr_elems_pvs_mvs.numpy2.pgz nsls2_sr_elems_pvs_mvs.numpy2.pgz.arch$(date +%Y%m%d)
cp nsls2sr_unitconv.yaml              nsls2sr_unitconv.yaml.arch$(date +%Y%m%d)
```

Confirm all three backup files exist before continuing.

---

## Step 3 — Sync JSON Snapshot (if needed)

**Purpose:** The JSON is a human-readable snapshot of the `.pgz` database,
committed so that git diffs are readable. Step 9 will regenerate it after the
update, so this step is not strictly required. However, if the JSON is already
stale (someone updated production `.pgz` outside this repo without committing
the JSON), the Step 10 commit will mix pre-existing discrepancies with the new
element changes — making the git history harder to read. Syncing here first
isolates the two concerns into separate commits.

**To check:** Run `save_pgz_db_contents_to_json` and inspect `git diff`:

```python
elif True:  # Last run on YYYY-MM-DD
    save_pgz_db_contents_to_json(machine_list=["SR"])
```

```bash
pixi run python db_update/update_apv2_db.py
git diff db_update/nsls2_sr_elems_pvs_mvs.json
```

If `git diff` shows no changes, the JSON is already in sync — flip the block
back to `elif False:` and skip to Step 4.

If there are changes, they represent pre-existing production updates not yet
captured in the repo. Commit just the JSON now:

```bash
git add db_update/nsls2_sr_elems_pvs_mvs.json
git commit -m "Sync JSON snapshot to current production state"
```

Then flip the block back to `elif False:` and continue to Step 4.

---

## Step 4 — Write the Update Function

Add a new function to `db_update/update_apv2_db.py`. Place it just before the
`if __name__ == "__main__":` block.

### Pattern A: New ID + UBPMs (canonical template)

This pattern is used when adding a new ID and its upstream/downstream UBPMs
to a straight cell for the first time. The canonical reference is
`update_C09_straight()`.

```python
def update_C##_straight(exist_ok=False):
    """C## <ID_TYPE> (<beamline_name>)"""

    assert np.__version__.startswith("2.")

    cell_num = ##

    # s-pos of center of straight
    straight_sc = SR_CIRCUMF / 30 * cell_num  # [m]

    ubpm_info_list = [
        dict(
            name="pu1g1c##a",                                 # upstream BPM
            sc=float(f"{straight_sc - <offset_us>:.6f}"),     # s-pos [m]
            devname=f"C{cell_num:02d}-BPM7",
            groups=["UBPM", "PU1"],
        ),
        dict(
            name="pu4g1c##a",                                 # downstream BPM
            sc=float(f"{straight_sc + <offset_ds>:.6f}"),     # s-pos [m]
            devname=f"C{cell_num:02d}-BPM8",
            groups=["UBPM", "PU4"],
        ),
    ]

    id_info_list = [
        dict(
            name="<id_elem_name>",   # e.g. "ivu18g1c09c" or "epu50g1c29u"
            type="<ID_TYPE>",        # e.g. "IVU", "EPU", "OVU"
            symmetry="<C|U|D>",      # U=upstream, D=downstream, C=centered
            groups=["ID", "<TYPE_GROUP>", "<U_GROUP>", "<BEAMLINE>"],
            # Example for IVU18 CDI: groups=["ID", "IVU18", "U18", "CDI"]
            sc=straight_sc + <offset>,  # 0.0 if centered; positive = downstream
            L=<length_m>,
        ),
    ]

    id_pvs = {
        "gap": dict(
            setpoint="SR:C##-ID:G1{<type>:<n>-<axis>:Gap}-Mtr-SP",  # [um]
            readback="SR:C##-ID:G1{<type>:<n>-<axis>:Gap}-Mtr.RBV",  # [um]
        ),
        "gap_trig": dict(setpoint="SR:C##-ID:G1{<type>:<n>-<axis>:Gap}-Mtr-Go"),
        "gap_go": dict(
            setpoint="SR:C##-ID:G1{<type>:<n>-<axis>:Gap}-Mtr-Go",  # [um]
            readback="SR:C##-ID:G1{<type>:<n>-<axis>:Gap}-Mtr.RBV",  # [um]
        ),
        "gap_hinominal": dict(readback="SR:C##-ID:NomOpen-Sp"),
        "gap_lonominal": dict(readback="SR:C##-ID:NomClose-Sp"),
        "gap_ramping": dict(readback="SR:C##-ID:G1{<type>:<n>-<axis>:Gap}-Mtr.MOVN"),
        "gap_speed": dict(
            setpoint="SR:C##-ID:G1{<type>:<n>}GapSpeed-SP",  # [um/s]
            readback="SR:C##-ID:G1{<type>:<n>}GapSpeed-RB",  # [um/s]
        ),
        # For IVU with taper, add:
        # "taper": dict(setpoint="...", readback="..."),
        # "taper_trig": dict(setpoint="..."),
        # "taper_speed": dict(setpoint="...", readback="..."),
        # For EPU, add phase fields:
        # "phase": dict(setpoint="...", readback="..."),
        # "phase_trig": dict(setpoint="..."),
        # "phase_speed": dict(setpoint="...", readback="..."),
    }
    id_pvs["gap_hilim"] = dict(readback=f'{id_pvs["gap"]["setpoint"]}.DRVH')
    id_pvs["gap_lolim"] = dict(readback=f'{id_pvs["gap"]["setpoint"]}.DRVL')
    # For IVU with taper or EPU with phase, also add _hilim/_lolim entries.

    # Corrector channels (cch*)
    epsilon = 0.05
    id_pvs["cch0"] = dict(setpoint="SR:C##-MG{<PS_PV>:Chan1}I-sp",
                          readback="SR:C##-MG{<PS_PV>}dcct1ADC:Chan1",
                          epsilon=epsilon)
    id_pvs["cch1"] = dict(setpoint="SR:C##-MG{<PS_PV>:Chan2}I-sp",
                          readback="SR:C##-MG{<PS_PV>}dcct1ADC:Chan2",
                          epsilon=epsilon)
    id_pvs["cch2"] = dict(setpoint="SR:C##-MG{<PS_PV>:Chan3}I-sp",
                          readback="SR:C##-MG{<PS_PV>}dcct1ADC:Chan3",
                          epsilon=epsilon)
    id_pvs["cch3"] = dict(setpoint="SR:C##-MG{<PS_PV>:Chan4}I-sp",
                          readback="SR:C##-MG{<PS_PV>}dcct1ADC:Chan4",
                          epsilon=epsilon)

    for iCh in range(4):
        id_pvs[f"cch[{iCh}]"] = dict(
            readback=id_pvs[f"cch{iCh}"]["readback"],
            epsilon=epsilon)

    # Orbit feedforward channels
    nCh = 4
    for iCh in range(nCh):
        orbff_pv_prefix = f"SR:C##-MG{{<BEAMLINE>:Orbit-FF:{iCh}}}"
        id_pvs[f"orbff{iCh}_on"] = dict(setpoint=f"{orbff_pv_prefix}Ena-Sel")
        id_pvs[f"orbff{iCh}_m0_gap"] = dict(setpoint=f"{orbff_pv_prefix}L2-Calc_.F")
        # For EPU also add orbff{iCh}_m0_phase and orbff{iCh}_m1_* etc.
        id_pvs[f"orbff{iCh}_m0_I"] = dict(setpoint=f"{orbff_pv_prefix}L2-Calc_.H")
        id_pvs[f"orbff{iCh}_output"] = dict(setpoint=id_pvs[f"cch{iCh}"]["setpoint"])

    d = _add_new_ID_and_IDBPMs(
        exist_ok, cell_num, ubpm_info_list, id_info_list, id_pvs)

    save_pgz_files_for_both_np1_and_np2(d, "SR")
```

**Key placeholders to fill in:**

| Placeholder | Value |
|------------|-------|
| `<offset_us>` | Upstream BPM offset from straight center (m), from LTE script `target_dse` |
| `<offset_ds>` | Downstream BPM offset from straight center (m), from LTE script `target_dse` |
| `<id_elem_name>` | Lowercase ELEGANT element name, e.g. `epu50g1c29u` |
| `<ID_TYPE>` | Element family string: `IVU`, `EPU`, `OVU`, etc. |
| `<C\|U\|D>` | Symmetry: `U` upstream, `D` downstream, `C` centered |
| `<length_m>` | Active/magnetic length in meters |
| `<PS_PV>` | Power supply PV identifier from control system |
| `<BEAMLINE>` | Beamline acronym for orbit FF PVs, e.g. `CDI`, `IFE` |

**Note on `orbff*_m0_gap` PV slot:** The `.F`/`.G`/`.H` etc. slot in the
`L2-Calc_` PV record varies by beamline. C09 CDI uses `.F` for gap; C20 IFE
uses `.C`. Verify from the actual PV record or control system documentation
before committing.

### Pattern B: XBPM co-located with existing ID

Model on `add_C09_XBPM()`:

```python
def add_C##_XBPM(exist_ok=False):
    """C## <beamline> XBPM"""

    cell_num = ##

    idobj = ap.getElements("<id_elem_name>")[0]
    id_sc = (idobj.sb + idobj.se) / 2

    ds_ubpm = ap.getNeighbors(idobj, "*", n=1)[-1]
    new_xbpm_index = (idobj.index + ds_ubpm.index) // 2

    xbpm_info_list = [
        dict(
            name="px1g1c##a",
            sc=float(f"{id_sc:.6f}"),
            devname=f"C{cell_num:02d}-XBPM1",
            groups=["XBPM", "PX1"],
            index=new_xbpm_index,
            pvs={
                "x":  "SR:C##-BI{XBPM:1}PosX:MeanValue_RBV",
                "x0": "SR:C##-BI{XBPM:1}PosX:MeanValue_RBV",
                "y":  "SR:C##-BI{XBPM:1}PosY:MeanValue_RBV",
                "y0": "SR:C##-BI{XBPM:1}PosY:MeanValue_RBV",
            },
        ),
    ]

    d = _add_new_XBPMs(exist_ok, cell_num, xbpm_info_list)
    save_pgz_files_for_both_np1_and_np2(d, "SR")
```

**Verify after writing:** Confirm element names match the LTE file and naming
conventions, and PV names are reachable via `caget` if EPICS is accessible.

---

## Step 5 — Flip the if/elif Block

In the `if __name__ == "__main__":` block at the bottom of
`db_update/update_apv2_db.py`:

1. Find the last `elif True:` block and change it to `elif False:`. Update
   its trailing comment to `# Last run on YYYY-MM-DD`.

2. Add a new `elif True:` block immediately after it:

```python
elif True:  # TO-BE-RUN on YYYY-MM-DD
    update_C##_straight(exist_ok=False)
```

**Before editing**, the tail of the file looks like:
```python
    elif False:  # Last run on 2026-03-21
        add_C09_XBPM_and_4_new_skew_quads(exist_ok=False)

    elif True:  # Last run on 03/21/2026
        save_pgz_db_contents_to_json(machine_list=["SR"])
```

**After editing:**
```python
    elif False:  # Last run on 2026-03-21
        add_C09_XBPM_and_4_new_skew_quads(exist_ok=False)

    elif False:  # Last run on 03/21/2026
        save_pgz_db_contents_to_json(machine_list=["SR"])

    elif True:  # TO-BE-RUN on YYYY-MM-DD
        update_C##_straight(exist_ok=False)
```

---

## Step 6 — Add Unit Conversion Entries

Edit `v2tests/nsls2sr_unitconv.yaml`. The correct section depends on element type.

### New UBPMs

No change needed. UBPMs automatically inherit from the existing `BPM` and
`BPM_ref` group entries (lines 7–28 of the YAML), which apply to all elements
in `groups: [BPM, UBPM]`.

### New IVU-type IDs (gap in µm)

Add the new element name to the `elements:` list in each of these three entries:
- `ID_IVU_gap` (and its `&ID_IVU_gap` anchor if defined there)
- `ID_IVU_gap_readonly`
- `ID_IVU_gap_speed`

Example — adding `ivu18g1c29c`:
```yaml
  ID_IVU_gap: &ID_IVU_gap
    elements: [ivu20g1c03c, ..., ovu68g1c20d, ivu18g1c29c]   # <-- append
```

If the new IVU has a taper axis, add a new taper block modeled on
`ID_IVU_taper` (and `ID_IVU_taper_readonly`, `ID_IVU_taper_speed`).

Also add to the appropriate `ID_orb_cor_channel` entry for `cch*` and
`orbff*_m0_I` fields.

### New EPU-type IDs

Determine whether gap/phase PVs are in mm (type1) or µm (type2):
- **type1 — mm** (e.g. `epu57g1c02c`): append to `ID_EPU_gap_phase_type1`,
  `ID_EPU_gap_phase_type1_readonly`, `ID_EPU_gap_phase_speed_type1`
- **type2 — µm** (e.g. `epu49g1c23u`): append to `ID_EPU_gap_phase_type2`,
  `ID_EPU_gap_phase_type2_readonly`, `ID_EPU_gap_phase_speed_type2`
- **New type**: create a new anchor block following the type1/type2 pattern

Also add to the appropriate `ID_orb_cor_channel` entry.

### New XBPM elements

No change needed. XBPMs inherit from the existing `Xray_BPM` group entry
(`groups: [XBPM]`, lines 51–61 of the YAML).

### New skew quads with beam-based calibration

Add per-element entries immediately after the generic `SKQUAD` group entry,
using YAML anchors to avoid repetition:

```yaml
  # <type> skew quads (YYYY-MM-DD): beam-based calibration coefficients
  <first_elem>: &<anchor_name>
    elements: [<first_elem>]
    fields: [b1]
    handles: [readback, setpoint]
    src_unitsys:
    dst_unitsys: phy
    src_unit: A
    dst_unit: "m^{-1}"
    class: polynomial
    invertible: True
    coeffs: [<coeff_1>, 0.0]
  <second_elem>:
    <<: *<anchor_name>
    elements: [<second_elem>]
    coeffs: [<coeff_2>, 0.0]
```

---

## Step 7 — Run the Update Script

```bash
cd /nsls2/users/yhidaka/git_repos/aphla
pixi run python db_update/update_apv2_db.py
```

Requires **numpy 2** — the pixi environment provides this. Do not use a plain
conda env for this step.

**Expected output:**
- `print_elems_around_straight` shows existing elements near the straight center
- New element names and their assigned indices are printed
- Both `.pgz` files are written to `/epics/aphla/apconf_v2/nsls2/`
- Script prints `Finished`

**After a successful run:** Update the `elif True:` comment to
`elif False:  # Last run on YYYY-MM-DD`.

**Troubleshooting:**
- `"Specified element already exists"` — set `exist_ok=True` only when
  deliberately re-running; for a fresh add this indicates a name collision
- `RuntimeError` from `save_pgz_files_for_both_np1_and_np2` — the numpy-1 step
  uses `~/.conda/envs/apv2-2023-rc2/bin/python`; confirm that conda env exists

---

## Step 8 — Copy unitconv to Production

```bash
cp v2tests/nsls2sr_unitconv.yaml /epics/aphla/apconf_v2/nsls2/nsls2sr_unitconv.yaml
```

Confirm the copy succeeded with `ls -la /epics/aphla/apconf_v2/nsls2/nsls2sr_unitconv.yaml`.

---

## Step 9 — Regenerate JSON Snapshot

The JSON in the repo must reflect the updated `.pgz` state so the commit diff
is readable.

In `update_apv2_db.py`, flip the `save_pgz_db_contents_to_json` block to
`elif True:`:

```python
elif True:  # Last run on YYYY-MM-DD
    save_pgz_db_contents_to_json(machine_list=["SR"])
```

Run the script again:
```bash
pixi run python db_update/update_apv2_db.py
```

Then flip it back to `elif False:`.

**Verify:** `git diff db_update/nsls2_sr_elems_pvs_mvs.json` should show the
new element entries.

---

## Step 10 — Commit

Stage the four modified/new files (including the progress log):

```bash
git add db_update/update_apv2_db.py
git add v2tests/nsls2sr_unitconv.yaml
git add db_update/nsls2_sr_elems_pvs_mvs.json
git add db_update/PROGRESS_add_C##_<NAME>.md
```

Commit message format:
```
Add <element_name(s)> to aphla v2 database
```

Examples:
- `Add ivu18g1c09c, pu1g1c09a, pu4g1c09a to aphla v2 database`
- `Add epu50g1c29u, epu70g1c29d, pu1g1c29a, pu2g1c29a, pu3g1c29a, pu4g1c29a to aphla v2 database`

---

## Gotchas and Edge Cases

1. **numpy-2 requirement** — `save_pgz_files_for_both_np1_and_np2` asserts
   `np.__version__.startswith("2.")`. Always run via `pixi run`. The numpy-1
   `.pgz` variant is written via a subprocess call to
   `~/.conda/envs/apv2-2023-rc2/bin/python`; that conda env must exist.

2. **Element index collisions** — `_add_new_ID_and_IDBPMs` derives indices by
   linear interpolation between existing element s-positions and indices.
   Existing gaps are typically ~200 index units, so the midpoint is safe for
   one element. If adding multiple new elements at once, verify none are
   assigned the same derived index.

3. **Position precision** — Use `float(f"{value:.6f}")` for `sc` values to
   round to 1 µm precision, matching the convention in all existing functions.

4. **BPM device numbering** — `devname` is `C##-BPM7` for upstream (PU1) and
   `C##-BPM8` for downstream (PU4) consistently across all straight cells.

5. **elemGroups drives unitconv inheritance** — `elemGroups` is stored as a
   semicolon-joined string in the database. An element must carry the right
   group name for YAML `groups:` entries to apply. Double-check that the groups
   in the info dict match what the YAML expects.

6. **orbff `L2-Calc_` slot varies by beamline** — C09 CDI gap slot is `.F`;
   C20 IFE is `.C`. Check the actual IOC record before assuming a slot letter.

7. **The script writes to production directly** — there is no dry-run mode.
   Always back up (Step 2) before running.

8. **`save_pgz_db_contents_to_json` is slow** — loading and serializing the
   full database takes ~30 s.
