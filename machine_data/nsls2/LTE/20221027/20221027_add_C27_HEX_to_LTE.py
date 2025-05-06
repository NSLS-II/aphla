from pathlib import Path
import re
import json
import gzip
import pickle

import numpy as np
from ruamel import yaml
import pyelegant as pe

import aphla as ap

ap.machines.load("nsls2", "SR")
ap.setOpModeStr("simulation")


def get_yaml_flow_style_list(L):

    L = yaml.comments.CommentedSeq(L)
    L.fa.set_flow_style()

    return L


def conv_yaml_dict_to_plain_dict(yaml_dict):

    return json.loads(json.dumps(yaml_dict))


def basic_lattice_integrity_check(LTE):

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
    assert len(ordered_skquad_names) == 30 + 1  # "+1" for C16SQL

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
    assert len(ordered_ubpm_names) == 43  # as of 02/03/2021

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
    assert len(ordered_ukickmap_names) == 17 + 2 * 3

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

    # Get upstream & downstream sextupole names that are bounding C27 straight
    us_sext_name = [
        v
        for v in all_variable_elem_names_ordered
        if ("C26" in v) and v.startswith(("SH", "SL")) and v.endswith(("A", "B"))
    ][-1]
    ds_sext_name = [
        v
        for v in all_variable_elem_names_ordered
        if ("C27" in v) and v.startswith(("SH", "SL")) and v.endswith(("A", "B"))
    ][0]

    iStart = flat_used_elem_names.index(us_sext_name)
    iEnd = flat_used_elem_names.index(ds_sext_name) + 1

    max_name_len = max([len(name) for name in flat_used_elem_names[iStart:iEnd]])

    is_cell_even = False

    header = f'{"Name":{max_name_len}s}' + " | Orig.L [m] |   se [m]   "
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

        print(f"{name:{max_name_len}s} | {L:10.6f} | {s:10.6f}")

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

    target_se = {  # [m]; s-pos of element end relative to straight beginning (se=0)
        "MK5G1C27A": straight_center_spos,
    }
    target_sb = (
        {}  # [m]; s-pos of element beginning relative to straight beginning (se=0)
    )
    new_Ls = {
        "IDC27H2": 1.19,  # [m]; from the length of the kickmap
    }
    target_dse = {  # [m]; s-pos of element end relative to straight center (dse=0)
        "PU1G1C27A": -2.3177,
        "PU4G1C27A": +2.1519,
    }
    target_dsc = {  # [m]; s-pos of element center relative to straight center (dsc=0)
        "IDC27H2": +1.0,
    }

    target_se["PU1G1C27A"] = straight_center_spos + target_dse["PU1G1C27A"]
    target_se["IDC27H2"] = (
        straight_center_spos + target_dsc["IDC27H2"] + new_Ls["IDC27H2"] / 2
    )
    target_sb["IDC27H2"] = target_se["IDC27H2"] - new_Ls["IDC27H2"]
    target_se["PU3G1C27A"] = target_sb["IDC27H2"]
    target_se["PU4G1C27A"] = straight_center_spos + target_dse["PU4G1C27A"]
    target_se["GSG2C27A"] = straight_end_spos

    # key: element whose L will be adjusted
    # value: element whose "se" will be adjusted to the target "se" after L adjustment
    target_names = {
        "DL01G1C27A": "PU1G1C27A",
        "DL04G1C27A": "MK5G1C27A",
        "DL05G1C27A": "PU3G1C27A",
        "IDC27H2": "IDC27H2",
        "DL07G1C27A": "PU4G1C27A",
        "DL08G1C27A": "GSG2C27A",
    }
    for name_for_L_adj, name_for_target_se in target_names.items():
        new_Ls[name_for_L_adj] = 0.0  # orig_L[name_for_L_adj] + (
        # target_se[name_for_target_se] - orig_se[name_for_target_se])

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


def extract_magnet_properties_from_LTE(
    LTE_filepath, used_beamline_name, elem_name_patterns, prop_names, n_expected_matches
):

    LTE = pe.ltemanager.Lattice(
        LTE_filepath=LTE_filepath, used_beamline_name=used_beamline_name
    )

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


def gen_new_layout_LTE_file():

    if False:
        # aphla_config_folderp = Path('/epics/aphla/apconf/nsls2')
        aphla_config_folderp = Path(ap.machines.HLA_CONFIG_DIR).joinpath("nsls2")

        orig_LTE_layout_filepath = str(
            aphla_config_folderp.joinpath(
                "models",
                "SR",
                "pyelegant",
                "LTEs",
                "20190125_VS_nsls2sr17idsmt_SQLC16.lte",
            )
        )
    else:
        orig_LTE_layout_filepath = LTE_fps["orig_layout"]

    for layout_type in ["new_layout", "new_layout_w_xbpms"]:

        base_LTE = pe.ltemanager.Lattice(
            LTE_filepath=orig_LTE_layout_filepath, used_beamline_name=USED_BEAMLINE
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
        ) = basic_lattice_integrity_check(base_LTE)

        # Interactively adjust this section to generate a desirable table
        #
        # *) Adding HEX ID Kickmap element
        # *) Adding ID BPMs P7 & P8 for C27 HEX SCW
        #
        # Additionaly only for "new_layout_w_xbpms":
        # *) Splitting kickmap elements at C03, C16, and C17 into half and inserted
        #    X-BPMs at the middle
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

        old_id_name = "IDC27H2"
        new_id_name = "SCW70G1C27D"
        elem_name_changes = {
            old_id_name: dict(name=new_id_name, update_in_beamline_def=True)
        }
        elem_type_changes = {
            new_id_name: "UKICKMAP",  # from drift
            "PU1G1C27A": "MONI",  # from drift
            "PU4G1C27A": "MONI",  # from drift
        }
        nkicks = int(np.ceil(1.19 / 70e-3))
        other_new_props = [
            dict(
                elem_name=new_id_name,
                prop_name="INPUT_FILE",
                prop_val='"./kickmaps/official/SCW_HEX70_4_3_T_1_2m_1o19m_T2m2_woKm2sdds.sdds"',
            ),
            dict(elem_name=new_id_name, prop_name="N_KICKS", prop_val=f"{nkicks}"),
            dict(elem_name=new_id_name, prop_name="PERIODS", prop_val=f"{nkicks}"),
            dict(elem_name=new_id_name, prop_name="KREF", prop_val="28.1"),
        ]

        new_elem_defs = []
        new_beamline_defs = []

        if layout_type == "new_layout_w_xbpms":

            old_id_name = "IVU20G1C03CM"
            new_id_name = old_id_name + "_HALF"
            elem_name_changes[old_id_name] = dict(
                name=new_id_name, update_in_beamline_def=False
            )
            for prop_name, prop_val in [
                ("L", "1.5"),
                (
                    "INPUT_FILE",
                    '"./kickmaps/official/U20_asbuilt_g52_1o5m_T2m2_woKm2sdds.sdds"',
                ),
                ("N_KICKS", "75"),
                ("PERIODS", "75"),
            ]:
                other_new_props.append(
                    dict(elem_name=new_id_name, prop_name=prop_name, prop_val=prop_val)
                )

            old_id_name = "IVU23G1C16CM"
            new_id_name = old_id_name + "_HALF"
            elem_name_changes[old_id_name] = dict(
                name=new_id_name, update_in_beamline_def=False
            )
            for prop_name, prop_val in [
                ("L", "1.4"),
                (
                    "INPUT_FILE",
                    '"./kickmaps/official/U23L_asbuilt_g57_1o4m_T2m2_woKm2sdds.sdds"',
                ),
                ("N_KICKS", "61"),
                ("PERIODS", "61"),
            ]:
                other_new_props.append(
                    dict(elem_name=new_id_name, prop_name=prop_name, prop_val=prop_val)
                )

            for old_id_name in ["IVU21G1C17UM", "IVU21G1C17DM"]:
                new_id_name = old_id_name + "_HALF"
                elem_name_changes[old_id_name] = dict(
                    name=new_id_name, update_in_beamline_def=False
                )
                for prop_name, prop_val in [
                    ("L", "0.75"),
                    (
                        "INPUT_FILE",
                        '"./kickmaps/official/U21_asbuilt_g64_0o75m_T2m2_woKm2sdds.sdds"',
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

            for insertIndex, (old_id_name, xbpm_name) in enumerate(
                [
                    ("IVU20G1C03CM", "PX1G1C03A"),
                    ("IVU23G1C16CM", "PX1G1C16A"),
                    ("IVU21G1C17UM", "PX1G1C17A"),
                    ("IVU21G1C17DM", "PX2G1C17A"),
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

        new_LTE_layout_filepath = LTE_fps[layout_type]

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

    print("Finished.")


def gen_magnet_props_yaml():

    mag_props = {}

    (elem_name_patterns, prop_names, n_expected_matches) = list(
        zip(*[("Q[HLM]\w+", "K1", 300)])
    )

    model_names = np.unique(
        [name for name in list(LTE_fps) if name.startswith("orig_model:")]
    )
    for lat_name in model_names:
        _, _, magnet_state = lat_name.split(":")

        LTE_filepath = LTE_fps[f"mag_props:{magnet_state}"]

        mag_props[magnet_state] = extract_magnet_properties_from_LTE(
            LTE_filepath,
            USED_BEAMLINE,
            elem_name_patterns,
            prop_names,
            n_expected_matches,
        )

    if False:
        with open("magnet_props.json", "w") as f:
            # json.dump(mag_props, f)
            json.dump(mag_props, f, indent=2)

    y = yaml.YAML()
    y.width = 110
    y.boolean_representation = ["False", "True"]
    y.indent(
        mapping=2, sequence=2, offset=0
    )  # Default: (mapping=2, sequence=2, offset=0)

    yaml_filepath = YAML_fps["mag_props"]

    with open(yaml_filepath, "w") as f:
        y.dump(mag_props, f)

    print("Finished")


def gen_insertion_device_states_yaml():

    layout_LTE_filepath = LTE_fps["new_layout"]

    states = {}

    for layout_type in ["new_layout", "new_layout_w_xbpms"]:

        layout_LTE_filepath = LTE_fps[layout_type]

        LTE = pe.ltemanager.Lattice(
            LTE_filepath=layout_LTE_filepath, used_beamline_name=USED_BEAMLINE
        )

        LTE_d = LTE.get_used_beamline_element_defs(used_beamline_name=USED_BEAMLINE)
        elem_defs = LTE_d["elem_defs"]
        elem_names = [v[0] for v in elem_defs]

        km_elem_names = list(LTE.get_kickmap_filepaths()["abs"])
        km_elem_names = sorted(km_elem_names)

        if layout_type == "new_layout":
            state_name = "bare"
        elif layout_type == "new_layout_w_xbpms":
            state_name = "bare_w_xbpms"
        else:
            raise ValueError
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

        if layout_type == "new_layout":
            state_name = "3dw"
        elif layout_type == "new_layout_w_xbpms":
            state_name = "3dw_w_xbpms"
        else:
            raise ValueError
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

        if layout_type == "new_layout":
            state_name = "18ids"
        elif layout_type == "new_layout_w_xbpms":
            state_name = "18ids_w_xbpms"
        else:
            raise ValueError
        states[state_name] = dict(elem_type_changes={}, elem_prop_changes=[])

    y = yaml.YAML()
    y.width = 110
    y.boolean_representation = ["False", "True"]
    y.indent(
        mapping=2, sequence=2, offset=0
    )  # Default: (mapping=2, sequence=2, offset=0)

    yaml_filepath = YAML_fps["id_states"]

    with open(yaml_filepath, "w") as f:
        y.dump(states, f)

    print("Finished")


def gen_new_model_LTE_files():

    y = yaml.YAML()
    mag_props = conv_yaml_dict_to_plain_dict(
        y.load(Path(YAML_fps["mag_props"]).read_text())
    )
    id_states = conv_yaml_dict_to_plain_dict(
        y.load(Path(YAML_fps["id_states"]).read_text())
    )

    all_new_model_lat_names = [
        name for name in list(LTE_fps) if name.startswith("new_model:")
    ]
    new_model_lat_names = {"new_layout": [], "new_layout_w_xbpms": []}
    for lat_name in all_new_model_lat_names:
        _, id_state, magnet_state = lat_name.split(":")
        assert id_state in id_states
        assert magnet_state in mag_props
        if id_state.endswith("_w_xbpms"):
            new_model_lat_names["new_layout_w_xbpms"].append(lat_name)
        else:
            new_model_lat_names["new_layout"].append(lat_name)

    for layout_type in ["new_layout", "new_layout_w_xbpms"]:

        layout_LTE_filepath = LTE_fps[layout_type]

        for lat_name in new_model_lat_names[layout_type]:
            _, id_state, magnet_state = lat_name.split(":")
            new_LTE_filepath = LTE_fps[lat_name]

            base_LTE = pe.ltemanager.Lattice(
                LTE_filepath=layout_LTE_filepath, used_beamline_name=USED_BEAMLINE
            )

            mod_LTE_d = base_LTE.get_persistent_used_beamline_element_defs(
                used_beamline_name=USED_BEAMLINE
            )

            # Change element types, if necessary
            elem_type_changes = id_states[id_state]["elem_type_changes"]
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
                for elem_name, prop_name, prop_val in mag_props[magnet_state]
            ]
            for elem_name, prop_name, prop_val_str in id_states[id_state][
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


def validate_new_LTE_files(load_from_proc):

    twi_filepath = f"{RELEASE_DATE_STR}_aphla_twiss.pgz"
    if not load_from_proc:
        output_filepath = "test.pgz"
        E_MeV = 3e3
        twi = {}
        for k in list(LTE_fps):
            if k.startswith("mag_props:"):
                continue
            pe.calc_ring_twiss(
                output_filepath, LTE_fps[k], E_MeV, use_beamline=USED_BEAMLINE
            )
            twi[k] = pe.util.load_pgz_file(output_filepath)["data"]["twi"]

        with gzip.GzipFile(twi_filepath, "wb") as f:
            pickle.dump(twi, f)

    with gzip.GzipFile(twi_filepath, "rb") as f:
        twi = pickle.load(f)

    split_km_elem_names = [
        "IVU20G1C03CM",
        "IVU23G1C16CM",
        "IVU21G1C17UM",
        "IVU21G1C17DM",
    ]

    d = twi["orig_layout"]
    ar = d["arrays"]
    quad_names = [
        name
        for name in ar["ElementName"]
        if re.match("^Q[HLM]\dG\w+", name) is not None
    ]
    assert len(quad_names) == 300
    skquad_names = [
        name for name in ar["ElementName"] if re.match("^SQ[HM]G\w+", name) is not None
    ]
    assert len(skquad_names) == 30 * 2  # "*2" for half-splitting
    skquad_names_C16SQL = [
        name for name in ar["ElementName"] if re.match("^SQLG\w+", name) is not None
    ]
    assert len(skquad_names_C16SQL) == 1 * 2  # "1" for C16SQL; "*2" for half-splitting
    sext_names = [
        name
        for name in ar["ElementName"]
        if re.match("^S[HLM]\dG\w+", name) is not None
    ]
    assert len(sext_names) == 270
    bend_names = [
        name for name in ar["ElementName"] if re.match("^B[12]G\w+", name) is not None
    ]
    assert len(bend_names) == 30 * 2
    scor_names = [
        name
        for name in ar["ElementName"]
        if re.match("^C[HLM]\dYG\w+", name) is not None
    ]
    assert len(scor_names) == 180
    fcor_names = [
        name
        for name in ar["ElementName"]
        if re.match("^F[HLM]\dG\w+", name) is not None
    ]
    assert len(fcor_names) == 90
    rbpm_names = [
        name
        for name in ar["ElementName"]
        if re.match("^P[HLM][1-3]\w+", name) is not None
    ]
    assert len(rbpm_names) == 180
    orig_ubpm_names = [
        elem_name
        for elem_name, elem_type in zip(ar["ElementName"], ar["ElementType"])
        if (re.match("^PU[1-4]\w+", elem_name) is not None) and (elem_type == "MONI")
    ]
    orig_n_ubpms = 43
    assert len(orig_ubpm_names) == orig_n_ubpms
    orig_ukickmap_names = [
        elem_name
        for elem_name, elem_type in zip(ar["ElementName"], ar["ElementType"])
        if elem_type == "UKICKMAP"
    ]
    orig_n_ukickmaps = 17 + 2 * 3  # (2 * 3) for 3 DWs with 2 each
    assert len(orig_ukickmap_names) == orig_n_ukickmaps

    # --- Check circumference ---
    circumf = 791.958
    for lat_name, d in twi.items():
        ar = d["arrays"]
        np.testing.assert_almost_equal(ar["s"][-1], circumf, decimal=16)

    # --- Check end s-pos has not moved for all existing major elements ---
    ref_ar = twi["orig_layout"]["arrays"]
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
        for lat_name, d in twi.items():
            if lat_name == "orig_model:3dw:3dw_nu_22_27":
                continue  # This lattice file's skew quads are not split in half. So, not comparable.
            ar = d["arrays"]
            elem_names = ar["ElementName"].tolist()
            spos = np.array(
                [ar["s"][elem_names.index(name)] for name in sel_elem_names]
            )
            np.testing.assert_almost_equal(spos, ref_spos, decimal=16)
    # Then check newer elements, but must exclude the old lattices during this check
    for sel_elem_names in [skquad_names_C16SQL, orig_ubpm_names, orig_ukickmap_names]:
        ref_spos = np.array(
            [ref_ar["s"][ref_elem_names.index(name)] for name in sel_elem_names]
        )
        for lat_name, d in twi.items():
            if lat_name.startswith(("orig_model:bare:", "orig_model:3dw:")):
                continue  # These selected elements didn't exist in these old lattice files.
            else:
                ar = d["arrays"]
                elem_names = ar["ElementName"].tolist()
                try:
                    spos = np.array(
                        [ar["s"][elem_names.index(name)] for name in sel_elem_names]
                    )
                except ValueError:
                    assert ("_w_xbpms" in lat_name) or ("_w_xbpms:" in lat_name)
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
                np.testing.assert_almost_equal(spos, ref_spos, decimal=16)

    # --- Check differences between "orig_layout" and "new_model" LTE files are
    # only the newly added elements ---
    new_n_ubpms = orig_n_ubpms + 2
    new_n_ukickmaps = {
        "bare": 0,
        "bare_w_xbpms": 0,
        "3dw": 2 * 3,  # 2 kickmap elemes at C08, C18, C28
        "3dw_w_xbpms": 2 * 3,  # 2 kickmap elemes at C08, C18, C28
        "18ids": orig_n_ukickmaps + 1,  # "+1" for C27 HEX
        "18ids_w_xbpms": orig_n_ukickmaps + 1 + 4
        # ^ "+1" for C27 HEX; 4 kickmaps split into half at C03, C16, C17-1, C17-2
    }
    for lat_name, d in twi.items():
        if not lat_name.startswith("new_model:"):
            continue

        ar = d["arrays"]

        new_ubpm_names = [
            elem_name
            for elem_name, elem_type in zip(ar["ElementName"], ar["ElementType"])
            if (re.match("^PU[1-4]\w+", elem_name) is not None)
            and (elem_type == "MONI")
        ]
        assert len(new_ubpm_names) == new_n_ubpms
        assert all([(name in new_ubpm_names) for name in orig_ubpm_names])
        assert np.all(
            np.sort([name for name in new_ubpm_names if name not in orig_ubpm_names])
            == np.sort(["PU1G1C27A", "PU4G1C27A"])
        )

        _, id_state_name, _ = lat_name.split(":")

        new_ukickmap_names = [
            elem_name
            for elem_name, elem_type in zip(ar["ElementName"], ar["ElementType"])
            if elem_type == "UKICKMAP"
        ]

        assert len(new_ukickmap_names) == new_n_ukickmaps[id_state_name]

        if id_state_name in ("bare", "bare_w_xbpms"):
            continue  # Kickmap elements in bare lattice have been converted to drifts.
        elif id_state_name in ("3dw", "3dw_w_xbpms"):
            assert all([name.startswith("DW100G1C") for name in new_ukickmap_names])
            continue  # Kickmap elements except for DWs have been converted to drifts.

        assert all(
            [
                (name in new_ukickmap_names) or (f"{name}_HALF" in new_ukickmap_names)
                for name in orig_ukickmap_names
            ]
        )
        assert np.all(
            np.sort(
                [
                    name
                    for name in new_ukickmap_names
                    if (name not in orig_ukickmap_names)
                    and not (
                        name.endswith("_HALF")
                        and name[: -len("_HALF")] in split_km_elem_names
                    )
                ]
            )
            == np.sort(["SCW70G1C27D"])
        )

    # --- Check lengths & s-pos of newly added elements ---
    C27_straight_center_spos = 27 * (circumf / 30)
    expected_Ls = {"SCW70G1C27D": 1.19}
    expected_spos = {
        "SCW70G1C27D": C27_straight_center_spos + 1.0 + expected_Ls["SCW70G1C27D"] / 2,
        "PU1G1C27A": C27_straight_center_spos - 2.3177,
        "PU4G1C27A": C27_straight_center_spos + 2.1519,
    }
    for lat_name in [
        "new_layout",
        "new_model:bare:bare",
        "new_model:3dw:3dw",
        "new_model:3dw:3dw_nu_22_27",
        "new_model:18ids:17ids",
    ]:
        d = twi[lat_name]
        ar = d["arrays"]
        elem_names = ar["ElementName"].tolist()

        for name, desired in expected_Ls.items():
            i = elem_names.index(name)
            L = ar["s"][i] - ar["s"][i - 1]
            np.testing.assert_almost_equal(L, desired, decimal=12)

        for name, desired in expected_spos.items():
            i = elem_names.index(name)
            np.testing.assert_almost_equal(ar["s"][i], desired, decimal=12)
    expected_Ls["IVU20G1C03CM_HALF"] = 1.5
    expected_Ls["IVU23G1C16CM_HALF"] = 1.4
    expected_Ls["IVU21G1C17UM_HALF"] = 0.75
    expected_Ls["IVU21G1C17DM_HALF"] = 0.75
    expected_spos["PX1G1C03A"] = 79.1958
    expected_spos["PX1G1C16A"] = 422.378
    expected_spos["PX1G1C17A"] = 447.455
    expected_spos["PX2G1C17A"] = 450.082
    for lat_name in [
        "new_layout_w_xbpms",
        "new_model:bare_w_xbpms:bare",
        "new_model:3dw_w_xbpms:3dw",
        "new_model:3dw_w_xbpms:3dw_nu_22_27",
        "new_model:18ids_w_xbpms:17ids",
    ]:
        d = twi[lat_name]
        ar = d["arrays"]
        elem_names = ar["ElementName"].tolist()

        for name, desired in expected_Ls.items():
            i = elem_names.index(name)
            L = ar["s"][i] - ar["s"][i - 1]
            np.testing.assert_almost_equal(L, desired, decimal=12)

        for name, desired in expected_spos.items():
            i = elem_names.index(name)
            np.testing.assert_almost_equal(ar["s"][i], desired, decimal=12)

    # --- Check tunes, chroms, beta functions, dispersions ---
    for model_name, lat_names_to_compare in {
        "bare:bare": ["new_model:bare:bare", "new_model:bare_w_xbpms:bare"],
        "3dw:3dw": ["new_model:3dw:3dw", "new_model:3dw_w_xbpms:3dw"],
        "3dw:3dw_nu_22_27": [
            "new_model:3dw:3dw_nu_22_27",
            "new_model:3dw_w_xbpms:3dw_nu_22_27",
        ],
        "17ids:17ids": ["orig_layout"],
    }.items():
        ref_sc = twi[f"orig_model:{model_name}"]["scalars"]
        ref_ar = twi[f"orig_model:{model_name}"]["arrays"]
        elem_names = ref_ar["ElementName"].tolist()
        bpm_inds = [elem_names.index(name) for name in rbpm_names]
        ref_betax = ref_ar["betax"][bpm_inds]
        ref_betay = ref_ar["betay"][bpm_inds]
        ref_etax = ref_ar["etax"][bpm_inds]
        print(
            f"Reference {model_name}: nux = {ref_sc['nux']:.3f}, nuy = {ref_sc['nuy']:.3f}"
        )
        for lat_name in lat_names_to_compare:
            sc = twi[lat_name]["scalars"]
            ar = twi[lat_name]["arrays"]

            # print(sc['nux'] - ref_sc['nux'])
            np.testing.assert_almost_equal(sc["nux"], ref_sc["nux"], decimal=16)
            np.testing.assert_almost_equal(sc["nuy"], ref_sc["nuy"], decimal=16)
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


def publicize_new_kickmap_files():

    import shutil

    src_folder = Path("./kickmaps/official")
    dst_folder = Path("/epics/aphla/apconf/nsls2/models/SR/pyelegant/kickmaps")

    for src_filename in [
        "SCW_HEX70_4_3_T_1_2m_1o19m_T2m2_woKm2sdds.sdds",
        "U21_asbuilt_g64_0o75m_T2m2_woKm2sdds.sdds",
        "U23L_asbuilt_g57_1o4m_T2m2_woKm2sdds.sdds",
        "U20_asbuilt_g52_1o5m_T2m2_woKm2sdds.sdds",
    ]:

        dst = dst_folder.joinpath(src_filename)
        if dst.exists():
            print(f'The new kickmap file "{src_filename}" alreday exists. Not copying.')
            continue

        src = src_folder.joinpath(src_filename)
        shutil.copy(src, dst)
        print(f'The new kickmap file "{src_filename}" has been copied over to "{dst}"')


def publicize_new_model_LTE_files(exist_ok=False):

    local_km_folderpath_str_pattern = "\./kickmaps/official/"
    public_km_folderpath_str = "/epics/aphla/apconf/nsls2/models/SR/pyelegant/kickmaps/"
    public_LTE_folderpath = Path("/epics/aphla/apconf/nsls2/models/SR/pyelegant/LTEs/")

    for lat_name in [name for name in list(LTE_fps) if name.startswith("new_model:")]:
        local_LTE_filepath = Path(LTE_fps[lat_name])
        public_LTE_filename = local_LTE_filepath.name.replace("_RelKMPaths.lte", ".lte")

        new_fp = public_LTE_folderpath.joinpath(public_LTE_filename)
        if (not exist_ok) and new_fp.exists():
            print(f'LTE File "{new_fp}" already exists. Not overwriting.')
            continue

        contents = local_LTE_filepath.read_text()
        contents = re.sub(
            local_km_folderpath_str_pattern, public_km_folderpath_str, contents
        )

        new_fp.write_text(contents)
        print(f'LTE File "{new_fp}" has been written.')


if __name__ == "__main__":

    RELEASE_DATE_STR = "20221027"

    USED_BEAMLINE = "RING"

    LTE_fps = {}

    LTE_fps["orig_layout"] = "20190125_VS_nsls2sr17idsmt_SQLC16_RelKMPaths.lte"
    LTE_fps["new_layout"] = f"{RELEASE_DATE_STR}_aphla_layout_RelKMPaths.lte"
    LTE_fps[
        "new_layout_w_xbpms"
    ] = f"{RELEASE_DATE_STR}_aphla_layout_w_xbpms_RelKMPaths.lte"

    LTE_fps["mag_props:bare"] = "nsls2sr_bare_20141015.lte"
    LTE_fps["mag_props:3dw"] = "nsls2sr_dw_20141119.lte"
    LTE_fps["mag_props:3dw_nu_22_27"] = "20170905_3DWs_Matched_XBPMs_nu_22_27.lte"
    # Quad settings matched by Victor Smaluk with 17 IDs included
    LTE_fps["mag_props:17ids"] = LTE_fps["orig_layout"]

    LTE_fps["orig_model:bare:bare"] = LTE_fps["mag_props:bare"]
    LTE_fps["orig_model:3dw:3dw"] = LTE_fps["mag_props:3dw"]
    LTE_fps["orig_model:3dw:3dw_nu_22_27"] = LTE_fps["mag_props:3dw_nu_22_27"]
    LTE_fps["orig_model:17ids:17ids"] = LTE_fps["mag_props:17ids"]

    for model_name in [
        "bare:bare",
        "3dw:3dw",
        "3dw:3dw_nu_22_27",
        "18ids:17ids",
        "bare_w_xbpms:bare",
        "3dw_w_xbpms:3dw",
        "3dw_w_xbpms:3dw_nu_22_27",
        "18ids_w_xbpms:17ids",
    ]:
        id_state, magnet_state = model_name.split(":")
        if id_state == magnet_state:
            model_file_name_str = id_state
        else:
            model_file_name_str = model_name.replace(":", "_MAG_")
        LTE_fps[
            f"new_model:{model_name}"
        ] = f"{RELEASE_DATE_STR}_aphla_{model_file_name_str}_RelKMPaths.lte"

    YAML_fps = {
        "mag_props": f"{RELEASE_DATE_STR}_aphla_magnet_props.yaml",
        "id_states": f"{RELEASE_DATE_STR}_aphla_ID_states.yaml",
    }

    # Run the following functions one by one in this order while adjusting the script
    if False:
        gen_magnet_props_yaml()
    if False:
        gen_new_layout_LTE_file()
    if False:
        gen_insertion_device_states_yaml()
    if False:
        gen_new_model_LTE_files()
    if False:
        load_from_proc = True
        validate_new_LTE_files(load_from_proc)

    if False:
        publicize_new_kickmap_files()
    if False:
        publicize_new_model_LTE_files(exist_ok=False)
