# aphla v2 Database Update Procedure

## Overview

The aphla v2 database is stored as gzip+pickle (`.pgz`) files at
`/epics/aphla/apconf_v2/nsls2/`. Two variants are maintained:

- `nsls2_sr_elems_pvs_mvs.pgz` — numpy-1 compatible
- `nsls2_sr_elems_pvs_mvs.numpy2.pgz` — numpy-2 compatible

A JSON snapshot (`db_update/nsls2_sr_elems_pvs_mvs.json`) is also kept in
the repo for easy `git diff` inspection of changes.

Unit conversion config: `v2tests/nsls2sr_unitconv.yaml` (source of truth in
the repo; must be copied to production after editing).

---

## Files to modify

| File | Purpose |
|------|---------|
| `db_update/update_apv2_db.py` | Main update script; add a new function and flip `if/elif` block |
| `v2tests/nsls2sr_unitconv.yaml` | Unit conversion entries for new elements |
| `db_update/nsls2_sr_elems_pvs_mvs.json` | Auto-regenerated; commit after running `save_pgz_db_contents_to_json` |

---

## Step-by-step procedure

### 1. Back up production files

```bash
cd /epics/aphla/apconf_v2/nsls2
cp nsls2_sr_elems_pvs_mvs.pgz        nsls2_sr_elems_pvs_mvs.pgz.bak.$(date +%Y%m%d)
cp nsls2_sr_elems_pvs_mvs.numpy2.pgz nsls2_sr_elems_pvs_mvs.numpy2.pgz.bak.$(date +%Y%m%d)
cp nsls2sr_unitconv.yaml              nsls2sr_unitconv.yaml.bak.$(date +%Y%m%d)
```

### 2. Sync the JSON snapshot (if needed)

If `db_update/nsls2_sr_elems_pvs_mvs.json` is behind the current `.pgz`
state (e.g. after recent production changes not yet committed), run
`save_pgz_db_contents_to_json` first so the next commit's diff is clean:

In `update_apv2_db.py`, set the `elif True:` block to:
```python
elif True:
    save_pgz_db_contents_to_json(machine_list=["SR"])
```
Run the script, commit just the JSON, then flip that block back to `False`.

### 3. Write the new update function in `update_apv2_db.py`

- For **new elements**: add a function (e.g. `add_C09_XBPM_and_4_new_skew_quads`).
- Key fields for each element:
  - `elemType`: e.g. `"SKQUAD"`, `"XBPM_"` — the `family` group is auto-derived from this
  - `elemLength`, `elemPosition` (= `se`, the end s-position)
  - `elemIndex`: unique integer used for sorting; must not collide with existing elements
  - `elemGroups`: semicolon-separated extra group names (beyond the auto-added family)
  - `map`: dict of field → `{"get": {"pv": ..., "mv": {}}, "put": {...}}`
- Call `save_pgz_files_for_both_np1_and_np2(d, "SR")` at the end (writes both `.pgz` variants).
- The script reads from production (`/epics/aphla/apconf_v2/nsls2/`) and writes back there.

#### Deriving `sc` / `sb` / `se` for new elements

If the new element is co-located with an existing element already in the
database (e.g. a corrector at the same center), derive positions at runtime:

```python
ref_elem = ap.getElements("ch1g6c01b")[0]
sc = (ref_elem.sb + ref_elem.se) / 2
sb = sc - L / 2
se = sc + L / 2
```

#### Choosing `elemIndex`

Indices must be unique. To insert a new element just before an existing one:

```python
us_elem = ap.getNeighbors(ref_elem, "*", n=1)[0]  # upstream neighbor
elem_index = (us_elem.index + ref_elem.index) // 2
```

Check that the gap is large enough (existing elements typically have ~200-unit
gaps between them, so the midpoint is safe).

### 4. Flip the `if/elif` block

In the `if __name__ == "__main__"` block at the bottom of `update_apv2_db.py`:
- Set the previous `elif True:` to `elif False:`
- Add a new block:
  ```python
  elif True:  # TO-BE-RUN on YYYY-MM-DD
      my_new_function(exist_ok=False)
  ```

### 5. Add unit conversion entries to `v2tests/nsls2sr_unitconv.yaml`

- For a **group-wide** entry, add under the element type group (e.g. `SKQUAD`).
- For **per-element** overrides (e.g. individual calibration coefficients),
  add named entries after the group entry. Use YAML anchors to avoid
  repetition:
  ```yaml
  sq3hg6c01b: &sq3h_skquad
    elements: [sq3hg6c01b]
    fields: [b1]
    handles: [readback, setpoint]
    src_unitsys:
    dst_unitsys: phy
    src_unit: A
    dst_unit: "m^{-1}"
    class: polynomial
    invertible: True
    coeffs: [0.000403, 0.0]
  sq3hg6c03b:
    <<: *sq3h_skquad
    elements: [sq3hg6c03b]
    coeffs: [0.000504, 0.0]
  ```

### 6. Run the update script

Use the pixi environment (requires numpy 2 for the numpy-2 pgz write path):

```bash
cd /nsls2/users/yhidaka/git_repos/aphla
pixi run python db_update/update_apv2_db.py
```

Or use the VS Code debugger with the "Debug: Current File with Arguments pixi default" configuration.

After a successful run:
- Update the comment: `elif False:  # Last run on YYYY-MM-DD`
- Flip the `save_pgz_db_contents_to_json` block to `elif True:` and run again to regenerate the JSON.
- Then flip that back to `elif False:`.

### 7. Copy unitconv to production

```bash
cp v2tests/nsls2sr_unitconv.yaml /epics/aphla/apconf_v2/nsls2/nsls2sr_unitconv.yaml
```

### 8. Commit

Stage and commit:
- `db_update/update_apv2_db.py`
- `v2tests/nsls2sr_unitconv.yaml`
- `db_update/nsls2_sr_elems_pvs_mvs.json`

---

## Environment notes

- `pixi.toml` defines a conda env with Python 3.11, numpy 2, epics-base, and aphla (editable install).
- `APHLA_CONFIG_DIR=/epics/aphla/apconf_v2`, `APHLA_FACILITY=nsls2` are set via `[activation.env]`.
- For the VS Code debugger, `EPICS_BASE` must be set manually in `.vscode/launch.json`
  (path: `${workspaceFolder}/.pixi/envs/default/epics`). See the comment in that file.
- `save_pgz_files_for_both_np1_and_np2` calls `save_np1_loadable_pgz.py` via
  `~/.conda/envs/apv2-2023-rc2/bin/python` to produce the numpy-1 compatible file.
  That conda env must exist on the machine.
