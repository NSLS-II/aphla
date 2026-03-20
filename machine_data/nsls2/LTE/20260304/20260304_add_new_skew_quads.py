# Used conda env "apv2-2025-09" (aphla-2.1, pyelegant-0.13, srtool=3.1)
# to run this script.

from pathlib import Path
import re
import json
import gzip
import pickle
import shutil
from typing import Literal
import tempfile
from datetime import datetime

import numpy as np
from ruamel import yaml
from pydantic import BaseModel
import h5py
import matplotlib.pyplot as plt

import pyelegant as pe
import aphla as ap

ap.machines.load("nsls2", "SR")
ap.setOpModeStr("simulation")

APHLA_SR_PYELE_MODELS_FOLDER = Path(
    '/epics/aphla/apconf_v2/nsls2/models/SR/pyelegant')

# ### IMPORTANT NOTE ABOUT KICKMAP FILEPATHS ###
# Note that the relative filepath for a kickmap is w.r.t. the current directory,
# NOT w.r.t. the location of the LTE file OR the ELE file.
KM_OFFICIAL_LOCAL_FOLDER_STR = "../kickmaps/official"
KM_OFFICIAL_LOCAL_FOLDER_RE_PATTERN = r"\.\./kickmaps/official/"
KM_OFFICIAL_LOCAL_FOLDER = Path(KM_OFFICIAL_LOCAL_FOLDER_STR)

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

class LatticeFile(BaseModel):
    path: Path

class LayoutLatticeFile(LatticeFile):
    with_xbpms: bool

class IDsQuadsStateLatticeFile(LatticeFile):
    ids_state: str
    quads_state: str

class NewModelLatticeFile(LatticeFile):
    with_xbpms: bool
    ids_state: str
    quads_state: str

def get_ids_quads_state_LTE_key(f: IDsQuadsStateLatticeFile):
    return f"{f.ids_state}:{f.quads_state}"

def get_yaml_flow_style_list(L):

    L = yaml.comments.CommentedSeq(L)
    L.fa.set_flow_style()

    return L


def conv_yaml_dict_to_plain_dict(yaml_dict):

    return json.loads(json.dumps(yaml_dict))


def basic_lattice_integrity_check(LTE, straight_cell_num, n_existing_ubpms, n_existing_ukickmaps):

    LTE_d = LTE.get_used_beamline_element_defs()

    flat_used_elem_names = LTE_d["flat_used_elem_names"]
    elem_defs = LTE_d["elem_defs"]

    elem_names = [v[0] for v in elem_defs]
    elem_types = [v[1] for v in elem_defs]
    props = [v[2] for v in elem_defs]

    ordered_quad_names = [
        name
        for name in flat_used_elem_names
        if (elem_types[elem_names.index(name)] == "KQUAD")
        and "TILT" not in props[elem_names.index(name)]
    ]
    ordered_quad_counts = [
        flat_used_elem_names.count(name)
        for name in flat_used_elem_names
        if (elem_types[elem_names.index(name)] == "KQUAD")
        and "TILT" not in props[elem_names.index(name)]
    ]
    assert np.all(np.array(ordered_quad_counts) == 1)
    assert len(ordered_quad_names) == 300

    ordered_skquad_names = [
        name
        for name in flat_used_elem_names
        if (elem_types[elem_names.index(name)] == "KQUAD")
        and "TILT" in props[elem_names.index(name)]
    ]
    ordered_skquad_counts = [
        flat_used_elem_names.count(name)
        for name in flat_used_elem_names
        if (elem_types[elem_names.index(name)] == "KQUAD")
        and "TILT" in props[elem_names.index(name)]
    ]
    assert np.all(np.array(ordered_skquad_counts) == 2)
    ordered_skquad_names = np.array(ordered_skquad_names)
    assert np.all(ordered_skquad_names[::2] == ordered_skquad_names[1::2])
    ordered_skquad_names = ordered_skquad_names[::2].tolist()
    assert len(ordered_skquad_names) == 30 + 1 + 15 # "+1" for C16SQL "+15" for New SQ3H*

    ordered_sext_names = [
        name
        for name in flat_used_elem_names
        if (elem_types[elem_names.index(name)] == "KSEXT")
    ]
    ordered_sext_counts = [
        flat_used_elem_names.count(name)
        for name in flat_used_elem_names
        if (elem_types[elem_names.index(name)] == "KSEXT")
    ]
    assert np.all(np.array(ordered_sext_counts) == 1)
    assert len(ordered_sext_names) == 270

    ordered_bend_names = [
        name
        for name in flat_used_elem_names
        if (elem_types[elem_names.index(name)] == "CSBEND")
    ]
    ordered_bend_counts = [
        flat_used_elem_names.count(name)
        for name in flat_used_elem_names
        if (elem_types[elem_names.index(name)] == "CSBEND")
    ]
    assert np.all(np.array(ordered_bend_counts) == 1)
    assert len(ordered_bend_names) == 60

    ordered_rbpm_names = [
        name
        for name in flat_used_elem_names
        if (elem_types[elem_names.index(name)] == "MONI")
        and name.startswith(("PH", "PL", "PM"))
    ]
    ordered_rbpm_counts = [
        flat_used_elem_names.count(name)
        for name in flat_used_elem_names
        if (elem_types[elem_names.index(name)] == "MONI")
        and name.startswith(("PH", "PL", "PM"))
    ]
    assert np.all(np.array(ordered_rbpm_counts) == 1)
    assert len(ordered_rbpm_names) == 180

    ordered_ubpm_names = [
        name
        for name in flat_used_elem_names
        if (elem_types[elem_names.index(name)] == "MONI") and name.startswith(("PU",))
    ]
    ordered_ubpm_counts = [
        flat_used_elem_names.count(name)
        for name in flat_used_elem_names
        if (elem_types[elem_names.index(name)] == "MONI") and name.startswith(("PU",))
    ]
    assert np.all(np.array(ordered_ubpm_counts) == 1)

    assert len(ordered_ubpm_names) == n_existing_ubpms

    ordered_cor_names = [
        name
        for name in flat_used_elem_names
        if (elem_types[elem_names.index(name)] == "KICKER")
        and name.startswith(("CH", "CL", "CM"))
    ]
    ordered_cor_counts = [
        flat_used_elem_names.count(name)
        for name in flat_used_elem_names
        if (elem_types[elem_names.index(name)] == "KICKER")
        and name.startswith(("CH", "CL", "CM"))
    ]
    assert np.all(np.array(ordered_cor_counts) == 1)
    assert len(ordered_cor_names) == 360
    ordered_corY_names = []
    for n1, n2 in zip(ordered_cor_names[::2], ordered_cor_names[1::2]):
        if "YG" in n1:
            assert n1 == n2.replace("XG", "YG")
            ordered_corY_names.append(n1)
        else:
            assert n1.replace("XG", "YG") == n2
            ordered_corY_names.append(n2)
    assert len(ordered_corY_names) == 180
    ordered_cor_names = ordered_corY_names

    ordered_fcor_names = [
        name
        for name in flat_used_elem_names
        if (elem_types[elem_names.index(name)] == "KICKER") and name.startswith("F")
    ]
    ordered_fcor_counts = [
        flat_used_elem_names.count(name)
        for name in flat_used_elem_names
        if (elem_types[elem_names.index(name)] == "KICKER") and name.startswith("F")
    ]
    assert np.all(np.array(ordered_fcor_counts) == 1)
    assert len(ordered_fcor_names) == 90

    ordered_ukickmap_names = [
        name
        for name in flat_used_elem_names
        if (elem_types[elem_names.index(name)] == "UKICKMAP")
    ]
    ordered_ukickmap_counts = [
        flat_used_elem_names.count(name)
        for name in flat_used_elem_names
        if (elem_types[elem_names.index(name)] == "UKICKMAP")
    ]
    assert np.all(np.array(ordered_ukickmap_counts) == 1)

    assert len(ordered_ukickmap_names) == n_existing_ukickmaps

    all_variable_elem_names = (
        ordered_bend_names
        + ordered_quad_names
        + ordered_skquad_names
        + ordered_sext_names
        + ordered_cor_names
        + ordered_fcor_names
        + ordered_rbpm_names
        + ordered_ubpm_names
        + ordered_ukickmap_names
    )
    assert len(all_variable_elem_names) == len(np.unique(all_variable_elem_names))
    sort_inds = np.argsort(
        [flat_used_elem_names.index(name) for name in all_variable_elem_names]
    )
    all_variable_elem_names_ordered = np.array(all_variable_elem_names)[
        sort_inds
    ].tolist()

    # Mapping between element names and the indexes for the element definition list.
    elem_defs_index_maps = {}
    for name in all_variable_elem_names_ordered:
        i = elem_names.index(name)
        # print(name)
        # print(elem_defs[i])
        # print(LTE.parse_elem_properties(elem_defs[i][2]))
        elem_defs_index_maps[name] = i

    if straight_cell_num is None:
        return

    # Get upstream & downstream sextupole names that are bounding the straight
    us_sext_name = [
        v
        for v in all_variable_elem_names_ordered
        if (f"C{straight_cell_num-1:02d}" in v) and v.startswith(("SH", "SL")) and v.endswith(("A", "B"))
    ][-1]
    ds_sext_name = [
        v
        for v in all_variable_elem_names_ordered
        if (f"C{straight_cell_num:02d}" in v) and v.startswith(("SH", "SL")) and v.endswith(("A", "B"))
    ][0]

    iStart = flat_used_elem_names.index(us_sext_name)
    iEnd = flat_used_elem_names.index(ds_sext_name) + 1

    max_name_len = max([len(name) for name in flat_used_elem_names[iStart:iEnd]])

    header = f'{"Name":{max_name_len}s}' + " | Orig.L [m] |   se [m]   |" + f" {'Type':6s}"
    print(header)
    print("-" * len(header))
    straight_spos = 0.0
    orig_L = {}
    orig_se = (
        {}
    )  # s-pos at the end of each element relative to the straight beginning (s=0)
    for i in range(iStart, iEnd):
        name = flat_used_elem_names[i]
        j = elem_names.index(name)
        elem_type = elem_defs[j][1]
        prop_str = elem_defs[j][2]
        prop = LTE.parse_elem_properties(prop_str)
        L = prop.get("L", 0.0)
        if i in (iStart, iEnd - 1):
            s = np.nan
        else:
            straight_spos += L
            s = straight_spos
            orig_L[name] = L
            orig_se[name] = s

        print(f"{name:{max_name_len}s} | {L:10.6f} | {s:10.6f} | {elem_type}")

    is_cell_even = (straight_cell_num % 2 == 0)

    if is_cell_even:
        straight_end_spos = 9.3
    else:
        straight_end_spos = 6.6
    np.testing.assert_almost_equal(straight_spos, straight_end_spos, decimal=9)
    straight_center_spos = straight_end_spos / 2

    return (
        straight_end_spos,
        straight_center_spos,
        iStart,
        iEnd,
        flat_used_elem_names,
        elem_names,
        elem_defs,
        orig_L,
        max_name_len,
    )


def interactively_adjust_elements(
    straight_end_spos,
    straight_center_spos,
    iStart,
    iEnd,
    flat_used_elem_names,
    LTE,
    elem_names,
    elem_defs,
    orig_L,
    max_name_len,
):

    # target_sb [m]: s-pos of the element beginning w.r.t. the straight beginning
    # (i.e., se = 0 at the straight beginning)
    target_sb = {}
    # target_se [m]:
    # s-pos of the element ending w.r.t. the straight beginning
    # (i.e., se = 0 at the straight beginning)
    target_se = {}
    new_Ls = {
        "IDC09H2": 2.4,  # [m]; from the length of the kickmap
    }
    # target_dse [m]: s-pos of the element ending w.r.t. the straight center
    # (i.e., dse = 0 at the straight center)
    # WARNING: Don't use S1/S3 values for `v3localbump` IOC (or equivalently S1/S2 values
    # for active interlock PVs). Those would be correct only if the ID center is exactly at
    # the straight center.
    target_dse = {"PU1G1C09A": -2.5428, "PU4G1C09A": +2.6786}
    # target_dsc [m]: s-pos of the element center w.r.t. the straight center
    # (i.e., dsc = 0 at the straight center)
    target_dsc = {"IDC09H2": 0.0}

    target_se["PU1G1C09A"] = straight_center_spos + target_dse["PU1G1C09A"]
    target_se["IDC09H2"] = (
        straight_center_spos + target_dsc["IDC09H2"] + new_Ls["IDC09H2"] / 2
    )
    target_sb["IDC09H2"] = target_se["IDC09H2"] - new_Ls["IDC09H2"]
    target_se["DL06G1C09A"] = target_sb["IDC09H2"]
    target_se["PU4G1C09A"] = straight_center_spos + target_dse["PU4G1C09A"]
    target_se["GSG2C09A"] = straight_end_spos

    # key: element whose L will be adjusted
    # value: element whose "se" will be adjusted to the target "se" after L adjustment
    target_names = {
        "DL01G1C09A": "PU1G1C09A",
        "DL05G1C09A": "DL06G1C09A",
        "IDC09H2": "IDC09H2",
        "DL07G1C09A": "PU4G1C09A",
        "DL08G1C09A": "GSG2C09A",
    }
    # print(set(target_names.values()))
    # print(set(target_se.keys()))
    assert set(target_names.values()) == set(target_se.keys())
    for name_for_L_adj, name_for_target_se in target_names.items():
        new_Ls[name_for_L_adj] = 0.0  # Only initializing here

    header = f'{"Name":{max_name_len}s}' + " | Orig.L [m] |  New L [m] |   se [m]   "
    print(header)
    print("-" * len(header))
    straight_spos = 0.0
    for i in range(iStart, iEnd):
        name = flat_used_elem_names[i]
        j = elem_names.index(name)
        prop_str = elem_defs[j][2]
        prop = LTE.parse_elem_properties(prop_str)
        L = prop.get("L", 0.0)
        if i in (iStart, iEnd - 1):
            se = np.nan
            new_L = np.nan
        else:
            if name in new_Ls:
                # Update before applying change based on current "se"
                name_for_target_se = target_names[name]
                downstream_len = 0.0
                if name != name_for_target_se:
                    for k in range(i + 1, iEnd):
                        next_name = flat_used_elem_names[k]
                        downstream_len += orig_L[next_name]
                        if next_name == name_for_target_se:
                            break
                se_before_L_adj = straight_spos + orig_L[name] + downstream_len
                new_Ls[name] = orig_L[name] + (
                    target_se[name_for_target_se] - se_before_L_adj
                )

                new_L = new_Ls[name]
                straight_spos += new_L
            else:
                new_L = L
                straight_spos += L
            se = straight_spos

        if name in target_se:
            np.testing.assert_almost_equal(se, target_se[name], decimal=9)

        print(f"{name:{max_name_len}s} | {L:10.6f} | {new_L:10.6f} | {se:10.6f}")

    np.testing.assert_almost_equal(straight_spos, straight_end_spos, decimal=9)

    return new_Ls


def save_modified_LTE(
    new_LTE_filepath,
    used_beamline_name,
    LTE,
    elem_name_changes,
    elem_type_changes,
    new_Ls,
    other_new_props,
    new_elem_defs,
    new_beamline_defs,
):

    mod_LTE_d = LTE.get_persistent_used_beamline_element_defs(
        used_beamline_name=used_beamline_name
    )

    # Change element names/types:
    # - First change element definitions
    for i, (elem_name, elem_type, prop_str) in enumerate(mod_LTE_d["elem_defs"]):

        need_update = False
        if elem_name in elem_name_changes:
            need_update = True
            elem_name = elem_name_changes[elem_name]["name"]
        if elem_name in elem_type_changes:
            elem_type = elem_type_changes[elem_name]
            need_update = True
            assert prop_str.strip() == ""

        if need_update:
            mod_LTE_d["elem_defs"][i] = (elem_name, elem_type, prop_str)
    # - Then change beamline definitions (if so requested)
    for i, (BL_name, BL_def) in enumerate(mod_LTE_d["beamline_defs"]):
        need_update = False

        for j, (elem_or_BL_name, multiplier) in enumerate(BL_def):
            if elem_or_BL_name in elem_name_changes:
                if elem_name_changes[elem_or_BL_name]["update_in_beamline_def"]:
                    need_update = True
                    BL_def[j] = (elem_name_changes[elem_or_BL_name]["name"], multiplier)

        if need_update:
            mod_LTE_d["beamline_defs"][i] = (BL_name, BL_def)
    # -Also update "new_Ls" if needed
    for old_elem_name, new_elem_name_d in elem_name_changes.items():
        if old_elem_name in new_Ls:
            L = new_Ls[old_elem_name]
            del new_Ls[old_elem_name]
            new_elem_name = new_elem_name_d["name"]
            new_Ls[new_elem_name] = L
    # - Finally update "other_new_props" if needed
    for d in other_new_props:
        if d["elem_name"] in elem_name_changes:
            d["elem_name"] = elem_name_changes[d["elem_name"]]["name"]

    # Change element types
    for i, v in enumerate(mod_LTE_d["elem_defs"]):
        if v[0] in elem_type_changes:
            elem_name, elem_type, prop_str = v
            mod_LTE_d["elem_defs"][i] = (
                elem_name,
                elem_type_changes[elem_name],
                prop_str,
            )

    mod_prop_dict_list = [
        {"elem_name": name, "prop_name": "L", "prop_val": f"{new_L:.6g}"}
        for name, new_L in new_Ls.items()
    ]
    mod_prop_dict_list += other_new_props

    LTE.modify_elem_properties(mod_prop_dict_list)

    mod_LTE_d["elem_defs"].extend(new_elem_defs)

    for insertIndex, bl_def in new_beamline_defs:
        mod_LTE_d["beamline_defs"].insert(insertIndex, bl_def)

    LTE.write_LTE(
        new_LTE_filepath,
        used_beamline_name,
        mod_LTE_d["elem_defs"],
        mod_LTE_d["beamline_defs"],
    )


def _get_LTE_from_bug_fixed_ltemanager_Lattice(LTE_filepath, used_beamline_name):

    if True:
        LTE = pe.ltemanager.Lattice(
            LTE_filepath=LTE_filepath, used_beamline_name=used_beamline_name
        )
    else:
        # When `load_LTE` is called without `elem_files_root_folderpath` argument,
        # it sets `elem_files_root_folderpath=LTE_filepath.parent`, which should
        # NOT be (a bug to be fixed in PyELEGANT). Since the kickmap files are
        # located relative to cwd, we need to set `elem_files_root_folderpath=Path.cwd()`.

        # Note also that calling "pe.calc_ring_twiss()" will
        # result in "UKICKMAP file does not exist" messages when it creates
        # a ELE file for the "run_setup" block, due to the same bug above.
        # So, until this bug is fixed, you can ignore about the error messages
        # when you run "pe.calc_ring_twiss()"

        LTE = pe.ltemanager.Lattice()
        LTE.load_LTE(LTE_filepath=LTE_filepath, used_beamline_name=used_beamline_name,
                     elem_files_root_folderpath=Path.cwd())

    return LTE

def extract_ids_quads_state_from_LTE(
    LTE_filepath, used_beamline_name, elem_name_patterns, prop_names, n_expected_matches
):

    LTE = _get_LTE_from_bug_fixed_ltemanager_Lattice(LTE_filepath, used_beamline_name)

    LTE_d = LTE.get_used_beamline_element_defs(used_beamline_name=used_beamline_name)

    elem_names = [v[0] for v in LTE_d["elem_defs"]]

    mag_props = []
    for name_pat, prop_name, n_exp in zip(
        elem_name_patterns, prop_names, n_expected_matches
    ):
        matched_elem_names = [
            name for name in elem_names if re.match(name_pat, name) is not None
        ]

        assert len(matched_elem_names) == n_exp

        matched_elem_names = sorted(matched_elem_names)

        inds = [elem_names.index(name) for name in matched_elem_names]

        for i in inds:
            elem_name, elem_type, prop_str = LTE_d["elem_defs"][i]
            mag_props.append(
                get_yaml_flow_style_list(
                    [
                        elem_name,
                        prop_name,
                        LTE.parse_elem_properties(prop_str)[prop_name],
                    ]
                )
            )

    return mag_props


def gen_new_layout_LTE_file(straight_cell_num, n_existing_ubpms, n_existing_ukickmaps):

    if False:
        APHLA_MODELS_DIR = Path(ap.machines.HLA_CONFIG_DIR) / ap.facility_name / "models"
        orig_LTE_layout_filepath = str(APHLA_MODELS_DIR / "SR/pyelegant/LTEs/20190125_VS_nsls2sr17idsmt_SQLC16.lte")
    else:
        orig_LTE_layout_filepath = LTE_files['layout']['orig'].path

    # First, we will modify the original layout to add new elements
    # *) Adding C09 CDI ID Kickmap element
    # *) Adding ID BPMs P7 & P8 for C09 CDI ID


    # When running the next line, you may see many error messages like:
    #   Kickmap elment "OVU68G1C20D": File "/nsls2/users/yhidaka/git_repos/aphla/machine_data/nsls2/LTE/20230915/kickmaps/official/U68kickmap_3o4m_T2m2_woKm2sdds.sdds" does not exist.
    # due to the relative kickmap file path issues. You COULD ignore them and
    # proceed, because we only need to extract element location information here,
    # but it later may cause problems, so it's probably better to be fixed at this stage.
    base_LTE = _get_LTE_from_bug_fixed_ltemanager_Lattice(
        orig_LTE_layout_filepath, USED_BEAMLINE
    )

    (
        straight_end_spos,
        straight_center_spos,
        iStart,
        iEnd,
        flat_used_elem_names,
        elem_names,
        elem_defs,
        orig_L,
        max_name_len,
    ) = basic_lattice_integrity_check(
        base_LTE, straight_cell_num, n_existing_ubpms, n_existing_ukickmaps)

    # Interactively adjust this section to generate a desirable table
    new_Ls = interactively_adjust_elements(
        straight_end_spos,
        straight_center_spos,
        iStart,
        iEnd,
        flat_used_elem_names,
        base_LTE,
        elem_names,
        elem_defs,
        orig_L,
        max_name_len,
    )

    old_id_name = "IDC09H2"
    new_id_name = "IVU18G1C09CM"
    new_id_length = 2.4 # [m]
    new_id_period = 18e-3 # [m]
    elem_name_changes = {
        old_id_name: dict(name=new_id_name, update_in_beamline_def=True)
    }
    elem_type_changes = {
        new_id_name: "UKICKMAP",  # from drift
        "PU1G1C09A": "MONI",  # from drift
        "PU4G1C09A": "MONI",  # from drift
    }
    nkicks = int(np.ceil(new_id_length / new_id_period))
    if nkicks % 2 == 1:
        nkicks += 1 # Make it even, in case this kickmap needs to be split half later
    other_new_props = [
        dict(
            elem_name=new_id_name,
            prop_name="INPUT_FILE",
            prop_val=f'"{KM_OFFICIAL_LOCAL_FOLDER_STR}/U18kickmap_2o4m_T2m2_woKm2sdds.sdds"',
        ),
        dict(elem_name=new_id_name, prop_name="N_KICKS", prop_val=f"{nkicks}"),
        dict(elem_name=new_id_name, prop_name="PERIODS", prop_val=f"{nkicks}"),
        dict(elem_name=new_id_name, prop_name="KREF", prop_val="1.93"),
    ]

    new_elem_defs = []
    new_beamline_defs = []

    LTE_key = "new"
    new_LTE_layout_filepath = LTE_files['layout'][LTE_key].path

    save_modified_LTE(
        new_LTE_layout_filepath,
        USED_BEAMLINE,
        base_LTE,
        elem_name_changes,
        elem_type_changes,
        new_Ls,
        other_new_props,
        new_elem_defs,
        new_beamline_defs,
    )

    # Second, we will modify the new layout to add X-BPMs
    # *) Splitting kickmap elements at C03, C09 (new addition this time!),
    #    C16, and C17 into half and inserting X-BPMs at the middle
    n_new_ubpms = n_existing_ubpms + 2 # Added 2 BPMs for C09 CDI
    n_new_ukickmaps = n_existing_ukickmaps + 1 # Added 1 full-length kickmap for C09 CDI
    gen_new_layout_w_xbpms_LTE_file(
        new_LTE_layout_filepath,
        straight_cell_num, n_new_ubpms, n_new_ukickmaps
        )

    print("Finished.")

def gen_new_layout_w_xbpms_LTE_file(
        new_layout_LTE_wo_xbpms_filepath,
        n_base_ubpms, n_base_ukickmaps
        ):

    base_LTE = _get_LTE_from_bug_fixed_ltemanager_Lattice(
        new_layout_LTE_wo_xbpms_filepath, USED_BEAMLINE
    )

    straight_cell_num = None
    basic_lattice_integrity_check(
        base_LTE, straight_cell_num, n_base_ubpms, n_base_ukickmaps)


    elem_name_changes = {}
    other_new_props = []
    new_elem_defs = []
    new_beamline_defs = []

    # --- C03 ID ---
    old_id_name = "IVU20G1C03CM"
    new_id_name = old_id_name + "_HALF"
    elem_name_changes[old_id_name] = dict(
        name=new_id_name, update_in_beamline_def=False
    )
    for prop_name, prop_val in [
        ("L", "1.5"),
        (
            "INPUT_FILE",
            f'"{KM_OFFICIAL_LOCAL_FOLDER_STR}/U20_asbuilt_g52_1o5m_T2m2_woKm2sdds.sdds"',
        ),
        ("N_KICKS", "75"),
        ("PERIODS", "75"),
    ]:
        other_new_props.append(
            dict(elem_name=new_id_name, prop_name=prop_name, prop_val=prop_val)
        )

    # --- C16 ID ---
    old_id_name = "IVU23G1C16CM"
    new_id_name = old_id_name + "_HALF"
    elem_name_changes[old_id_name] = dict(
        name=new_id_name, update_in_beamline_def=False
    )
    for prop_name, prop_val in [
        ("L", "1.4"),
        (
            "INPUT_FILE",
            f'"{KM_OFFICIAL_LOCAL_FOLDER_STR}/U23L_asbuilt_g57_1o4m_T2m2_woKm2sdds.sdds"',
        ),
        ("N_KICKS", "61"),
        ("PERIODS", "61"),
    ]:
        other_new_props.append(
            dict(elem_name=new_id_name, prop_name=prop_name, prop_val=prop_val)
        )

    # --- C17 IDs ---
    for old_id_name in ["IVU21G1C17UM", "IVU21G1C17DM"]:
        new_id_name = old_id_name + "_HALF"
        elem_name_changes[old_id_name] = dict(
            name=new_id_name, update_in_beamline_def=False
        )
        for prop_name, prop_val in [
            ("L", "0.75"),
            (
                "INPUT_FILE",
                f'"{KM_OFFICIAL_LOCAL_FOLDER_STR}/U21_asbuilt_g64_0o75m_T2m2_woKm2sdds.sdds"',
            ),
            ("N_KICKS", "36"),
            ("PERIODS", "36"),
        ]:
            other_new_props.append(
                dict(
                    elem_name=new_id_name,
                    prop_name=prop_name,
                    prop_val=prop_val,
                )
            )

    # --- C09 ID ---
    old_id_name = "IVU18G1C09CM"
    new_id_name = old_id_name + "_HALF"
    elem_name_changes[old_id_name] = dict(
        name=new_id_name, update_in_beamline_def=False
    )
    d = base_LTE.get_elem_props_from_names([old_id_name])[old_id_name]
    L = d['properties']['L']
    new_L = L / 2
    np.testing.assert_almost_equal(new_L, 1.2, decimal=9)
    new_L_str = f"{new_L:.6g}"
    N_KICKS = d['properties']['N_KICKS']
    new_N_KICKS = N_KICKS // 2
    assert new_N_KICKS * 2 == N_KICKS
    new_N_KICKS_str = f"{new_N_KICKS:d}"
    for prop_name, prop_val in [
        ("L", new_L_str),
        (
            "INPUT_FILE",
            f'"{KM_OFFICIAL_LOCAL_FOLDER_STR}/U18kickmap_1o2m_T2m2_woKm2sdds.sdds"',
        ),
        ("N_KICKS", new_N_KICKS_str),
        ("PERIODS", new_N_KICKS_str),
    ]:
        other_new_props.append(
            dict(elem_name=new_id_name, prop_name=prop_name, prop_val=prop_val)
        )

    for insertIndex, (old_id_name, xbpm_name) in enumerate(
        [
            ("IVU20G1C03CM", "PX1G1C03A"),
            ("IVU23G1C16CM", "PX1G1C16A"),
            ("IVU21G1C17UM", "PX1G1C17A"),
            ("IVU21G1C17DM", "PX2G1C17A"),
            ("IVU18G1C09CM", "PX1G1C09A"),
        ]
    ):

        new_elem_defs.append((xbpm_name, "MONI", ""))

        new_id_name = old_id_name + "_HALF"
        new_beamline_defs.append(
            [
                insertIndex,
                (
                    old_id_name,
                    [(new_id_name, 1), (xbpm_name, 1), (new_id_name, 1)],
                ),
            ]
        )

    LTE_key = "new_w_xbpms"

    new_LTE_layout_filepath = LTE_files['layout'][LTE_key].path

    elem_type_changes = {}
    new_Ls = {}

    save_modified_LTE(
        new_LTE_layout_filepath,
        USED_BEAMLINE,
        base_LTE,
        elem_name_changes,
        elem_type_changes,
        new_Ls,
        other_new_props,
        new_elem_defs,
        new_beamline_defs,
    )

def gen_new_layout_LTE_file_with_new_SQs(n_existing_ubpms, n_existing_ukickmaps):

    orig_LTE_layout_filepath = LTE_files['layout']['orig'].path

    # First, we will modify the original layout to add new elements

    # ..., DH2BG6B, DSCH, CH1YG6C01B, CH1XG6C01B, DSCH, DH2AG6B, ...

    # =>

    # ..., DH2BG6B, SQ3HG6C01B, CH1YG6C01B, CH1XG6C01B, SQ3HG6C01B, DH2AG6B, ...

    # In other words, we convert "DSCH" into "SQ3HG6C01B".
    #
    # The naming convention "SQ3H" was chosen to mean "SQ" for skew quads, "3" for the
    # 3rd set of skew quads (SQH and SQM are already used for the 1st and 2nd sets of
    # skew quads), and "H" to indicate these are in the high-beta section, not "Half",
    # although these elements are split into half.

    # Same modification was applied manually for the following:
    #   CH1[XY]G6C01B
    #   CH1[XY]G6C03B
    #   CH1[XY]G6C05B
    #   CH1[XY]G6C07B
    #   ...
    #   CH1[XY]G6C29B

    # Manually added the following skew quad element definitions:
    # SQ3HG6C01B: KQUAD, L=0.1, TILT=0.78539816
    # SQ3HG6C03B: KQUAD, L=0.1, TILT=0.78539816
    # SQ3HG6C05B: KQUAD, L=0.1, TILT=0.78539816
    # SQ3HG6C07B: KQUAD, L=0.1, TILT=0.78539816
    # SQ3HG6C09B: KQUAD, L=0.1, TILT=0.78539816
    # SQ3HG6C11B: KQUAD, L=0.1, TILT=0.78539816
    # SQ3HG6C13B: KQUAD, L=0.1, TILT=0.78539816
    # SQ3HG6C15B: KQUAD, L=0.1, TILT=0.78539816
    # SQ3HG6C17B: KQUAD, L=0.1, TILT=0.78539816
    # SQ3HG6C19B: KQUAD, L=0.1, TILT=0.78539816
    # SQ3HG6C21B: KQUAD, L=0.1, TILT=0.78539816
    # SQ3HG6C23B: KQUAD, L=0.1, TILT=0.78539816
    # SQ3HG6C25B: KQUAD, L=0.1, TILT=0.78539816
    # SQ3HG6C27B: KQUAD, L=0.1, TILT=0.78539816
    # SQ3HG6C29B: KQUAD, L=0.1, TILT=0.78539816


    # When running the next line, you may see many error messages like:
    #   Kickmap elment "OVU68G1C20D": File "/nsls2/users/yhidaka/git_repos/aphla/machine_data/nsls2/LTE/20230915/kickmaps/official/U68kickmap_3o4m_T2m2_woKm2sdds.sdds" does not exist.
    # due to the relative kickmap file path issues. You COULD ignore them and
    # proceed, because we only need to extract element location information here,
    # but it later may cause problems, so it's probably better to be fixed at this stage.
    # =>
    # I didn't see those error messages anymore, which means the kickmap file paths are now correctly resolved.
    base_LTE = _get_LTE_from_bug_fixed_ltemanager_Lattice(
        orig_LTE_layout_filepath, USED_BEAMLINE
    )

    LTE_key = "new"
    new_LTE_layout_filepath = LTE_files['layout'][LTE_key].path

    shutil.copyfile(orig_LTE_layout_filepath, new_LTE_layout_filepath)

    # Second, we will modify the new layout to add X-BPMs
    # *) Splitting kickmap elements at C03, C09, C16, and C17 into half and inserting
    #    X-BPMs at the middle
    n_new_ubpms = n_existing_ubpms # No newly added BPMs this time
    n_new_ukickmaps = n_existing_ukickmaps # No newly added kickmap this time
    gen_new_layout_w_xbpms_LTE_file(
        new_LTE_layout_filepath, n_new_ubpms, n_new_ukickmaps
        )

    print("Finished.")



def gen_ids_quads_states_yaml():

    ids_quads_states = {}

    (elem_name_patterns, prop_names, n_expected_matches) = list(
        zip(*[(r"Q[HLM]\w+", "K1", 300)])
    )

    for lat_name, lat_file in LTE_files['ids_quads_state'].items():
        ids_state, quads_state = lat_name.split(":")

        ids_quads_states[f"{ids_state}:{quads_state}"] = extract_ids_quads_state_from_LTE(
            lat_file.path,
            USED_BEAMLINE,
            elem_name_patterns,
            prop_names,
            n_expected_matches,
        )


    y = yaml.YAML()
    y.width = 110
    y.boolean_representation = ["False", "True"]
    y.indent(
        mapping=2, sequence=2, offset=2
    )  # Default: (mapping=2, sequence=2, offset=0)

    yaml_filepath = YAML_fps["ids_quads_states"]

    with open(yaml_filepath, "w") as f:
        y.dump(ids_quads_states, f)

    print("Finished")


def gen_insertion_device_states_yaml():

    states = {}

    for layout_type in ["new", "new_w_xbpms"]:

        layout_LTE_filepath = LTE_files['layout'][layout_type].path

        LTE = _get_LTE_from_bug_fixed_ltemanager_Lattice(
            layout_LTE_filepath, USED_BEAMLINE)


        LTE_d = LTE.get_used_beamline_element_defs(used_beamline_name=USED_BEAMLINE)
        elem_defs = LTE_d["elem_defs"]
        elem_names = [v[0] for v in elem_defs]

        km_elem_names = list(LTE.get_kickmap_filepaths()["abs"])
        km_elem_names = sorted(km_elem_names)

        state_name = layout_type.replace("new", "bare")
        states[state_name] = dict(
            elem_type_changes={name: "EDRIFT" for name in km_elem_names},
            elem_prop_changes=[],
        )
        for name in list(states[state_name]["elem_type_changes"]):
            i = elem_names.index(name)
            L = LTE.parse_elem_properties(elem_defs[i][2])["L"]
            states[state_name]["elem_prop_changes"].append(
                get_yaml_flow_style_list([name, "L", f"{L:.6g}"])
            )

        state_name = layout_type.replace("new", "3dw")
        if False:
            states[state_name] = dict(
                elem_type_changes={},
                elem_prop_changes=[
                    get_yaml_flow_style_list([name, "FIELD_FACTOR", "0.0"])
                    for name in km_elem_names
                    if not name.startswith("DW100G1")
                ],
            )
        else:
            states[state_name] = dict(
                elem_type_changes={
                    name: "EDRIFT"
                    for name in km_elem_names
                    if not name.startswith("DW100G1C")
                },
                elem_prop_changes=[],
            )
            for name in list(states[state_name]["elem_type_changes"]):
                i = elem_names.index(name)
                L = LTE.parse_elem_properties(elem_defs[i][2])["L"]
                states[state_name]["elem_prop_changes"].append(
                    get_yaml_flow_style_list([name, "L", f"{L:.6g}"])
                )

        # --- You probably need to update the sections from this point on,
        # if you are updating this script. ---

        # All 20 non-DW IDs, i.e., C27 HEX, C20 IFE, & C09 CDI all closed
        state_name = layout_type.replace("new", "20ids")
        states[state_name] = dict(elem_type_changes={}, elem_prop_changes=[])

        common_args = (states, km_elem_names, elem_names, elem_defs, LTE)

        # Out of all 20 non-DW IDs, only C27 HEX is opened.
        state_name = layout_type.replace("new", "20ids_wo_HEX")
        id_elem_names_to_open = ["SCW70G1C27D"]
        _add_new_ids_state(state_name, id_elem_names_to_open, *common_args)

        # Out of all 20 non-DW IDs, only C20 IFE is opened.
        state_name = layout_type.replace("new", "20ids_wo_IFE")
        id_elem_names_to_open = ["OVU68G1C20D"]
        _add_new_ids_state(state_name, id_elem_names_to_open, *common_args)

        # Out of all 20 non-DW IDs, only C20 IFE & C27 HEX are opened.
        state_name = layout_type.replace("new", "20ids_wo_IFE_HEX")
        id_elem_names_to_open = ["OVU68G1C20D", "SCW70G1C27D"]
        _add_new_ids_state(state_name, id_elem_names_to_open, *common_args)


    y = yaml.YAML()
    y.width = 110
    y.boolean_representation = ["False", "True"]
    y.indent(
        mapping=2, sequence=2, offset=2
    )  # Default: (mapping=2, sequence=2, offset=0)

    yaml_filepath = YAML_fps["ids_states"]

    with open(yaml_filepath, "w") as f:
        y.dump(states, f)

    print("Finished")

def _add_new_ids_state(
        state_name, id_elem_names_to_open, states, km_elem_names, elem_names,
        elem_defs, LTE):

    states[state_name] = dict(
        elem_type_changes={
            name: "EDRIFT"
            for name in km_elem_names
            if name in id_elem_names_to_open
        },
        elem_prop_changes=[],
    )
    for name in list(states[state_name]["elem_type_changes"]):
        i = elem_names.index(name)
        L = LTE.parse_elem_properties(elem_defs[i][2])["L"]
        states[state_name]["elem_prop_changes"].append(
            get_yaml_flow_style_list([name, "L", f"{L:.6g}"])
        )


def gen_new_model_LTE_files():
    """
    This function most likely does NOT need to be updated when you are
    updating this script.
    """

    y = yaml.YAML()
    ids_quads_states = conv_yaml_dict_to_plain_dict(
        y.load(Path(YAML_fps["ids_quads_states"]).read_text())
    )
    ids_states = conv_yaml_dict_to_plain_dict(
        y.load(Path(YAML_fps["ids_states"]).read_text())
    )

    for layout_type in ["new", "new_w_xbpms"]:

        layout_LTE_filepath = LTE_files['layout'][layout_type].path

        for lat_file in LTE_files['new_model']:

            if lat_file.with_xbpms:
                if layout_type != "new_w_xbpms":
                    continue
                xbpms_suffix = '_w_xbpms'
            else:
                if layout_type != "new":
                    continue
                xbpms_suffix = ''

            new_LTE_filepath = lat_file.path
            ids_state = lat_file.ids_state
            quads_state = lat_file.quads_state

            ids_quads_state = f"{ids_state}:{quads_state}"

            ids_state_w_xbpms_suffix = f"{ids_state}{xbpms_suffix}"

            assert ids_state_w_xbpms_suffix in ids_states, f"Error: {ids_state_w_xbpms_suffix} is not found in the ID states YAML file."
            assert ids_quads_state in ids_quads_states, f"Error: {quads_state} is not found in the quad settings YAML file."

            base_LTE = _get_LTE_from_bug_fixed_ltemanager_Lattice(
                layout_LTE_filepath, USED_BEAMLINE)

            mod_LTE_d = base_LTE.get_persistent_used_beamline_element_defs(
                used_beamline_name=USED_BEAMLINE
            )

            # Change element types, if necessary
            elem_type_changes = ids_states[ids_state_w_xbpms_suffix]["elem_type_changes"]
            if elem_type_changes != {}:
                for i, v in enumerate(mod_LTE_d["elem_defs"]):
                    if v[0] in elem_type_changes:
                        elem_name, elem_type, prop_str = v
                        prop_str = ""  # Should delete all properties as the type has been changed
                        mod_LTE_d["elem_defs"][i] = (
                            elem_name,
                            elem_type_changes[elem_name],
                            prop_str,
                        )

            # Change element properties, if necessary
            mod_prop_dict_list = [
                dict(
                    elem_name=elem_name,
                    prop_name=prop_name,
                    prop_val=f"{prop_val:.16g}",
                )
                for elem_name, prop_name, prop_val in ids_quads_states[ids_quads_state]
            ]
            for elem_name, prop_name, prop_val_str in ids_states[ids_state_w_xbpms_suffix][
                "elem_prop_changes"
            ]:
                mod_prop_dict_list.append(
                    dict(
                        elem_name=elem_name, prop_name=prop_name, prop_val=prop_val_str
                    )
                )

            base_LTE.modify_elem_properties(mod_prop_dict_list)

            base_LTE.write_LTE(
                new_LTE_filepath,
                USED_BEAMLINE,
                mod_LTE_d["elem_defs"],
                mod_LTE_d["beamline_defs"],
            )

    print("Finished.")


def validate_new_LTE_files(
        load_from_proc, straight_cell_num, n_existing_ubpms, n_existing_ukickmaps,
        new_ubpm_names, new_kickmap_elem_names):

    twi_filepath = f"{RELEASE_DATE_STR}_aphla_twiss.pgz"
    if not load_from_proc:
        output_filepath = "test.pgz"
        E_MeV = 3e3
        twi_layouts = {}
        twi_ids_quads_states = {}
        twi_new_models = {}

        for k, lat in LTE_files['layout'].items():
            print(f"layout:{k} ==> {lat.path}")

            pe.calc_ring_twiss(
                output_filepath, lat.path, E_MeV, use_beamline=USED_BEAMLINE,
                alter_elements_list=ALTER_ELEMENTS_LIST
            )

            twi_layouts[k] = pe.util.load_pgz_file(output_filepath)["data"]["twi"]

        for k, lat in LTE_files['ids_quads_state'].items():
            print(f"ids_quads_state:{k} ==> {lat.path}")

            pe.calc_ring_twiss(
                output_filepath, lat.path, E_MeV, use_beamline=USED_BEAMLINE,
                alter_elements_list=ALTER_ELEMENTS_LIST
            )

            twi_ids_quads_states[k] = pe.util.load_pgz_file(output_filepath)["data"]["twi"]


        for lat in LTE_files['new_model']:
            print(f"new_model: {lat.path}")

            pe.calc_ring_twiss(
                output_filepath, lat.path, E_MeV, use_beamline=USED_BEAMLINE,
                alter_elements_list=ALTER_ELEMENTS_LIST
            )

            twi_new_models[lat.path] = pe.util.load_pgz_file(output_filepath)["data"]["twi"]

        with gzip.GzipFile(twi_filepath, "wb") as f:
            pickle.dump([twi_layouts, twi_ids_quads_states, twi_new_models], f)

    with gzip.GzipFile(twi_filepath, "rb") as f:
        twi_layouts, twi_ids_quads_states, twi_new_models = pickle.load(f)

    # UKICKMAP elements are split in half for those that have X-BPMs for
    # the lattices with the "_w_xbpms" layout.
    split_km_elem_names = [
        "IVU20G1C03CM",
        "IVU18G1C09CM",
        "IVU23G1C16CM",
        "IVU21G1C17UM",
        "IVU21G1C17DM",
    ]

    # Check the known numbers of elements using the original layout lattice
    d = twi_layouts['orig']
    ar = d["arrays"]

    # Check the number of quads
    quad_names = [
        name
        for name in ar["ElementName"]
        if re.match(r"^Q[HLM]\dG\w+", name) is not None
    ]
    assert len(quad_names) == 300

    # Check the number of Day-1 skew quads
    skquad_names = [
        name for name in ar["ElementName"] if re.match(r"^SQ[HM]G\w+", name) is not None
    ]
    assert len(skquad_names) == 30 * 2  # "*2" for half-splitting

    # Check the number of skew quads added later
    skquad_names_C16SQL = [
        name for name in ar["ElementName"] if re.match(r"^SQLG\w+", name) is not None
    ]
    assert len(skquad_names_C16SQL) == 1 * 2  # "1" for C16SQL; "*2" for half-splitting

    # Check the number of sextupoles
    sext_names = [
        name
        for name in ar["ElementName"]
        if re.match(r"^S[HLM]\dG\w+", name) is not None
    ]
    assert len(sext_names) == 270

    # Check the number of bends
    bend_names = [
        name for name in ar["ElementName"] if re.match(r"^B[12]G\w+", name) is not None
    ]
    assert len(bend_names) == 30 * 2

    # Check the number of slow orbit correctors
    scor_names = [
        name
        for name in ar["ElementName"]
        if re.match(r"^C[HLM]\dYG\w+", name) is not None
    ]
    assert len(scor_names) == 180

    # Check the number of fast orbit correctors
    fcor_names = [
        name
        for name in ar["ElementName"]
        if re.match(r"^F[HLM]\dG\w+", name) is not None
    ]
    assert len(fcor_names) == 90

    # Check the number of regular (arc) BPMs
    rbpm_names = [
        name
        for name in ar["ElementName"]
        if re.match(r"^P[HLM][1-3]\w+", name) is not None
    ]
    assert len(rbpm_names) == 180
    orig_ubpm_names = [
        elem_name
        for elem_name, elem_type in zip(ar["ElementName"], ar["ElementType"])
        if (re.match(r"^PU[1-4]\w+", elem_name) is not None) and (elem_type == "MONI")
    ]

    # Check the number of ID BPMs (for the original layout, i.e., not the new one)
    orig_n_ubpms = n_existing_ubpms
    assert len(orig_ubpm_names) == orig_n_ubpms
    orig_ukickmap_names = [
        elem_name
        for elem_name, elem_type in zip(ar["ElementName"], ar["ElementType"])
        if elem_type == "UKICKMAP"
    ]
    orig_n_ukickmaps = n_existing_ukickmaps
    assert len(orig_ukickmap_names) == orig_n_ukickmaps

    all_twis = {**twi_layouts, **twi_ids_quads_states, **twi_new_models}
    all_twis_wo_ids_quads_states = {**twi_layouts, **twi_new_models}

    # --- Check circumference ---
    circumf = 791.958
    for lat_name, d in all_twis.items():
        ar = d["arrays"]
        np.testing.assert_almost_equal(ar["s"][-1], circumf, decimal=10)

    # --- Check end s-pos has not moved for all existing major elements ---
    ref_ar = twi_layouts["orig"]["arrays"]
    ref_elem_names = ref_ar["ElementName"].tolist()
    # First check all the elements that existed since Day-1
    for sel_elem_names in [
        bend_names,
        quad_names,
        skquad_names,
        sext_names,
        scor_names,
        fcor_names,
        rbpm_names,
    ]:
        ref_spos = np.array(
            [ref_ar["s"][ref_elem_names.index(name)] for name in sel_elem_names]
        )
        for _, d in all_twis_wo_ids_quads_states.items():
            ar = d["arrays"]
            elem_names = ar["ElementName"].tolist()
            spos = np.array(
                [ar["s"][elem_names.index(name)] for name in sel_elem_names]
            )
            np.testing.assert_almost_equal(spos, ref_spos, decimal=10)
    # Then check newer elements, but must exclude the old lattices during this check
    for sel_elem_names in [skquad_names_C16SQL, orig_ubpm_names, orig_ukickmap_names]:
        ref_spos = np.array(
            [ref_ar["s"][ref_elem_names.index(name)] for name in sel_elem_names]
        )
        for lat_name, d in all_twis_wo_ids_quads_states.items():
            lat_name = str(lat_name)
            if lat_name.startswith(()):
                continue  # These selected elements didn't exist in these old lattice files.
            else:
                ar = d["arrays"]
                elem_names = ar["ElementName"].tolist()
                try:
                    spos = np.array(
                        [ar["s"][elem_names.index(name)] for name in sel_elem_names]
                    )
                except ValueError:
                    if lat_name in twi_layouts:
                        assert LTE_files['layout'][lat_name].with_xbpms
                    else:
                        for lat in LTE_files['new_model']:
                            if Path(lat_name) == lat.path:
                                break
                        else:
                            raise
                        assert lat.with_xbpms
                    spos = []
                    for name in sel_elem_names:
                        if name in split_km_elem_names:
                            us_i = elem_names.index(f"{name}_HALF")
                            ds_i = us_i + 2
                            assert elem_names[ds_i] == f"{name}_HALF"
                            spos.append(ar["s"][ds_i])
                        else:
                            spos.append(ar["s"][elem_names.index(name)])
                    spos = np.array(spos)
                np.testing.assert_almost_equal(spos, ref_spos, decimal=10)

    # --- Check differences between "orig_layout" and "new_model" LTE files are
    # only the newly added elements ---
    new_n_ubpms = orig_n_ubpms + len(new_ubpm_names)
    new_n_ukickmaps = {
        "bare": 0,
        "3dw": 2 * 3,  # 2 kickmap elemes at C08, C18, C28
        "20ids": orig_n_ukickmaps + len(new_kickmap_elem_names),
    }
    new_n_ukickmaps["20ids_wo_HEX"] = new_n_ukickmaps["20ids"] - 1
    new_n_ukickmaps["20ids_wo_IFE"] = new_n_ukickmaps["20ids"] - 1
    new_n_ukickmaps["20ids_wo_IFE_HEX"] = new_n_ukickmaps["20ids"] - 2
    for k in list(new_n_ukickmaps):
        new_n_ukickmaps[k + "_w_xbpms"] = new_n_ukickmaps[k]
    # The lattices with X-BPMs have additional kickmap elements due to splitting
    # the kickmap elements into half at C03, C09, C16, C17-1, and C17-2.
    for k in ['20ids', '20ids_wo_HEX', '20ids_wo_IFE', '20ids_wo_IFE_HEX']:
        new_n_ukickmaps[k + "_w_xbpms"] += 5

    orig_ukickmap_names_w_xbpms = []
    for name in orig_ukickmap_names:
        if name in split_km_elem_names:
            orig_ukickmap_names_w_xbpms.append(f"{name}_HALF")
        else:
            orig_ukickmap_names_w_xbpms.append(name)

    for lat_name, d in twi_new_models.items():

        ar = d["arrays"]

        found_new_ubpm_names = [
            elem_name
            for elem_name, elem_type in zip(ar["ElementName"], ar["ElementType"])
            if (re.match(r"^PU[1-4]\w+", elem_name) is not None)
            and (elem_type == "MONI")
        ]
        assert len(found_new_ubpm_names) == new_n_ubpms
        assert all([(name in found_new_ubpm_names) for name in orig_ubpm_names])
        assert np.all(
            np.sort([name for name in found_new_ubpm_names if name not in orig_ubpm_names])
            == np.sort(new_ubpm_names)
        )

        matched_lat = [lat for lat in LTE_files['new_model'] if lat.path == lat_name]
        assert len(matched_lat) == 1
        matched_lat = matched_lat[0]

        ids_state = matched_lat.ids_state

        found_new_ukickmap_names = [
            elem_name
            for elem_name, elem_type in zip(ar["ElementName"], ar["ElementType"])
            if elem_type == "UKICKMAP"
        ]

        if matched_lat.with_xbpms:
            ukickmap_key = f"{ids_state}_w_xbpms"
        else:
            ukickmap_key = ids_state
        assert len(found_new_ukickmap_names) == new_n_ukickmaps[ukickmap_key]

        if ids_state == "bare":
            # All kickmap elements in bare lattice have been converted to drifts.
            assert found_new_ukickmap_names == []
        elif ids_state == "3dw":
            assert all([name.startswith("DW100G1C") for name in found_new_ukickmap_names])
            continue  # Kickmap elements except for DWs have been converted to drifts.
        elif ids_state.startswith("20ids"):
            if not matched_lat.with_xbpms:
                _orig_ukickmap_names = orig_ukickmap_names[:]
            else:
                _orig_ukickmap_names = orig_ukickmap_names_w_xbpms[:]

            if ids_state == "20ids":
                adjusted_orig_ukickmap_names = _orig_ukickmap_names[:]
            elif ids_state == "20ids_wo_HEX":
                adjusted_orig_ukickmap_names = [
                    name for name in _orig_ukickmap_names if name != "SCW70G1C27D"
                ]
            elif ids_state == "20ids_wo_IFE":
                adjusted_orig_ukickmap_names = [
                    name for name in _orig_ukickmap_names if name != "OVU68G1C20D"
                ]
            elif ids_state == "20ids_wo_IFE_HEX":
                adjusted_orig_ukickmap_names = [
                    name
                    for name in _orig_ukickmap_names
                    if name not in ("OVU68G1C20D", "SCW70G1C27D")
                ]
            else:
                raise ValueError(f"Unexpected ids_state: {ids_state}")

            assert all(
                [
                    (name in found_new_ukickmap_names)
                    for name in adjusted_orig_ukickmap_names
                ]
            )

            found_names_not_in_orig = np.unique(
                [
                    name
                    for name in found_new_ukickmap_names
                    if (name not in adjusted_orig_ukickmap_names)
                ]
            )
            assert np.all(
                found_names_not_in_orig
                == np.sort([f"{name}_HALF" if matched_lat.with_xbpms and (name in split_km_elem_names) else name for name in new_kickmap_elem_names])
            )


        else:
            raise ValueError(f"Unexpected ids_state_name: {ids_state}")

    if straight_cell_num is not None:
        straight_center_spos = straight_cell_num * (circumf / 30)

        # --- Check lengths & s-pos (`se`, i.e., ending s-pos) of
        #     newly added elements ---
        expected_Ls = {"IVU18G1C09CM": 2.4}
        id_center_offsets = {"IVU18G1C09CM": 0.0}
        expected_ses = {
            "IVU18G1C09CM": straight_center_spos + id_center_offsets["IVU18G1C09CM"] + expected_Ls["IVU18G1C09CM"] / 2,
            "PU1G1C09A": straight_center_spos - 2.5428,
            "PU4G1C09A": straight_center_spos + 2.6786,
        }

        d_list = [twi_layouts['new']]
        for lat_path, d in twi_new_models.items():
            matched_lat = [lat for lat in LTE_files['new_model'] if lat.path == lat_path]
            assert len(matched_lat) == 1
            matched_lat = matched_lat[0]
            if not matched_lat.with_xbpms:
                d_list.append(d)

        for d in d_list:
            ar = d["arrays"]
            elem_names = ar["ElementName"].tolist()

            for name, desired in expected_Ls.items():
                i = elem_names.index(name)
                L = ar["s"][i] - ar["s"][i - 1]
                np.testing.assert_almost_equal(L, desired, decimal=12)

            for name, desired in expected_ses.items():
                i = elem_names.index(name)
                np.testing.assert_almost_equal(ar["s"][i], desired, decimal=12)

        if "IVU18G1C09CM" in expected_Ls:
            expected_Ls["IVU18G1C09CM_HALF"] = expected_Ls["IVU18G1C09CM"] / 2
            del expected_Ls["IVU18G1C09CM"]
        if "IVU18G1C09CM" in expected_ses:
            expected_ses["IVU18G1C09CM_HALF"] = expected_ses["IVU18G1C09CM"] - expected_Ls["IVU18G1C09CM_HALF"]
            del expected_ses["IVU18G1C09CM"]
    else:
        expected_Ls = {}
        expected_ses = {}

    expected_Ls["IVU20G1C03CM_HALF"] = 1.5
    expected_Ls["IVU18G1C09CM_HALF"] = 1.2
    expected_Ls["IVU23G1C16CM_HALF"] = 1.4
    expected_Ls["IVU21G1C17UM_HALF"] = 0.75
    expected_Ls["IVU21G1C17DM_HALF"] = 0.75
    expected_ses["PX1G1C03A"] = 79.1958 # = 791.958 / 30 * 3 = 79.1958
    expected_ses["PX1G1C09A"] = 237.5874 # = 791.958 / 30 * 9 = 237.5874
    expected_ses["PX1G1C16A"] = 422.378
    expected_ses["PX1G1C17A"] = 447.455
    expected_ses["PX2G1C17A"] = 450.082

    d_list = [twi_layouts['new_w_xbpms']]
    for lat_path, d in twi_new_models.items():
        matched_lat = [lat for lat in LTE_files['new_model'] if lat.path == lat_path]
        assert len(matched_lat) == 1
        matched_lat = matched_lat[0]
        if matched_lat.with_xbpms:
            d_list.append(d)

    for d in d_list:
        ar = d["arrays"]
        elem_names = ar["ElementName"].tolist()

        for name, desired in expected_Ls.items():
            i = elem_names.index(name)
            L = ar["s"][i] - ar["s"][i - 1]
            np.testing.assert_almost_equal(L, desired, decimal=12)

        for name, desired in expected_ses.items():
            i = elem_names.index(name)
            np.testing.assert_almost_equal(ar["s"][i], desired, decimal=12)

    # --- Check quads state ---
    (elem_name_patterns, prop_names, n_expected_matches) = list(
        zip(*[(r"Q[HLM]\w+", "K1", 300)])
    )

    for k, ref_lat in LTE_files['ids_quads_state'].items():
        ids_state, quads_state = k.split(":")
        assert ref_lat.ids_state == ids_state
        assert ref_lat.quads_state == quads_state

        ref = extract_ids_quads_state_from_LTE(
            ref_lat.path,
            USED_BEAMLINE,
            elem_name_patterns,
            prop_names,
            n_expected_matches,
        )

        ref_d = {name: v for name, _, v in ref}

        for new_lat in LTE_files['new_model']:
            if not (new_lat.ids_state == ids_state and new_lat.quads_state == quads_state):
                continue

            new = extract_ids_quads_state_from_LTE(
                new_lat.path,
                USED_BEAMLINE,
                elem_name_patterns,
                prop_names,
                n_expected_matches,
            )

            new_d = {name: v for name, _, v in new}

            print(f"Ref. {ids_state}:{quads_state} --- Checking quads state for {new_lat.path}")

            assert [ref_d[k] == new_d[k] for k in ref_d.keys()]

    # --- Check tunes, chroms, beta functions, dispersions ---
    for k, ref_lat in LTE_files['ids_quads_state'].items():
        ids_state, quads_state = k.split(":")
        assert ref_lat.ids_state == ids_state
        assert ref_lat.quads_state == quads_state

        ref_twi = twi_ids_quads_states[k]
        ref_sc = ref_twi['scalars']
        ref_ar = ref_twi['arrays']
        elem_names = ref_ar["ElementName"].tolist()
        bpm_inds = [elem_names.index(name) for name in rbpm_names]
        ref_betax = ref_ar["betax"][bpm_inds]
        ref_betay = ref_ar["betay"][bpm_inds]
        ref_etax = ref_ar["etax"][bpm_inds]

        print(
            f"Reference {ids_state}:{quads_state}: nux = {ref_sc['nux']:.3f}, nuy = {ref_sc['nuy']:.3f}"
        )

        for new_lat in LTE_files['new_model']:
            if not (new_lat.ids_state == ids_state and new_lat.quads_state == quads_state):
                continue

            # None of the reference lattices can agree with "20ids" new models
            # because they contain the C09 CDI kickmap. So, exclude those here.
            if new_lat.ids_state.startswith("20ids"):
                continue

            print(f"Ref. {ids_state}:{quads_state} --- Checking tunes etc. for {new_lat.path}")

            sc = twi_new_models[new_lat.path]["scalars"]
            ar = twi_new_models[new_lat.path]["arrays"]

            # print(sc['nux'] - ref_sc['nux'])
            np.testing.assert_almost_equal(sc["nux"], ref_sc["nux"], decimal=7)
            np.testing.assert_almost_equal(sc["nuy"], ref_sc["nuy"], decimal=7)
            np.testing.assert_almost_equal(sc["dnux/dp"], ref_sc["dnux/dp"], decimal=5)
            np.testing.assert_almost_equal(sc["dnuy/dp"], ref_sc["dnuy/dp"], decimal=5)

            elem_names = ar["ElementName"].tolist()
            bpm_inds = [elem_names.index(name) for name in rbpm_names]
            betax = ar["betax"][bpm_inds]
            betay = ar["betay"][bpm_inds]
            etax = ar["etax"][bpm_inds]
            if False:
                np.testing.assert_almost_equal(betax, ref_betax, decimal=5)
                np.testing.assert_almost_equal(betay, ref_betay, decimal=4)
                np.testing.assert_almost_equal(etax, ref_etax, decimal=16)
            else:
                np.testing.assert_allclose(betax, ref_betax, rtol=1e-5, atol=0.0)
                np.testing.assert_allclose(betay, ref_betay, rtol=1e-4, atol=0.0)
                np.testing.assert_allclose(etax, ref_etax, rtol=1e-5, atol=0.0)

    print("** All new lattice files have been validated.")


def publicize_new_kickmap_files(new_official_kickmap_filenames, exist_ok=False):

    import shutil

    dst_folder = APHLA_SR_PYELE_MODELS_FOLDER / "kickmaps"

    for src_filename in new_official_kickmap_filenames:
        dst = dst_folder / src_filename
        if (not exist_ok) and dst.exists():
            print(f'The new kickmap file "{src_filename}" alreday exists. Not copying.')
            continue

        src = KM_OFFICIAL_LOCAL_FOLDER / src_filename
        shutil.copy(src, dst)
        print(f'The new kickmap file "{src_filename}" has been copied over to "{dst}"')


def publicize_new_model_LTE_files(exist_ok=False):

    # CRUCIAL to add `/` at the end. Otherwise, the absolute path to the kickmap file
    # will be invalid.
    public_km_folderpath_str = str(APHLA_SR_PYELE_MODELS_FOLDER / "kickmaps") + '/'

    public_LTE_root_folderpath = APHLA_SR_PYELE_MODELS_FOLDER / "LTEs"
    public_LTE_folderpath = public_LTE_root_folderpath / RELEASE_DATE_STR
    public_LTE_folderpath.mkdir(exist_ok=True)

    layout_filepaths = [lat.path for lat in LTE_files['layout'].values()]

    all_new_LTE_files = list(new_LTE_folder.glob("*.lte"))
    new_model_filepaths = [lat.path for lat in LTE_files['new_model']]
    assert all([fp not in layout_filepaths for fp in new_model_filepaths])
    new_quad_matched_LTE_files = [fp for fp in all_new_LTE_files
                                  if fp not in new_model_filepaths
                                  and fp not in layout_filepaths]
    print(f"# Total number of new model LTE files (non-quads-matched): {len(new_model_filepaths)}")
    for fp in new_model_filepaths:
        print(fp)
    print(f"# Total number of new quad-matched LTE files: {len(new_quad_matched_LTE_files)}")
    for fp in new_quad_matched_LTE_files:
        print(fp)

    for i_file, local_LTE_fp in enumerate(new_model_filepaths + new_quad_matched_LTE_files):
        public_LTE_filename = local_LTE_fp.name.replace("_RelKMPaths.lte", ".lte")

        new_fp = public_LTE_folderpath / public_LTE_filename
        if (not exist_ok) and new_fp.exists():
            print(f'#{i_file+1:02d}: LTE File "{new_fp}" already exists. Not overwriting.')
            continue

        contents = local_LTE_fp.read_text()
        contents = re.sub(
            KM_OFFICIAL_LOCAL_FOLDER_RE_PATTERN, public_km_folderpath_str, contents
        )

        new_fp.write_text(contents)
        print(f'#{i_file+1:02d}: LTE File "{new_fp}" has been written.')

        if False:
            _LTE = _get_LTE_from_bug_fixed_ltemanager_Lattice(new_fp, USED_BEAMLINE)

            pe.calc_ring_twiss(
                'test.pgz',
                str(new_fp),
                E_MeV=3e3,
                use_beamline=USED_BEAMLINE,
                alter_elements_list=ALTER_ELEMENTS_LIST
            )



def extract_sel_twis(output_pgz_filepath, elem_names=False, spos=False):
    d = pe.util.load_pgz_file(output_pgz_filepath)
    twi_scalars = d["data"]["twi"]["scalars"]
    twi_arrays = d["data"]["twi"]["arrays"]
    twis = dict(
        nux=twi_scalars["nux"],
        nuy=twi_scalars["nuy"],
        betax=twi_arrays["betax"],
        betay=twi_arrays["betay"],
        phix=twi_arrays["psix"] / (2 * np.pi),  # [2pi]
        phiy=twi_arrays["psiy"] / (2 * np.pi),  # [2pi]
        etax=twi_arrays["etax"],
    )

    if elem_names:
        twis["elem_names"] = twi_arrays["ElementName"]
    if spos:
        twis["spos"] = twi_arrays["s"]

    return twis

def calcTruncSVMatrix(sv, rcond=1e-6, nsv=None, disp=0):
    """
    Returns a truncated singluar value matrix for the given singular value
    vector "sv", which must be a 1-D vector.

    "rcond" will override "nsv", if both are specified. If both of them are
    `None`, all singular values will be kept.
    """

    norm_sv = sv / sv[0]

    n = len(sv)

    if disp >= 3:
        print("\n* Normalized Singular Values:")
        print(norm_sv)
        print(" ")

    if (disp >= 2) and np.any(sv == 0.0):
        print("### WARNING ### Zero singular values detected!")
        n_zero = np.where(sv == 0.0)[0].size
        n_nonzero = n - n_zero
        print(f"Number of non-zero singular values = {n_nonzero:d}")
        print(f"Number of     zero singular values = {n_zero:d}")
        print(" ")

    if rcond is not None:
        nsv = np.sum(norm_sv >= rcond)

        if (disp >= 2) and (np.min(norm_sv) < rcond):
            print(
                (
                    "# Info # Near-zero normalized singular values "
                    f"(<{rcond:.3e}) detected!"
                )
            )
            n_ok = np.sum(norm_sv >= rcond)
            n_notok = n - n_ok
            print(f"Number of above-threshold singular values = {n_ok:d}")
            print(f"Number of below-threshold singular values = {n_notok:d}")
            print(" ")

    if nsv is None:
        nsv = n

    S_inv_trunc = np.zeros((n, n))
    S_inv_trunc_square = np.diagflat(1.0 / sv[:nsv])
    S_inv_trunc[:nsv, :nsv] = S_inv_trunc_square

    if (disp >= 1) and (nsv != n):
        print(f"* Using only {nsv:d} out of {n:d} singular values.")

    return S_inv_trunc

def calc_twi_after_alter_elem(
    elem_name_prop_name_val, base_LTE, new_LTE_filepstr="", delete_temp_LTE_file=True
):
    pe.disable_stdout()

    mod_prop_dict_list = []

    elem_name, prop_name, prop_val = elem_name_prop_name_val

    mod_prop_dict_list.append(
        dict(
            elem_name=elem_name,
            prop_name=prop_name,
            prop_val=prop_val,
        )
    )

    if new_LTE_filepstr:
        pe.ltemanager.write_modified_LTE(
            new_LTE_filepstr, mod_prop_dict_list, LTE_obj=base_LTE
        )
        new_LTE_filepath = Path(new_LTE_filepstr)
        output_filepath = new_LTE_filepath.with_suffix(".pgz")

        pe.calc_ring_twiss(
            output_filepath.name,
            new_LTE_filepath.name,
            E_MeV=3e3,
            use_beamline=base_LTE.used_beamline_name,
            alter_elements_list=ALTER_ELEMENTS_LIST
        )

    else:
        temp_LTE_filepstr = pe.ltemanager.write_temp_modified_LTE(
            mod_prop_dict_list, LTE_obj=base_LTE
        )
        temp_LTE_filepath = Path(temp_LTE_filepstr)
        output_filepath = temp_LTE_filepath.with_suffix(".pgz")

        pe.calc_ring_twiss(
            output_filepath.name,
            temp_LTE_filepath.name,
            E_MeV=3e3,
            use_beamline=base_LTE.used_beamline_name,
            alter_elements_list=ALTER_ELEMENTS_LIST
        )

        if delete_temp_LTE_file:
            try:
                temp_LTE_filepath.unlink()
            except:
                pass

    twis = extract_sel_twis(output_filepath)

    if (not new_LTE_filepstr) and (not delete_temp_LTE_file):
        twis["temp_LTE_filepath"] = temp_LTE_filepath

    try:
        output_filepath.unlink()
    except:
        pass

    return twis


def calc_twi_after_alter_elems(
    mod_prop_dict_list, base_LTE, new_LTE_filepstr="", delete_temp_LTE_file=True
):
    pe.disable_stdout()

    if new_LTE_filepstr:
        pe.ltemanager.write_modified_LTE(
            new_LTE_filepstr, mod_prop_dict_list, LTE_obj=base_LTE
        )
        new_LTE_filepath = Path(new_LTE_filepstr)
        output_filepath = new_LTE_filepath.with_suffix(".pgz")

        pe.calc_ring_twiss(
            output_filepath.name,
            new_LTE_filepath.name,
            E_MeV=3e3,
            use_beamline=base_LTE.used_beamline_name,
            alter_elements_list=ALTER_ELEMENTS_LIST
        )

    else:
        temp_LTE_filepstr = pe.ltemanager.write_temp_modified_LTE(
            mod_prop_dict_list, LTE_obj=base_LTE
        )
        temp_LTE_filepath = Path(temp_LTE_filepstr)
        output_filepath = temp_LTE_filepath.with_suffix(".pgz")

        pe.calc_ring_twiss(
            output_filepath.name,
            temp_LTE_filepath.name,
            E_MeV=3e3,
            use_beamline=base_LTE.used_beamline_name,
            alter_elements_list=ALTER_ELEMENTS_LIST
        )

        if delete_temp_LTE_file:
            try:
                temp_LTE_filepath.unlink()
            except:
                pass

    twis = extract_sel_twis(output_filepath)

    if (not new_LTE_filepstr) and (not delete_temp_LTE_file):
        twis["temp_LTE_filepath"] = temp_LTE_filepath

    try:
        output_filepath.unlink()
    except:
        pass

    return twis


def calc_beta_phi_nu_respmat(input_LTE_filepath, input_twis, respmat_output_filepath):
    base_LTE = _get_LTE_from_bug_fixed_ltemanager_Lattice(
        input_LTE_filepath, USED_BEAMLINE
    )

    module_name = "correct_beta"
    func_name = "calc_twi_after_alter_elem"

    quad_elem_inds = base_LTE.get_elem_inds_from_regex(r"Q[HLM]\w+")
    assert len(quad_elem_inds) == 300
    quad_names = base_LTE.get_names_from_elem_inds(quad_elem_inds)

    sext_elem_inds = base_LTE.get_elem_inds_from_regex(r"S[HLM]\w+")
    assert len(sext_elem_inds) == 270
    sext_names = base_LTE.get_names_from_elem_inds(sext_elem_inds)

    bpm_elem_inds = base_LTE.get_elem_inds_from_regex(r"P[HLM]\w+")
    assert len(bpm_elem_inds) == 180
    bpm_names = base_LTE.get_names_from_elem_inds(bpm_elem_inds)

    if False:
        if False:
            base_output_filepath = input_LTE_filepath.with_suffix(".pgz")
            if not base_output_filepath.exists():
                pe.calc_ring_twiss(
                    base_output_filepath.name,
                    input_LTE_filepath.name,
                    E_MeV=3e3,
                    use_beamline="RING",
                    radiation_integrals=False,
                    alter_elements_list=ALTER_ELEMENTS_LIST
                )
            base_twis = extract_sel_twis(base_output_filepath, elem_names=True, spos=True)
            spos = base_twis['spos']
            cell_length = spos[-1] / 30
            for i in np.argsort(np.abs(spos - cell_length * 26)):
                name = base_LTE.get_names_from_elem_inds(i)
                if name.startswith('MK'):
                    np.testing.assert_almost_equal(spos[i], cell_length * 26, decimal=12)
                    c26_straight_center_ind = i
                    break
            if False:
                print(base_LTE.get_names_from_elem_inds(c26_straight_center_ind))
        else:
            c26_straight_center_ind = get_c26_straight_center_elem_index(base_LTE)


    all_elem_defs = base_LTE.get_used_beamline_element_defs(
        used_beamline_name=base_LTE.used_beamline_name
    )["elem_defs"]
    all_elem_names = [v[0] for v in all_elem_defs]
    param_list = []
    dK1 = 1e-4
    for name in quad_names:
        i = all_elem_names.index(name)
        prop_str = all_elem_defs[i][2]
        base_K1 = base_LTE.parse_elem_properties(prop_str).get("K1", 0.0)
        new_K1 = base_K1 + dK1
        param_list.append((name, "K1", new_K1))


    if False:
        args = (base_LTE,)

        err_log_check = dict(funcs=[pe.remote.check_remote_err_log_exit_code])

        remote_opts = dict(
            job_name="twi",
            ntasks=40,
            partition="debug",
            # partition="normal",
            qos="long",
            time="5:00",
        )

        raw_result, slurm_info = pe.remote.run_mpi_python(
            remote_opts,
            module_name,
            func_name,
            param_list,
            args,
            paths_to_prepend=[str(Path.cwd())],
            err_log_check=err_log_check,
            ret_slurm_info=True,
        )

        if "Traceback" in slurm_info.get("err_log", ""):
            print(slurm_info["err_log"])
            raise RuntimeError("### An error occurred during run_phys_eval() ###")
    else:
        raw_result = []
        for p in param_list:
            args = (pickle.loads(pickle.dumps(base_LTE)), ) # CRITICAL to
            # make and pass a copy into the function as `base_LTE` will be
            # modified in place, and thus, without using a copy, each change
            # for response calculation will be carried over to next.
            raw_result.append(calc_twi_after_alter_elem(p, *args))

    if raw_result == []:
        raise RuntimeError("Empty results")

    # sel_elem_inds = np.sort(np.hstack(
    #     [quad_elem_inds, sext_elem_inds, bpm_elem_inds, [c26_straight_center_ind]]))
    sel_elem_inds = np.sort(np.hstack(
        [quad_elem_inds, sext_elem_inds, bpm_elem_inds]))

    obs_names = input_twis["elem_names"][sel_elem_inds]
    obs_s = input_twis["spos"][sel_elem_inds]
    del input_twis["elem_names"]
    del input_twis["spos"]

    RM = {}
    RM["knob_names"] = quad_names
    RM["obs_names"] = obs_names
    RM["obs_s"] = obs_s
    for k in ["nux", "nuy"]:
        RM[k] = np.array([(d[k] - input_twis[k]) / dK1 for d in raw_result])
    assert 0 not in sel_elem_inds
    for k in ["betax", "betay", "etax"]:
        RM[k] = []
        for d in raw_result:
            v0 = input_twis[k]
            v0_avg = (v0[sel_elem_inds - 1] + v0[sel_elem_inds]) / 2
            v1 = d[k]
            v1_avg = (v1[sel_elem_inds - 1] + v1[sel_elem_inds]) / 2
            RM[k].append((v1_avg - v0_avg) / dK1)
        RM[k] = np.array(RM[k])
    for k in ["phix", "phiy"]:
        RM[f"d{k}"] = []
        assert len(quad_elem_inds) == len(raw_result)
        for ei, d in zip(quad_elem_inds, raw_result):
            v0 = input_twis[k]
            v0_avg = (v0[sel_elem_inds - 1] + v0[sel_elem_inds]) / 2
            v1 = d[k]
            v1_avg = (v1[sel_elem_inds - 1] + v1[sel_elem_inds]) / 2

            assert ei in sel_elem_inds
            i = np.where(sel_elem_inds == ei)[0][0]
            dphi0 = v0_avg - v0_avg[i]
            dphi1 = v1_avg - v1_avg[i]
            RM[f"d{k}"].append((dphi1 - dphi0) / dK1)
        RM[f"d{k}"] = np.array(RM[f"d{k}"])

    if False:
        plt.figure()
        plt.plot(RM["nux"], ".-")
        plt.plot(RM["nuy"], ".-")

        iQuad = 50

        plt.figure()
        plt.plot(RM["betax"][iQuad, :], "b.-")
        plt.plot(RM["betay"][iQuad, :], "r.-")

        plt.figure()
        plt.plot(RM["etax"][iQuad, :], "b.-")

        plt.figure()
        plt.plot(RM["dphix"][iQuad, :], "b.-")

        plt.figure()
        plt.plot(RM["dphiy"][iQuad, :], "b.-")


    with h5py.File(respmat_output_filepath, "w") as f:
        for k, v in RM.items():
            if k in ["knob_names", "obs_names"]:
                f[k] = RM[k].astype("S")
            else:
                f.create_dataset(k, data=v, compression="gzip")

    # plt.show()


def match_quads(ref_lat, lat_to_match, new_output_LTE_filepath: Path,
                target_nux: float=0.22, target_nuy: float=0.27):
    """
    Based on `restore_optics()` in
    /nsls2/data3/staff/yhidaka/git_repos/nsls2cb/20231103_optim_NEXT3/correct_beta.py
    """

    ref_LTE_filepath = ref_lat.path.resolve()

    twis_folder = Path("twis_for_matching")
    twis_folder.mkdir(exist_ok=True, parents=True)

    ref_output_filepath = twis_folder / ref_LTE_filepath.with_suffix(".pgz").name
    ref_output_filepath = ref_output_filepath.resolve()

    if not ref_output_filepath.exists():
        pe.calc_ring_twiss(
            str(ref_output_filepath),
            str(ref_LTE_filepath),
            E_MeV=3e3,
            use_beamline="RING",
            radiation_integrals=False,
            alter_elements_list=ALTER_ELEMENTS_LIST
        )

    ref_twis = extract_sel_twis(ref_output_filepath, elem_names=True, spos=True)

    ref_LTE = _get_LTE_from_bug_fixed_ltemanager_Lattice(
        ref_LTE_filepath, USED_BEAMLINE)

    quad_elem_inds = {}
    quad_elem_inds['ref'] = ref_LTE.get_elem_inds_from_regex(r"Q[HLM]\w+")
    assert len(quad_elem_inds['ref']) == 300
    quad_names = ref_LTE.get_names_from_elem_inds(quad_elem_inds['ref'])

    sext_elem_inds = {}
    sext_elem_inds['ref'] = ref_LTE.get_elem_inds_from_regex(r"S[HLM]\w+")
    assert len(sext_elem_inds['ref']) == 270
    sext_names = ref_LTE.get_names_from_elem_inds(sext_elem_inds['ref'])

    bpm_elem_inds = {}
    bpm_elem_inds['ref'] = ref_LTE.get_elem_inds_from_regex(r"P[HLM]\w+")
    assert len(bpm_elem_inds['ref']) == 180
    bpm_names = ref_LTE.get_names_from_elem_inds(bpm_elem_inds['ref'])

    ini_LTE_filepath = lat_to_match.path.resolve()

    ini_output_filepath = twis_folder / ini_LTE_filepath.with_suffix(".pgz").name
    ini_output_filepath = ini_output_filepath.resolve()

    if True or (not ini_output_filepath.exists()):
        pe.calc_ring_twiss(
            str(ini_output_filepath),
            str(ini_LTE_filepath),
            E_MeV=3e3,
            use_beamline="RING",
            radiation_integrals=False,
            alter_elements_list=ALTER_ELEMENTS_LIST
        )

    ini_twis = extract_sel_twis(ini_output_filepath, elem_names=True, spos=True)

    ini_LTE = _get_LTE_from_bug_fixed_ltemanager_Lattice(
        ini_LTE_filepath, USED_BEAMLINE)

    quad_elem_inds['ini'] = ini_LTE.get_elem_inds_from_regex(r"Q[HLM]\w+")
    assert len(quad_elem_inds['ref']) == len(quad_elem_inds['ini'])

    sext_elem_inds['ini'] = ini_LTE.get_elem_inds_from_regex(r"S[HLM]\w+")
    assert len(sext_elem_inds['ref']) == len(sext_elem_inds['ini'])

    bpm_elem_inds['ini'] = ini_LTE.get_elem_inds_from_regex(r"P[HLM]\w+")
    assert len(bpm_elem_inds['ref']) == len(bpm_elem_inds['ini'])

    QSP_elem_inds = {}
    for k in ['ref', 'ini']:
        QSP_elem_inds[k] = np.sort(
            np.hstack([quad_elem_inds[k], sext_elem_inds[k], bpm_elem_inds[k]]))

    if True:
        plt.figure()
        plt.plot(ref_twis["spos"], ref_twis["betax"], "b-")
        plt.plot(ini_twis["spos"], ini_twis["betax"], "r-")

        plt.figure()
        plt.plot(ref_twis["spos"][QSP_elem_inds['ref']],
                 ini_twis["etax"][QSP_elem_inds['ini']] -
                 ref_twis["etax"][QSP_elem_inds['ref']], "b-")

        plt.figure()
        plt.plot(np.diff(ref_twis["phix"][QSP_elem_inds['ref']]), "b.-")
        plt.plot(np.diff(ini_twis["phix"][QSP_elem_inds['ini']]), "r.-")

        plt.figure()
        plt.plot(np.diff(ref_twis["phiy"][QSP_elem_inds['ref']]), "b.-")
        plt.plot(np.diff(ini_twis["phiy"][QSP_elem_inds['ini']]), "r.-")

    obs_elem_inds = {}
    for k in ['ref', 'ini']:
        if True:
            obs_elem_inds[k] = sext_elem_inds[k][:]
        else:
            obs_elem_inds[k] = bpm_elem_inds[k][:]
    obs_elem_names = {}
    obs_elem_names['ref'] = ref_twis["elem_names"][obs_elem_inds['ref']]
    obs_elem_names['ini'] = ini_twis["elem_names"][obs_elem_inds['ini']]
    obs_prop_names = ["nux", "nuy", "betax", "betay", "etax"]

    # Override target nux/nuy
    ref_twis["nux"] = 33 + target_nux
    ref_twis["nuy"] = 16 + target_nuy

    delta = {}
    for k in obs_prop_names:
        if k in ("nux", "nuy"):
            delta[k] = ini_twis[k] - ref_twis[k]
        else:
            delta[k] = ini_twis[k][obs_elem_inds['ini']] - ref_twis[k][obs_elem_inds['ref']]

    respmat_folder = Path("respmats")
    respmat_folder.mkdir(exist_ok=True, parents=True)

    respmat_filepath = respmat_folder / f"{ini_LTE_filepath.stem}_respmat.h5"
    if not respmat_filepath.exists():
        calc_beta_phi_nu_respmat(
            ini_LTE_filepath,
            pickle.loads(pickle.dumps(ini_twis)), # Deep copy to avoid modifying original
            respmat_filepath)

    RM = {}
    with h5py.File(respmat_filepath, "r") as f:
        for k in list(f):
            RM[k] = f[k][()]
    RM_obs_names = RM["obs_names"].astype("U").tolist()
    RM_knob_names = RM["knob_names"].astype("U").tolist()

    index_map = [RM_obs_names.index(name) for name in obs_elem_names['ini']]

    # weight_case = 'A2'
    # weight_case = 'C'
    # weight_case = 'C2'
    weight_case = 'C3'
    # weight_case = 'E'
    if weight_case == 'A':
        weights = dict(nu=1e2, beta=1.0, eta=1.0)
    elif weight_case == 'A2':
        weights = dict(nu=1e2, beta=1.0, eta=1e3)
    elif weight_case == 'B':
        weights = dict(nu=1e3, beta=1.0, eta=1e2)
    elif weight_case == 'C':
        weights = dict(nu=1e3, beta=1.0, eta=5e2)
    elif weight_case == 'C2':
        weights = dict(nu=1e3, beta=1.0, eta=0.0)
    elif weight_case == 'C3':
        weights = dict(nu=5e2, beta=1.0, eta=5e2)
    elif weight_case == 'D':
        weights = dict(nu=1e3, beta=1.0, eta=1e3)
    elif weight_case == 'E':
        weights = dict(nu=0.0, beta=1.0, eta=0.0)
    else:
        raise NotImplementedError

    if weights['eta'] != 0.0:
        sel_knob_inds = list(range(len(RM_knob_names)))
    else:
        sel_knob_inds = [i for i, name in enumerate(RM_knob_names)
                         if not name.startswith("QM")]

    M_list = [RM["nux"] * weights["nu"], RM["nuy"] * weights["nu"]]
    M_list += [RM["betax"][:, i] * weights["beta"] for i in index_map]
    M_list += [RM["betay"][:, i] * weights["beta"] for i in index_map]
    M_list += [RM["etax"][:, i] * weights["eta"] for i in index_map]
    M = np.array(M_list)

    M = M[:, sel_knob_inds]
    sel_quad_names = [RM['knob_names'][i].astype(str) for i in sel_knob_inds]

    U, sv, Vt = np.linalg.svd(M, full_matrices=0, compute_uv=1)
    if True:
        plt.figure()
        plt.semilogy(sv / sv[0], ".-")

    rcond = 1e-5 # 1e-4
    Sinv_trunc = calcTruncSVMatrix(sv, rcond=rcond, nsv=None, disp=0)

    dobs = np.hstack(
        [
            delta["nux"] * weights["nu"],
            delta["nuy"] * weights["nu"],
            delta["betax"] * weights["beta"],
            delta["betay"] * weights["beta"],
            delta["etax"] * weights["eta"],
        ]
    )

    dI_list = []
    dobs_list = []

    cor_frac = 0.9

    dI = Vt.T @ Sinv_trunc @ U.T @ (-dobs)
    dI *= cor_frac
    dI_list.append(dI)
    dobs_list.append(dobs)
    if False:
        plt.figure()
        plt.plot(dI, "b.-")

    tmp = tempfile.NamedTemporaryFile(
        prefix=f"tmpLteMod_", suffix=".lte", dir=Path.cwd().resolve(), delete=False
    )
    new_LTE_filepstr = str(Path(tmp.name).resolve())
    tmp.close()

    cur_LTE = _get_LTE_from_bug_fixed_ltemanager_Lattice(
        ini_LTE_filepath, USED_BEAMLINE
    )

    nMaxIter = 20
    for iIter in range(nMaxIter):
        all_elem_defs = cur_LTE.get_used_beamline_element_defs(
            used_beamline_name=cur_LTE.used_beamline_name
        )["elem_defs"]
        all_elem_names = [v[0] for v in all_elem_defs]
        assert len(sel_quad_names) == len(dI)
        mod_prop_dict_list = []
        for elem_name, dK1 in zip(sel_quad_names, dI):
            i = all_elem_names.index(elem_name)
            prop_str = all_elem_defs[i][2]
            cur_K1 = cur_LTE.parse_elem_properties(prop_str).get("K1", 0.0)
            new_K1 = cur_K1 + dK1
            mod_prop_dict_list.append(
                dict(elem_name=elem_name, prop_name="K1", prop_val=new_K1)
            )
        new_twis = calc_twi_after_alter_elems(
            mod_prop_dict_list, cur_LTE, new_LTE_filepstr=new_LTE_filepstr
        )

        if False:
            if False:
                plt.figure()
                plt.plot(ref_twis["spos"], ref_twis["betax"], "b-")
                plt.plot(ini_twis["spos"], ini_twis["betax"], "r-")
                plt.plot(ini_twis["spos"], new_twis["betax"], "m-")

            sl_ini = obs_elem_inds['ini']
            sl_ref = obs_elem_inds['ref']

            plt.figure()
            # plt.plot(ini_twis["spos"], ini_twis["betax"] / ref_twis["betax"] - 1, "r-")
            # plt.plot(ini_twis["spos"], new_twis["betax"] / ref_twis["betax"] - 1, "b-")
            plt.plot(
                ini_twis["spos"][sl_ini],
                ini_twis["betax"][sl_ini] / ref_twis["betax"][sl_ref] - 1,
                "ro",
            )
            plt.plot(
                ini_twis["spos"][sl_ini],
                new_twis["betax"][sl_ini] / ref_twis["betax"][sl_ref] - 1,
                "bo",
            )

            plt.figure()
            # plt.plot(ini_twis["spos"], ini_twis["betay"] / ref_twis["betay"] - 1, "r-")
            # plt.plot(ini_twis["spos"], new_twis["betay"] / ref_twis["betay"] - 1, "b-")
            plt.plot(
                ini_twis["spos"][sl_ini],
                ini_twis["betay"][sl_ini] / ref_twis["betay"][sl_ref] - 1,
                "ro",
            )
            plt.plot(
                ini_twis["spos"][sl_ini],
                new_twis["betay"][sl_ini] / ref_twis["betay"][sl_ref] - 1,
                "bo",
            )

            plt.figure()
            plt.subplot(211)
            plt.plot(
                ref_twis["spos"][sl_ref], ref_twis["etax"][sl_ref], "bo-"
            )
            plt.plot(
                ini_twis["spos"][sl_ini], ini_twis["etax"][sl_ini], "ro-"
            )
            plt.subplot(212)
            plt.plot(
                ref_twis["spos"][sl_ref], ref_twis["etax"][sl_ref], "bo-"
            )
            plt.plot(
                ini_twis["spos"][sl_ini], new_twis["etax"][sl_ini], "ro-"
            )

            plt.figure()
            # plt.plot(ref_twis["spos"], ini_twis["etax"] - ref_twis["etax"], "r-")
            # plt.plot(ref_twis["spos"], new_twis["etax"] - ref_twis["etax"], "b-")
            plt.plot(
                ref_twis["spos"][sl_ref], ini_twis["etax"][sl_ini] - ref_twis["etax"][sl_ref], "ro"
            )
            plt.plot(
                ref_twis["spos"][sl_ref], new_twis["etax"][sl_ini] - ref_twis["etax"][sl_ref], "bo"
            )

            if False:
                plt.figure()
                plt.plot(np.diff(ref_twis["phix"][QSP_elem_inds['ref']]), "b.-")
                plt.plot(np.diff(ini_twis["phix"][QSP_elem_inds['ini']]), "r.-")

            plt.figure()
            plt.subplot(211)
            _ref_dphi = np.diff(ref_twis["phix"][QSP_elem_inds['ref']])
            plt.plot(np.diff(ini_twis["phix"][QSP_elem_inds['ini']]) - _ref_dphi, "r.-")
            plt.plot(np.diff(new_twis["phix"][QSP_elem_inds['ini']]) - _ref_dphi, "b.-")
            plt.subplot(212)
            _ref_dphi = np.diff(ref_twis["phix"][sl_ref])
            plt.plot(np.diff(ini_twis["phix"][sl_ini]) - _ref_dphi, "ro-")
            plt.plot(np.diff(new_twis["phix"][sl_ini]) - _ref_dphi, "bo-")

            plt.figure()
            plt.subplot(211)
            _ref_dphi = np.diff(ref_twis["phiy"][QSP_elem_inds['ref']])
            plt.plot(np.diff(ini_twis["phiy"][QSP_elem_inds['ini']]) - _ref_dphi, "r.-")
            plt.plot(np.diff(new_twis["phiy"][QSP_elem_inds['ini']]) - _ref_dphi, "b.-")
            plt.subplot(212)
            _ref_dphi = np.diff(ref_twis["phiy"][sl_ref])
            plt.plot(np.diff(ini_twis["phiy"][sl_ini]) - _ref_dphi, "ro-")
            plt.plot(np.diff(new_twis["phiy"][sl_ini]) - _ref_dphi, "bo-")

        delta = {}
        for k in obs_prop_names:
            if k in ("nux", "nuy"):
                delta[k] = new_twis[k] - ref_twis[k]
            else:
                delta[k] = new_twis[k][obs_elem_inds['ini']] - ref_twis[k][obs_elem_inds['ref']]

        dobs = np.hstack(
            [
                delta["nux"] * weights["nu"],
                delta["nuy"] * weights["nu"],
                delta["betax"] * weights["beta"],
                delta["betay"] * weights["beta"],
                delta["etax"] * weights["eta"],
            ]
        )

        dI = Vt.T @ Sinv_trunc @ U.T @ (-dobs)
        dI *= cor_frac
        dI_list.append(dI)
        dobs_list.append(dobs)
        if False:
            plt.figure()
            plt.plot(np.array(dI_list), ".-")

            plt.figure()
            plt.plot(np.array(dobs_list).T, '.-')

            plt.figure()
            plt.plot(dobs_list[0], 'r.-')
            plt.plot(dobs_list[1], 'b.-')

            plt.figure()
            i = 0
            plt.plot(dobs_list[i], 'b.-')
            plt.plot(- M @ dI_list[i], 'r.-')



        cur_LTE = _get_LTE_from_bug_fixed_ltemanager_Lattice(
            new_LTE_filepstr, USED_BEAMLINE
        )

        if np.all(np.abs(dI) < 1e-5):
            print(f"* Converged in {iIter+1:d} iterations.")
            break

    print(delta["nux"], delta["nuy"])

    if False:
        dI_list = np.array(dI_list).T

        plt.figure()
        plt.plot(dI_list)

        plt.figure()
        plt.plot(np.max(np.abs(dI_list), axis=0), ".-")

    if False:
        final_LTE_filepath = f'{datetime.now():%Y%m%d}_aphla_19ids_w_xbpms_MAG_19ids_YH_match_{ref}.lte'

        # For the lattice report generator meant for 15-period lattices, it needs a
        # fake super-cell definition, which is being added here.
        contents = cur_LTE.LTE_text
        use_ring_line = 'USE, "RING"'
        assert use_ring_line in contents

        with_supcell_def = f'''
    IDC02H1: DRIF,L=1.75
    L0008_MOD: LINE=(DFT,DH01G1C02A,PU1G1C02A,DH02G1C02A,CU1XG1C02ID1,CU1YG1C02ID1,&
    !EPU57G1C02CM,&
        IDC02H1,MK4G1C30A)
    SUPCELL: LINE=(L0001,L0002,L0003,L0004,L0005,L0006,L0007,L0008_MOD)

    {use_ring_line}'''

        Path(final_LTE_filepath).write_text(contents.replace(use_ring_line, with_supcell_def))

    new_output_LTE_filepath.write_text(cur_LTE.LTE_text)

    try:
        Path(new_LTE_filepstr).unlink()
    except:
        pass

    # plt.show()
    plt.close('all')


if __name__ == "__main__":

    # Used ~/.ap_pixi_manifests/yh-apv2-2026-01-pyele pixi env on 03/04/2026

    new_LTE_folder = Path("new_LTEs")
    new_LTE_folder.mkdir(exist_ok=True)

    RELEASE_DATE_STR = "20260304"

    USED_BEAMLINE = "RING"

    LTE_files = dict(layout={}, ids_quads_state={}, new_model=[])

    YAML_fps = {
        "ids_quads_states": f"{RELEASE_DATE_STR}_aphla_IDs_quads_states.yaml",
        "ids_states": f"{RELEASE_DATE_STR}_aphla_IDs_states.yaml",
    }

    # In this script, we're not adding any new ID.
    straight_cell_num = None

    # In this script, we're converting the existing following correctors into
    # correctors + skew quadrupoles:
    #   CH1[XY]G6C01B
    #   CH1[XY]G6C03B
    #   CH1[XY]G6C05B
    #   CH1[XY]G6C07B
    #   ...
    #   CH1[XY]G6C29B

    # As of 03/04/2026, the layout includes up to C09 CDI.
    # In this script, we will not add any new BPMs. So, next time you
    # update this script, this number should stay as 49.
    n_existing_ubpms = 49

    # As of 03/04/2026 the layout includes up to C09 CDI.
    #
    # ID Cell # (excluding the one(s) being added in this script):
    #  I(O)VU: 3, 4, 5, 7-1, 10, 11, 12, 16, 17-1, 17-2, 19, 20 (total 12)
    #  EPU: 2, 7-2, 21-1, 21-2, 23-1, 23-2 (total 6)
    #  SCW: 27 (total 1)
    #  DW: 8, 18, 28 (total 3)
    # Note:
    #   Non-DW 18th ID = HEX
    #   Non-DW 19th ID = IFE
    #   Non-DW 20th ID = CDI
    #
    # There are 3 damping wigglers (2 each) plus 20 non-DW IDs before new addition.
    # In this script, we will not add any new kickmap. So, next time you
    # update this script, `_n_ex_non_dw_ukickmaps` should stay as 20.
    _n_ex_dw_ukickmaps = 3 * 2
    _n_ex_non_dw_ukickmaps = 20
    n_existing_ukickmaps = _n_ex_dw_ukickmaps + _n_ex_non_dw_ukickmaps


    # Run the following functions one by one in this order while adjusting the
    # script.
    funcs_to_run = {
        "gen_new_layout_LTE_file": False, #True,
        "gen_ids_quads_states_yaml": False, #True,
        "gen_insertion_device_states_yaml": False, #True,
        "gen_new_model_LTE_files": False, #True,
        "validate_new_LTE_files": False, #True,
        "match_quads": False, #True,
        "publicize_new_kickmap_files": False, #True,
        "publicize_new_model_LTE_files": True,
    }

    # The following LTE file should be the latest layout file (without "_w_xbpms")
    # at the time of updating/running this script.
    # As of 03/04/2026, it was "../20250905/new_LTEs/20250905_aphla_layout_RelKMPaths.lte",
    # which was copied into "20260304/manual_layout_LTE_mods". Based on this file,
    # I manually modified the layout and saved it as
    #     "20260304/manual_layout_LTE_mods/20260304_aphla_layout_manually_mod_RelKMPaths.lte"
    # And I set that as the original layout (though already new), and
    # a later call to gen_new_layout_LTE_file_with_new_SQs() will simply copy this into
    # the new LTE folder with the new file name.
    LTE_files['layout']['orig'] = LayoutLatticeFile(
        path=Path("manual_layout_LTE_mods/20260304_aphla_layout_manually_mod_RelKMPaths.lte"),
        with_xbpms=False,
    )

    # No need to change the following lines when updating this script.
    LTE_files['layout']['new'] = LayoutLatticeFile(
        path=new_LTE_folder / f"{RELEASE_DATE_STR}_aphla_layout_RelKMPaths.lte",
        with_xbpms=False,
    )
    LTE_files['layout']['new_w_xbpms'] = LayoutLatticeFile(
        path=new_LTE_folder / f"{RELEASE_DATE_STR}_aphla_layout_w_xbpms_RelKMPaths.lte",
        with_xbpms=True,
    )

    if funcs_to_run["gen_new_layout_LTE_file"]:
        if False:
            # Interactively adjust this function for newly added ID(s)
            gen_new_layout_LTE_file(
                straight_cell_num, n_existing_ubpms, n_existing_ukickmaps)
        gen_new_layout_LTE_file_with_new_SQs(n_existing_ubpms, n_existing_ukickmaps)

    # Must specify which LTE should be used for each "quads_state" to extract
    # quad strengths.
    for ids_state, quads_state, path in [
        ("bare", "day1", "../nsls2sr_bare_20141015.lte"),
        ("3dw", "day1", "../nsls2sr_dw_20141119.lte"),
        ("3dw", "nuy27", "../20170905_3DWs_Matched_XBPMs_nu_22_27.lte"),
    ]:
        f = IDsQuadsStateLatticeFile(
            path=Path(path),
            ids_state=ids_state,
            quads_state=quads_state
        )
        LTE_files['ids_quads_state'][get_ids_quads_state_LTE_key(f)] = f

    # Quad settings matched by Victor Smaluk with 17 non-DW IDs included:
    VS_17ids_matched_fp = "../20190125_VS_nsls2sr17idsmt_SQLC16_RelKMPaths_UpOneFolder.lte"
    for ids_state, quads_state in [
        ("20ids_wo_IFE_HEX", "17ids_matched_VS"),
        ("20ids_wo_HEX", "17ids_matched_VS"),
    ]:
        f = IDsQuadsStateLatticeFile(
            path=Path(VS_17ids_matched_fp),
            ids_state=ids_state,
            quads_state=quads_state
        )
        LTE_files['ids_quads_state'][get_ids_quads_state_LTE_key(f)] = f

    # Quad settings matched by Yongjun Li with 18 non-DW IDs (i.e., up to HEX) included:
    YL_18ids_matched_fp = "../nsls2_18ID_RepV1o4.lte"
    for ids_state, quads_state in [
        ("20ids_wo_IFE", "18ids_matched_YL"),
        ("20ids", "18ids_matched_YL"),
    ]:
        f = IDsQuadsStateLatticeFile(
            path=Path(YL_18ids_matched_fp),
            ids_state=ids_state,
            quads_state=quads_state
        )
        LTE_files['ids_quads_state'][get_ids_quads_state_LTE_key(f)] = f

    if funcs_to_run["gen_ids_quads_states_yaml"]:
        gen_ids_quads_states_yaml()

    # `model_name` format: "ids_state:quads_state"
    #
    # "ids_state=20ids" means 20 non-DW IDs (up to C09 CDI) are closed.
    # "_wo_HEX" means C27 HEX is open (i.e., turned off).
    # "_wo_IFE" means C20 IFE is open.
    # "_wo_IFE_HEX" means both C20 IFE and C27 HEX are open.
    #
    # "quads_state": "nuy27" means tunes adjusted to (0.22, 0.27),
    # instead of Day-1 tunes of (0.22, 0.26).
    # model_name_list = [
    #     "bare:day1",
    #     "3dw:day1",
    #     "3dw:nuy27",
    #     "20ids_wo_IFE_HEX:17ids_matched_VS",
    #     "20ids_wo_HEX:17ids_matched_VS",
    #     "20ids_wo_IFE:18ids_matched_YL",
    #     "20ids:18ids_matched_YL",
    # ]
    model_name_list = list(LTE_files['ids_quads_state'])

    for with_xbpms in (False, True):
        for model_name in model_name_list:
            ids_state, quads_state = model_name.split(":")
            model_file_name_str = (
                f"{ids_state}_w_xbpms_Q_{quads_state}" if with_xbpms
                else f"{ids_state}_Q_{quads_state}")
            new_LTE_filename = f"{RELEASE_DATE_STR}_aphla_{model_file_name_str}_RelKMPaths.lte"
            LTE_files['new_model'].append( NewModelLatticeFile(
                path=new_LTE_folder / new_LTE_filename,
                with_xbpms=with_xbpms,
                ids_state=ids_state,
                quads_state=quads_state
            ))

    if funcs_to_run["gen_insertion_device_states_yaml"]:
        # This funtion also needs to be updated every time when this script is updated.
        gen_insertion_device_states_yaml()
    if funcs_to_run["gen_new_model_LTE_files"]:
        gen_new_model_LTE_files()
    if funcs_to_run["validate_new_LTE_files"]:
        # new_ubpm_names = ["PU1G1C09A", "PU4G1C09A"]
        # new_kickmap_elem_names = ["IVU18G1C09CM"]
        new_ubpm_names = []
        new_kickmap_elem_names = []

        load_from_proc = False
        # load_from_proc = True

        # This funtion also needs to be updated every time when this script is updated.
        validate_new_LTE_files(load_from_proc, straight_cell_num, n_existing_ubpms, n_existing_ukickmaps,
                               new_ubpm_names, new_kickmap_elem_names)

    if funcs_to_run["match_quads"]:
        # ref_lat = LTE_files['ids_quads_state']['bare:day1']
        ref_lat = LTE_files['ids_quads_state']['3dw:day1']

        for lat_to_match in LTE_files['new_model']:

            if lat_to_match.ids_state not in ("bare", "3dw"):

                stem = lat_to_match.path.stem
                prefix = stem.split('Q_')[0]
                new_file_name = f"{prefix}Q_matched_YH_3dw_nuy27_RelKMPaths.lte"

                new_output_LTE_filepath = lat_to_match.path.parent / new_file_name

                match_quads(ref_lat, lat_to_match, new_output_LTE_filepath)


    if funcs_to_run["publicize_new_kickmap_files"]:
        # new_official_kickmap_filenames = ['U18kickmap_2o4m_T2m2_woKm2sdds.sdds',
        #                                   'U18kickmap_1o2m_T2m2_woKm2sdds.sdds']
        new_official_kickmap_filenames = []
        if new_official_kickmap_filenames != []:
            publicize_new_kickmap_files(new_official_kickmap_filenames, exist_ok=False)
    if funcs_to_run["publicize_new_model_LTE_files"]:
        publicize_new_model_LTE_files(exist_ok=False)
