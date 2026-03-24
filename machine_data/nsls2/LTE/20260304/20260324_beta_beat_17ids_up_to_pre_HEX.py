"""
Beta beat computation: 17-ID lattice (20 IDs wo HEX, minus C09 CDI and C20 IFE)
vs. 3DW base lattice.

Run this script from:
  /nsls2/users/yhidaka/git_repos/aphla/machine_data/nsls2/LTE/20260304/

The kickmap INPUT_FILE paths in the LTE files are relative to the current
working directory (NOT to the LTE file location), so the script must be run
from 20260304/ for the remaining kickmap paths ("../kickmaps/official/...")
to resolve correctly.
"""

import re
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import pyelegant as pe

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent.resolve()

# 20-ID-wo-HEX lattice (contains C09 CDI as IVU18G1C09CM and C20 IFE as OVU68G1C20D)
LTE_20ids_wo_HEX_filepath = SCRIPT_DIR / "new_LTEs" / (
    "20260304_aphla_20ids_wo_HEX_Q_17ids_matched_VS_RelKMPaths.lte"
)

# 3DW base lattice
base_LTE_filepath = SCRIPT_DIR / "new_LTEs" / (
    "20260304_aphla_3dw_Q_day1_RelKMPaths.lte"
)

# Modified LTE (C09 CDI and C20 IFE kickmaps replaced with drifts)
mod_LTE_filepath = SCRIPT_DIR / (
    "20260304_aphla_17ids_Q_17ids_matched_VS_RelKMPaths_wo_C09CDI_C20IFE_C27HEX.lte"
)

# Output pgz files (written to cwd = SCRIPT_DIR)
twi_17ids_pgz = SCRIPT_DIR / "twi_17ids_wo_HEX_wo_C09CDI_C20IFE_C27HEX.pgz"
twi_3dw_pgz   = SCRIPT_DIR / "twi_3dw_base.pgz"

# ---------------------------------------------------------------------------
# ELEGANT settings
# ---------------------------------------------------------------------------
E_MeV = 3e3
USED_BEAMLINE = "RING"

N_KICKS = dict(CSBEND=40, KQUAD=40, KSEXT=8, KOCT=8)
ALTER_ELEMENTS_LIST = [
    dict(
        name="*",
        type=elem_type,
        item="N_KICKS",
        value=v,
        allow_missing_elements=True,
    )
    for elem_type, v in N_KICKS.items()
]

# ---------------------------------------------------------------------------
# Step 1 – Create modified LTE: replace C09 CDI and C20 IFE with drifts
# ---------------------------------------------------------------------------
def make_modified_lte(src: Path, dst: Path) -> None:
    """Replace the two UKICKMAP definitions with DRIF elements of the same L."""

    text = src.read_text()

    # C09 CDI: IVU18G1C09CM  UKICKMAP L=2.4
    old_c09 = (
        'IVU18G1C09CM: UKICKMAP, L=2.4, &\n'
        '   INPUT_FILE="../kickmaps/official/U18kickmap_2o4m_T2m2_woKm2sdds.sdds", &\n'
        '   N_KICKS=134, PERIODS=134, KREF=1.93'
    )
    new_c09 = 'IVU18G1C09CM: DRIF, L=2.4'

    # C20 IFE: OVU68G1C20D  UKICKMAP L=3.4
    old_c20 = (
        'OVU68G1C20D: UKICKMAP, L=3.4, &\n'
        '   INPUT_FILE="../kickmaps/official/U68kickmap_3o4m_T2m2_woKm2sdds.sdds", &\n'
        '   N_KICKS=50, PERIODS=50, KREF=4.5'
    )
    new_c20 = 'OVU68G1C20D: DRIF, L=3.4'

    assert old_c09 in text, "Could not find C09 CDI UKICKMAP definition"
    assert old_c20 in text, "Could not find C20 IFE UKICKMAP definition"

    text = text.replace(old_c09, new_c09)
    text = text.replace(old_c20, new_c20)

    dst.write_text(text)
    print(f"Modified LTE written to: {dst}")


if not mod_LTE_filepath.exists():
    make_modified_lte(LTE_20ids_wo_HEX_filepath, mod_LTE_filepath)
else:
    print(f"Modified LTE already exists: {mod_LTE_filepath}")

# ---------------------------------------------------------------------------
# Step 2 – Compute Twiss for both lattices
# ---------------------------------------------------------------------------
def run_twiss(lte_filepath: Path, output_pgz: Path) -> None:
    pe.calc_ring_twiss(
        str(output_pgz),
        str(lte_filepath),
        E_MeV,
        use_beamline=USED_BEAMLINE,
        alter_elements_list=ALTER_ELEMENTS_LIST,
    )
    print(f"Twiss saved to: {output_pgz}")


if not twi_17ids_pgz.exists():
    run_twiss(mod_LTE_filepath, twi_17ids_pgz)
else:
    print(f"17-ID twiss already exists: {twi_17ids_pgz}")

if not twi_3dw_pgz.exists():
    run_twiss(base_LTE_filepath, twi_3dw_pgz)
else:
    print(f"3DW twiss already exists: {twi_3dw_pgz}")

# ---------------------------------------------------------------------------
# Step 3 – Extract BPM data (P[HLM]* elements, 180 BPMs)
# ---------------------------------------------------------------------------
def extract_bpm_twiss(pgz_path: Path):
    """Return betax, betay, s at all P[HLM]* BPMs."""
    d = pe.util.load_pgz_file(str(pgz_path))
    arrays = d["data"]["twi"]["arrays"]
    scalars = d["data"]["twi"]["scalars"]

    elem_names = arrays["ElementName"]
    bpm_mask = np.array([bool(re.match(r'^P[HLM]', n)) for n in elem_names])

    n_bpms = bpm_mask.sum()
    print(f"  {pgz_path.name}: found {n_bpms} P[HLM]* BPMs")
    assert n_bpms == 180, f"Expected 180 BPMs, got {n_bpms}"

    return dict(
        names=elem_names[bpm_mask],
        betax=arrays["betax"][bpm_mask],
        betay=arrays["betay"][bpm_mask],
        s=arrays["s"][bpm_mask],
        nux=scalars["nux"],
        nuy=scalars["nuy"],
    )


print("Extracting twiss at BPMs...")
twi_17ids = extract_bpm_twiss(twi_17ids_pgz)
twi_3dw   = extract_bpm_twiss(twi_3dw_pgz)

# Verify BPM names match between the two lattices
assert np.all(twi_17ids["names"] == twi_3dw["names"]), \
    "BPM element names differ between the two lattices!"

# ---------------------------------------------------------------------------
# Step 4 – Plot beta beat
# ---------------------------------------------------------------------------
bpm_index = np.arange(180)
betax_beat = (twi_17ids["betax"] / twi_3dw["betax"] - 1.0) * 1e2  # [%]
betay_beat = (twi_17ids["betay"] / twi_3dw["betay"] - 1.0) * 1e2  # [%]

rms_betax = np.std(betax_beat)
rms_betay = np.std(betay_beat)

fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

ax = axes[0]
ax.plot(bpm_index, betax_beat, "b.-", ms=4)
ax.axhline(0.0, color="k", lw=0.8, ls="--")
ax.set_ylabel(
    r"$(\beta_x^{17\mathrm{ID}} / \beta_x^{3\mathrm{DW}} - 1) \times 100$ [%]"
)
ax.set_title(
    "Beta beat: 17-ID (wo C09 CDI, C20 IFE, & C27 HEX) vs. 3DW base\n"
    f"17ID: $\\nu_x={twi_17ids['nux']:.4f}$, $\\nu_y={twi_17ids['nuy']:.4f}$  |  "
    f"3DW: $\\nu_x={twi_3dw['nux']:.4f}$, $\\nu_y={twi_3dw['nuy']:.4f}$  |  "
    f"rms $\\Delta\\beta_x/\\beta_x$ = {rms_betax:.2f}%, "
    f"rms $\\Delta\\beta_y/\\beta_y$ = {rms_betay:.2f}%"
)
ax.grid(True, lw=0.4)

ax = axes[1]
ax.plot(bpm_index, betay_beat, "r.-", ms=4)
ax.axhline(0.0, color="k", lw=0.8, ls="--")
ax.set_ylabel(
    r"$(\beta_y^{17\mathrm{ID}} / \beta_y^{3\mathrm{DW}} - 1) \times 100$ [%]"
)
ax.set_xlabel("BPM index")
ax.grid(True, lw=0.4)

fig.tight_layout()
plot_path = SCRIPT_DIR / "20260324_beta_beat_17ids_wo_HEX_wo_C09CDI_C20IFE_C27HEX.png"
fig.savefig(str(plot_path), dpi=150, bbox_inches="tight")
print(f"Plot saved to: {plot_path}")

plt.show()
