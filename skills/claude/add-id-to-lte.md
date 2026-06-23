---
name: add-id-to-lte
description: "Interactive guide for adding a new insertion device (ID) and its BPMs to the NSLS2 storage ring LTE lattice files. Steps through the dated Python script workflow one phase at a time."
---

# Add Insertion Device to LTE

Guide the user through the incremental workflow for adding a new insertion device
(ID) and its BPMs to the NSLS2 storage ring LTE lattice files. This workflow
produces a dated Python script that generates new layout and model LTE files.

## When to Use

- User wants to add a new undulator, wiggler, EPU, or other ID to a straight cell
- User wants to generate new BPMs (PU-type UBPM elements) for a new ID's straight section
- User needs to regenerate or update model LTE files after an ID addition

## Reference Scripts

Existing scripts to copy from (most recent first):

| Script | ID added | Cell |
|--------|----------|------|
| `machine_data/nsls2/LTE/20250905/20250905_add_C09_CDI_to_LTE.py` | C09 CDI | 9 |
| `machine_data/nsls2/LTE/20230915/20230915_add_C20_IFE_to_LTE.py` | C20 IFE | 20 |
| `machine_data/nsls2/LTE/20221027/20221027_add_C27_HEX_to_LTE.py` | C27 HEX | 27 |

Always copy from the **most recent** script and adapt it.

## Step 0 — Gather Parameters

Before creating the script, ask the user for these required values:

1. **`straight_cell_num`** — integer cell number (e.g. 9 for C09)
2. **New ID name** — the ELEGANT element name for the kickmap (e.g. `IVU18G1C09CM`)
3. **New BPM names** — the PU-type UBPM element names (e.g. `PU1G1C09A`, `PU4G1C09A`)
4. **New kickmap filenames** — the `.sdds` kickmap files to publicize (e.g. `U18kickmap_2o4m_T2m2_woKm2sdds.sdds`)
5. **`n_existing_ubpms`** — count of ID BPMs in the lattice *before* adding new ones (check the previous script's comment block or YAML file)
6. **`n_existing_ukickmaps`** — count of all UKICKMAP elements *before* adding the new one (DW + non-DW kickmaps; check the previous script's comment block)
7. **Source LTE** — path to the most recent `*_aphla_layout_RelKMPaths.lte` file (without `_w_xbpms`), typically in the previous script's `new_LTEs/` directory

## Step 0b — Convert RADIA Kickmap Files to SDDS

ELEGANT's UKICKMAP element requires SDDS-format kickmaps. If the kickmap files you
have are in RADIA text format (`.txt`), convert them first. Skip this step if the
SDDS files already exist in `machine_data/nsls2/LTE/kickmaps/official/`.

### Directory structure

```
machine_data/nsls2/LTE/kickmaps/
  orig_Radia/         ← put original RADIA .txt files here
  conversions/        ← run conversions from here; output files land here
    conv_kickmap.py   ← conversion engine (KickmapFile class)
    conversion_history.py  ← record of all past conversions (add new entries here)
  official/           ← final SDDS files referenced by LTE files
```

### Output filename convention

`{SourceName}_{L}m_T2m2_woKm2sdds.sdds`
- `{L}` uses `o` for the decimal point: `1o8m` = 1.8 m, `1o82m` = 1.82 m
- `T2m2` = unit after conversion
- `woKm2sdds` = generated without the `km2sdds` SDDS tool (pure Python)

### Conversion procedure

1. Copy the RADIA `.txt` files from wherever they are into `orig_Radia/`.

2. Add an entry to `conversion_history.py` for each new kickmap (follow the existing
   style in that file).

3. Activate the correct environment, then run the conversion from the `conversions/`
   directory. The script requires `pyelegant` — use:

   ```bash
   ap-pixi-shell yh-apv2-2026-03-pyele
   # manifest lives in ~/.ap_pixi_manifests/yh-apv2-2026-03-pyele/
   # verified working on 2026-06-23 for C29 SXN/ARI EPU kickmap conversion
   ```

   Example conversion for a file in **urad units** (the most common case from RADIA/Mathematica exports):

```python
# Run from: machine_data/nsls2/LTE/kickmaps/conversions/
import sys
sys.path.insert(0, '.')
from conv_kickmap import KickmapFile

km = KickmapFile(
    input_filepath="../orig_Radia/MyDevice_LV.txt",
    input_format="radia",
    output_filepath="MyDevice_LV_1o8m_T2m2_woKm2sdds.sdds",
    output_format="sdds",
    output_unit="T2m2",
    output_length=1.8,          # effective active length in meters
    design_energy_GeV=3.0,      # NSLS-II design energy; required for urad → T2m2
    output_decimal=16,
    use_km2sdds=False,
)
km.convert()
```

If the RADIA file is already in **T2m2 units**, omit `design_energy_GeV`:

```python
km = KickmapFile(
    input_filepath="../orig_Radia/MyDevice_LV.txt",
    input_format="radia",
    output_filepath="MyDevice_LV_1o8m_T2m2_woKm2sdds.sdds",
    output_format="sdds",
    output_unit="T2m2",
    output_length=1.8,
    output_decimal=16,
    use_km2sdds=False,
)
km.convert()
```

4. Verify the output SDDS file was created in `conversions/`.

5. Copy the final SDDS file to `official/`:

```bash
cp conversions/MyDevice_LV_1o8m_T2m2_woKm2sdds.sdds official/
```

The filenames in `official/` are what you reference in `gen_insertion_device_states_yaml()`
and the `publicize_new_kickmap_files()` call in the LTE script.

### Check the RADIA file unit

Look at the header of the `.txt` file:
- `# Horizontal Kick [micro-rad]` → **urad** (provide `design_energy_GeV=3.0`)
- `# Horizontal 2nd Order Kick [T2m2]` or `# Total Horizontal 2nd Order Kick [T2m2]` → **T2m2** (no energy needed)

## Step 1 — Create the Dated Script

1. Create a new directory: `machine_data/nsls2/LTE/YYYYMMDD/`
2. Copy the most recent reference script into it as `YYYYMMDD_add_C##_NEWID_to_LTE.py`
3. Update the top-level constants in the main block (`if __name__ == "__main__":` section):

```python
RELEASE_DATE_STR = "YYYYMMDD"
straight_cell_num = <cell_num>

# Set to current counts BEFORE this script adds new elements.
# Update the comment block listing all existing IDs to reflect current state.
n_existing_ubpms = <count_before>
n_existing_ukickmaps = <count_before>
```

4. Update `LTE_files['layout']['orig']` to point to the source LTE file:

```python
LTE_files['layout']['orig'] = LayoutLatticeFile(
    path=Path("../YYYYMMDD_prev/new_LTEs/YYYYMMDD_prev_aphla_layout_RelKMPaths.lte"),
    with_xbpms=False,
)
```

5. Start with all `funcs_to_run` flags set to `False`.

6. Also update these functions in the script body to match the new ID:
   - `gen_new_layout_LTE_file()` — element name mappings (DRIFT → UKICKMAP, BPM names)
   - `gen_insertion_device_states_yaml()` — ID states, kickmap file paths
   - `validate_new_LTE_files()` call — `new_ubpm_names`, `new_kickmap_elem_names`

## Step 2 — Phase 1: Generate New Layout LTE File

Set `funcs_to_run["gen_new_layout_LTE_file"] = True`, run the script, then set it back to `False`.

```bash
cd machine_data/nsls2/LTE/YYYYMMDD
python YYYYMMDD_add_C##_NEWID_to_LTE.py
```

**What this does:**
- Reads the source layout LTE file
- Replaces the placeholder DRIFT elements with the new UKICKMAP and BPM elements
- Calls `interactively_adjust_elements()` to let you tweak element lengths/positions
- Writes `new_LTEs/YYYYMMDD_aphla_layout_RelKMPaths.lte` (without X-BPMs)
- Writes `new_LTEs/YYYYMMDD_aphla_layout_w_xbpms_RelKMPaths.lte` (with X-BPMs at kickmap midpoints)

**Verify:**
- Open the new LTE file and check that element names are correct
- Check that the cell length is preserved (total length should be unchanged)
- Check that UBPM and UKICKMAP element counts increased by the expected amounts
- Inspect the X-BPM placement (should be at the midpoint of each kickmap element)

**If lengths need adjustment:** Edit `gen_new_layout_LTE_file()` and re-run.

## Step 3 — Phase 2: Generate IDs+Quads States YAML

Set `funcs_to_run["gen_ids_quads_states_yaml"] = True`, run, then reset to `False`.

**What this does:** Produces `YYYYMMDD_aphla_IDs_quads_states.yaml` combining ID state and quad state labels.

**Verify:** Open the YAML and confirm the new ID appears in the `ids_states` section.

## Step 4 — Phase 3: Generate Insertion Device States YAML

Set `funcs_to_run["gen_insertion_device_states_yaml"] = True`, run, then reset to `False`.

**What this does:** Produces `YYYYMMDD_aphla_IDs_states.yaml` with the list of operational states for all IDs (bare, 3dw, 20ids, etc.), including the new ID's kickmap file references.

**Verify:** Open the YAML and confirm:
- The new ID appears in each relevant state
- Kickmap file paths are correct (relative paths from the LTE file location)
- The new ID is absent in states where it should be open (e.g. `_wo_CDI`)

**If state definitions need updating:** Edit `gen_insertion_device_states_yaml()` and re-run.

## Step 5 — Phase 4: Generate New Model LTE Files

Set `funcs_to_run["gen_new_model_LTE_files"] = True`, run, then reset to `False`.

**What this does:** Iterates over all `(ids_state, quads_state)` combinations and writes one model LTE file per combination (both with and without X-BPMs). Outputs go to `new_LTEs/`.

**Verify:**
- Count of output files matches expected (number of states × 2 for with/without X-BPMs)
- Each file opens in PyELEGANT without errors

## Step 6 — Phase 5: Validate New LTE Files

Set `funcs_to_run["validate_new_LTE_files"] = True`, run, then reset to `False`.

Also confirm the call arguments match:

```python
new_ubpm_names = ["PU1G1C##A", "PU4G1C##A"]   # <-- update for new ID
new_kickmap_elem_names = ["IVU18G1C##CM"]       # <-- update for new ID
```

**What this does:** Loads each model LTE file, runs Twiss calculations, and checks:
- New BPM elements are present and at expected positions
- New kickmap element is present
- Twiss functions (beta, eta, phase) are consistent with expectations

**If `expected_ses` assertions fail with a tiny mismatch (< 1e-10 m):** This is
floating-point accumulation in cumulative s-positions, not a real error. The
`expected_ses` assertions should use `decimal=9` (1 nm tolerance); `decimal=12`
is too tight for elements deep in the ring where hundreds of element lengths
accumulate. The `expected_Ls` assertions can stay at `decimal=12` since element
lengths are stored exactly in the LTE file and do not accumulate error.

**If validation fails for other reasons:** Check element names in the LTE files and fix the source functions.

## Step 7 — Phase 6 (Optional): Match Quads

Only needed if you want a new matched optics solution. Set `funcs_to_run["match_quads"] = True`, run, then reset.

**What this does:** Uses response-matrix matching to find quad strengths that reproduce the reference lattice Twiss functions (typically `3dw:day1` as the reference).

This is computationally intensive — expect it to take several minutes per lattice.

**Output:** New LTE files with suffix `_Q_matched_YH_3dw_nuy27_RelKMPaths.lte`.

## Step 8 — Phase 7: Publicize New Kickmap Files

Set `funcs_to_run["publicize_new_kickmap_files"] = True`, run, then reset.

Confirm `new_official_kickmap_filenames` in the script lists the correct `.sdds` files.

**What this does:** Copies the kickmap SDDS files from a working location into the official shared kickmaps directory so all LTE files can reference them with their standard relative paths.

**Verify:** Confirm the files appear in `machine_data/nsls2/LTE/kickmaps/`.

## Step 9 — Phase 8: Publicize New Model LTE Files

Set `funcs_to_run["publicize_new_model_LTE_files"] = True`, run, then reset.

**What this does:** Copies the final model LTE files from `new_LTEs/` to the official location where aphla reads them.

**Verify:** Confirm the files appear in the expected aphla model directory and that the YAML configuration points to the correct paths.

## Updating Counts for Future Scripts

After this script is complete, leave a comment in the main block noting the updated counts for the *next* person who runs this workflow:

```python
# After this script: n_existing_ubpms = <new_count>, n_existing_ukickmaps = <new_count>
```

Also update the comments listing all existing IDs and their cell numbers.

## Quick Reference: `funcs_to_run` Execution Order

```python
funcs_to_run = {
    "gen_new_layout_LTE_file": False,        # Phase 1 — run first, iterate until correct
    "gen_ids_quads_states_yaml": False,      # Phase 2
    "gen_insertion_device_states_yaml": False,  # Phase 3 — update function body for new ID
    "gen_new_model_LTE_files": False,        # Phase 4
    "validate_new_LTE_files": False,         # Phase 5
    "match_quads": False,                    # Phase 6 (optional)
    "publicize_new_kickmap_files": False,    # Phase 7
    "publicize_new_model_LTE_files": False,  # Phase 8
}
```

Run **one phase at a time**: set that flag to `True`, run the script, verify output,
set it back to `False` before proceeding to the next phase.
