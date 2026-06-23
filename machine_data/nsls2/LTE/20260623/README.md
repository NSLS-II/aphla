# 20260623 — Add C29 SXN (EPU50) and ARI (EPU70) IDs

## Overview

This release adds two EPU insertion devices in cell 29:

| Device | ELEGANT element | Position | Active length | Kickmap SDDS |
|--------|----------------|----------|--------------|--------------|
| SXN EPU50 | `EPU50G1C29U` | Upstream | 1.8 m | `SXN_EPU50LV_1o8m_T2m2_woKm2sdds.sdds` |
| ARI EPU70 | `EPU70G1C29D` | Downstream | 1.82 m | `ARI_EPU70LV_1o82m_T2m2_woKm2sdds.sdds` |

Four new UBPMs are added to the C29 straight: `PU1G1C29A`, `PU2G1C29A`, `PU3G1C29A`, `PU4G1C29A`.

## Skill Used

The interactive step-by-step workflow was driven by the `/add-id-to-lte` Claude skill:

```
.claude/skills/add-id-to-lte/SKILL.md  (symlink → skills/claude/add-id-to-lte.md)
```

## Starting Counts (from 20260304)

These are the counts in the lattice *before* this script adds anything:

```python
n_existing_ubpms = 49          # 47 after C09 CDI + 2 = 49; skew quads (20260304) added none
n_existing_ukickmaps = 26      # 6 DW + 20 non-DW; skew quads added none
```

After this release: `n_existing_ubpms = 53`, `n_existing_ukickmaps = 28` (6 DW + 22 non-DW).

## Source Layout LTE

```
../20260304/new_LTEs/20260304_aphla_layout_RelKMPaths.lte
```

## Steps Completed

### Step 0b — Kickmap Conversion (RADIA → SDDS)

**Environment:** `ap-pixi-shell yh-apv2-2026-03-pyele`
(manifest at `~/.ap_pixi_manifests/yh-apv2-2026-03-pyele/`, verified 2026-06-23)

1. Copied original RADIA files (urad units) to:
   - `machine_data/nsls2/LTE/kickmaps/orig_Radia/SXN_EPU50LV.txt`
   - `machine_data/nsls2/LTE/kickmaps/orig_Radia/ARI_EPU70LV.txt`

2. Added `gen_C29_SXN_EPU50()` and `gen_C29_ARI_EPU70()` functions to
   `machine_data/nsls2/LTE/kickmaps/conversions/conversion_history.py`.

3. Ran conversion from `machine_data/nsls2/LTE/kickmaps/conversions/`:
   ```bash
   python conversion_history.py C29
   ```
   The `_wKm2sdds` step errors with `oagtclsh: not found` — expected and harmless
   (same behavior as C09 CDI). The `_woKm2sdds` files succeeded.

4. Copied final SDDS files to `official/`:
   ```bash
   cp SXN_EPU50LV_1o8m_T2m2_woKm2sdds.sdds ../official/
   cp ARI_EPU70LV_1o82m_T2m2_woKm2sdds.sdds ../official/
   ```

### Steps Completed (continued)

### Step 1 — Create Python Script

Created `20260623_add_C29_SXN_ARI_to_LTE.py` by copying from
`../20250905/20250905_add_C09_CDI_to_LTE.py` and adapting for C29:

- `RELEASE_DATE_STR = "20260623"`, `straight_cell_num = 29`
- `n_existing_ubpms = 49`, `n_existing_ukickmaps = 26` (6 DW + 20 non-DW)
- Source LTE: `../20260304/new_LTEs/20260304_aphla_layout_RelKMPaths.lte`
- Element names: `EPU50G1C29U` (upstream, 1.8m), `EPU70G1C29D` (downstream, 1.82m)
- 4 BPMs: `PU1G1C29A`–`PU4G1C29A`
- Kickmaps: `SXN_EPU50LV_1o8m_T2m2_woKm2sdds.sdds`, `ARI_EPU70LV_1o82m_T2m2_woKm2sdds.sdds`
- State names updated: `20ids` → `22ids` (22 non-DW IDs after this release)
- All `funcs_to_run` flags set to `False`
- **TODO before Phase 1**: set correct KREF values (currently `1.0` as placeholder) and
  adjust `target_dse`/`target_dsc` in `interactively_adjust_elements()` to match actual
  design requirements for the C29 EPU positions.

### Steps Remaining

- [ ] **Phase 1** — `gen_new_layout_LTE_file`
- [ ] **Phase 1** — `gen_new_layout_LTE_file` (set flag True, run, verify, adjust KREF + target positions, reset)
- [ ] **Phase 2** — `gen_ids_quads_states_yaml`
- [ ] **Phase 3** — `gen_insertion_device_states_yaml`
- [ ] **Phase 4** — `gen_new_model_LTE_files`
- [ ] **Phase 5** — `validate_new_LTE_files`
- [ ] **Phase 6** — `match_quads` (optional)
- [ ] **Phase 7** — `publicize_new_kickmap_files`
- [ ] **Phase 8** — `publicize_new_model_LTE_files`
