from pathlib import Path
import re
from shutil import copy
import os
from subprocess import Popen, PIPE

import numpy as np

import pyelegant as pe

TEST_USE_km2sdds_FALSE = False

def load_Radia_text_file(filepath):

    all_text = Path(filepath).read_text()

    if "# Horizontal Kick [micro-rad]" in all_text:
        unit = "urad"
    elif "# Horizontal Kick [T2m2]" in all_text:
        unit = "T2m2"
    elif "# Horizontal 2nd Order Kick [T2m2]" in all_text:
        unit = "T2m2"
    elif "# Total Horizontal 2nd Order Kick [T2m2]" in all_text:
        unit = "T2m2"
    else:
        raise ValueError("Unexpected unit for kickmap")

    line_list = all_text.split("\n")
    nLines = len(line_list)

    START_line_numbers = [
        i for i in range(nLines) if re.match("^START\s*$", line_list[i]) is not None
    ]
    START_line_num = {"horiz": None, "vert": None, "longit": None}
    if len(START_line_numbers) == 2:
        START_line_num["horiz"], START_line_num["vert"] = START_line_numbers
    elif len(START_line_numbers) == 3:
        (
            START_line_num["horiz"],
            START_line_num["vert"],
            START_line_num["longit"],
        ) = START_line_numbers
    else:
        raise ValueError('The number of "START" lines in Radia file must be 2 or 3.')

    param_list = []
    for line in line_list:
        if not line.startswith("#"):
            param_list.append(float(line))
            if len(param_list) == 3:
                undulator_length, nh, nv = param_list
                nh = int(nh)
                nv = int(nv)
                hkick = np.zeros((nv, nh))
                vkick = np.zeros((nv, nh))
                xmat = np.zeros((nv, nh))
                ymat = np.zeros((nv, nh))
                break

    if START_line_num["longit"] is not None:
        zkick = np.zeros((nv, nh))
    else:
        zkick = None

    line = line_list[START_line_num["horiz"] + 1]
    x = [float(s) for s in line.split()]
    y = [0.0] * len(x)

    for i in range(nv):
        line = line_list[START_line_num["horiz"] + 2 + i]
        split_line = line.split()
        y[i] = float(split_line[0])
        hkick[i, :] = [float(s) for s in split_line[1:]]
        xmat[i, :] = x
        ymat[i, :] = y[i]

        line = line_list[START_line_num["vert"] + 2 + i]
        split_line = line.split()
        vkick[i, :] = [float(s) for s in split_line[1:]]

        if START_line_num["longit"] is not None:
            line = line_list[START_line_num["longit"] + 2 + i]
            split_line = line.split()
            zkick[i, :] = [float(s) for s in split_line[1:]]

    return {
        "x": xmat,
        "y": ymat,
        "hkick": hkick,
        "vkick": vkick,
        "zkick": zkick,
        "unit": unit,
        "undulator_length": undulator_length,
    }


def load_SDDS_file(sdds_filepath):
    """"""

    str_format = ''
    #str_format = "%25.16e"

    out = pe.sdds.sdds2dicts(sdds_filepath, str_format=str_format)

    return out[0]["columns"]


def convert_SDDS_vecs_to_Radia_format(sdds_dict):
    """
    Elegant SDDS kickmap file does NOT contain longitudinal table.
    """

    nx = np.unique(sdds_dict["x"]).shape[0]
    ny = np.unique(sdds_dict["y"]).shape[0]

    radia_x = np.flipud(sdds_dict["x"].reshape((ny, nx)))
    radia_y = np.flipud(sdds_dict["y"].reshape((ny, nx)))
    radia_hkick = np.flipud(sdds_dict["xpFactor"].reshape((ny, nx)))
    radia_vkick = np.flipud(sdds_dict["ypFactor"].reshape((ny, nx)))

    return (
        nx,
        ny,
        {
            "x": radia_x,
            "y": radia_y,
            "hkick": radia_hkick,
            "vkick": radia_vkick,
            "zkick": None,
        },
    )


def change_Radia_kickmap_length(
    input_Radia_filepath, output_Radia_filepath, desired_length, decimal=5
):
    """"""

    radia_dict = load_Radia_text_file(input_Radia_filepath)

    radia_dict["hkick"] *= desired_length / radia_dict["undulator_length"]
    radia_dict["vkick"] *= desired_length / radia_dict["undulator_length"]
    if radia_dict["zkick"] is not None:
        radia_dict["zkick"] *= desired_length / radia_dict["undulator_length"]
    radia_dict["undulator_length"] = desired_length

    generate_Radia_kickmap_file(radia_dict, output_Radia_filepath, decimal=decimal)


def change_Radia_kickmap_unit(
    input_Radia_filepath,
    output_Radia_filepath,
    desired_unit,
    design_energy_GeV,
    decimal=5,
):
    """"""

    if desired_unit not in ("T2m2", "urad"):
        raise ValueError('"desired_unit" must be either "T2m2" or "urad".')

    radia_dict = load_Radia_text_file(input_Radia_filepath)

    if radia_dict["unit"] == desired_unit:
        print(
            f'Input Radia file "{input_Radia_filepath}" already has the desired unit.'
        )
    else:
        c0 = 2.99792458e8
        Brho = 1e9 * design_energy_GeV / c0  # magnetic rigidity [T-m]
        if (radia_dict["unit"] == "T2m2") and (desired_unit == "urad"):
            radia_dict["hkick"] = radia_dict["hkick"] / (Brho ** 2) * 1e6
            radia_dict["vkick"] = radia_dict["vkick"] / (Brho ** 2) * 1e6
            radia_dict["unit"] = "urad"
        elif (radia_dict["unit"] == "urad") and (desired_unit == "T2m2"):
            radia_dict["hkick"] = radia_dict["hkick"] / 1e6 * (Brho ** 2)
            radia_dict["vkick"] = radia_dict["vkick"] / 1e6 * (Brho ** 2)
            radia_dict["unit"] = "T2m2"
        else:
            raise ValueError(
                f'Uexpected unit change: from "{radia_dict["unit"]}" to "{desired_unit}"'
            )

    generate_Radia_kickmap_file(radia_dict, output_Radia_filepath, decimal=decimal)


def zero_kick(radia_dict, kick_plane_list):
    """"""

    for kick_plane in kick_plane_list:
        if kick_plane in ("h", "hkick", "horiz", "horizontal", "x"):
            radia_dict["hkick"] *= 0.0
        elif kick_plane in ("v", "vkick", "vert", "vertical", "y"):
            radia_dict["vkick"] *= 0.0
        elif kick_plane in ("z", "zkick", "longit", "longitudinal"):
            radia_dict["zkick"] *= 0.0
        else:
            raise ValueError(f'Unexpected "kick_plane": {kick_plane}')

    return radia_dict


def zero_Radia_kickmap_file(
    input_Radia_filepath, output_Radia_filepath, kick_plane_list, decimal=5
):
    """"""

    radia_dict = load_Radia_text_file(input_Radia_filepath)

    radia_dict = zero_kick(radia_dict, kick_plane_list)

    generate_Radia_kickmap_file(radia_dict, output_Radia_filepath, decimal=decimal)


def generate_Radia_kickmap_file(radia_dict, output_Radia_text_filepath, decimal=5):
    """"""

    ny, nx = radia_dict["x"].shape

    lines = [
        "# Auto-generated by generate_Radia_kickmap_file() in",
        "# aphla/machine_data/nsls2/LTE/kickmaps/conversions/conv_kickmap.py"
    ]

    if radia_dict["unit"] not in ("T2m2", "urad"):
        raise ValueError('"unit" must be either "T2m2" or "urad".')
    else:
        unit = radia_dict["unit"]

    x_line_str_format = " ".join([f"{{{i}: .{decimal}e}}" for i in range(nx)])
    line_str_format = " ".join([f"{{{i}: .{decimal}e}}" for i in range(nx + 1)])

    lines.append("# Undulator Length [m]")
    lines.append(f'{radia_dict["undulator_length"]:.3f}')

    lines.append("# Number of Horizontal Points")
    lines.append(f"{nx:d}")

    lines.append("# Number of Vertical Points")
    lines.append(f"{ny:d}")

    table_indent = " "
    y_indent = " " * (decimal + 8)

    x_line = (
        f'{table_indent}{y_indent} {x_line_str_format.format(*radia_dict["x"][0,:])}'
    )

    if unit == "T2m2":
        lines.append("# Horizontal 2nd Order Kick [T2m2]")
    elif unit == "urad":
        lines.append("# Horizontal Kick [micro-rad]")
    lines.append("START")
    lines.append(x_line)
    for i in range(ny):
        data_list = [radia_dict["y"][i, 0]] + list(radia_dict["hkick"][i, :])
        lines.append(f"{table_indent} {line_str_format.format(*data_list)}")

    if unit == "T2m2":
        lines.append("# Vertical 2nd Order Kick [T2m2]")
    elif unit == "urad":
        lines.append("# Vertical Kick [micro-rad]")
    lines.append("START")
    lines.append(x_line)
    for i in range(ny):
        data_list = [radia_dict["y"][i, 0]] + list(radia_dict["vkick"][i, :])
        lines.append(f"{table_indent} {line_str_format.format(*data_list)}")

    if radia_dict["zkick"] is not None:
        lines.append(
            "# Longitudinally Integrated Squared Transverse Magnetic Field [T2m]"
        )
        lines.append("START")
        lines.append(x_line)
        for i in range(ny):
            data_list = [radia_dict["y"][i, 0]] + list(radia_dict["zkick"][i, :])
            lines.append(f"{table_indent} {line_str_format.format(*data_list)}")

    Path(output_Radia_text_filepath).write_text("\n".join(lines))


def generate_SDDS_kickmap_file_from_Radia_kickmap_file(
    Radia_kickmap_filepath,
    output_SDDS_filepath=None,
    design_energy_GeV=None,
    decimal=None,
    use_km2sdds=False
):
    """
    The arguments "design_energy_GeV" and "decimal" are only needed
    when the input Radia file is NOT in the unit of T2m2. In this case,
    a temporary Radia file in the unit of T2m2 must be created before
    this function can convert the original Radia file into a SDDS kickmap
    file.
    """

    if output_SDDS_filepath is None:
        output_SDDS_filepath = Radia_kickmap_filepath.replace(".txt", "") + ".sdds"

    radia_dict = load_Radia_text_file(Radia_kickmap_filepath)
    if radia_dict["unit"] != "T2m2":
        if design_energy_GeV is None or decimal is None:
            raise ValueError(
                'You must provide args "design_energy_GeV" and "decimal" for unit conversion of Radia kickmap file.'
            )
        Radia_T2m2_filepath = "temp_radia_T2m2.txt"
        change_Radia_kickmap_unit(
            Radia_kickmap_filepath,
            Radia_T2m2_filepath,
            "T2m2",
            design_energy_GeV,
            decimal=decimal,
        )
        delete_temp_Radia_file = True
    else:
        Radia_T2m2_filepath = Radia_kickmap_filepath
        delete_temp_Radia_file = False

    if use_km2sdds:
        temp_sdds_filepath = output_SDDS_filepath + ".unsorted"

        if os.getenv("HOST_ARCH") is None:
            os.environ["HOST_ARCH"] = "linux-x86_64"

        p = Popen(
            ["km2sdds", "-input", Radia_T2m2_filepath, "-output", temp_sdds_filepath],
            stdout=PIPE,
            stderr=PIPE,
            encoding="utf-8",
        )
        out, err = p.communicate()
        if err:
            print("ERROR:")
            print(err)
            raise RuntimeError('Command "km2sdds" failed.')
        else:
            print('"km2sdds" command successful.')

        p = Popen(
            [
                "sddssort",
                "-column=y,increasing",
                "-column=x,increasing",
                temp_sdds_filepath,
                output_SDDS_filepath,
            ],
            stdout=PIPE,
            stderr=PIPE,
            encoding="utf-8",
        )
        out, err = p.communicate()
        if err:
            print("ERROR:")
            print(err)
            raise RuntimeError('Command "sddssort" failed.')

        Path(temp_sdds_filepath).unlink()
        Path(temp_sdds_filepath + ".1").unlink()

    else:

        radia_dict = load_Radia_text_file(Radia_T2m2_filepath)

        # Re-order and flatten to match the SDDS output file that would be
        # generated by "km2sdds", i.e., increasing order in "y" and then increasing
        # order in "x".
        x = np.flipud(radia_dict['x']).flatten()
        y = np.flipud(radia_dict['y']).flatten()
        xpFactor = np.flipud(radia_dict['hkick']).flatten()
        ypFactor = np.flipud(radia_dict['vkick']).flatten()

        columns = dict(x=x, xpFactor=xpFactor, y=y, ypFactor=ypFactor)
        columns_units = dict(x='m', y='m', xpFactor='(T*m)$a2$n', ypFactor='(T*m)$a2$n')

        params = dict(yc=np.max(y), NumberCombined=1)
        params_descr = dict(
            NumberCombined='Number of files combined to make this file')
        params_units = dict(yc='m')

        pe.sdds.dicts2sdds(
            output_SDDS_filepath, params=params, columns=columns,
            params_units=params_units, columns_units=columns_units,
            params_descr=params_descr,
            outputMode='binary', suppress_err_msg=False)

        if TEST_USE_km2sdds_FALSE:
            import matplotlib.pyplot as plt

            sdds_filepath_gen_by_km2sdds = "U20_asbuilt_g52_1o5m_T2m2.sdds"
            out_km2sdds = pe.sdds.sdds2dicts(sdds_filepath_gen_by_km2sdds)
            km2sdds_d = out_km2sdds[0]['columns']

            plt.figure()
            plt.plot(x, 'r-', km2sdds_d['x'], 'b-')

            np.testing.assert_almost_equal(x, km2sdds_d['x'], decimal=16)

            plt.figure()
            plt.plot(y, 'r-', km2sdds_d['y'], 'b-')

            np.testing.assert_almost_equal(y, km2sdds_d['y'], decimal=16)

            plt.figure()
            plt.subplot(211)
            plt.plot(xpFactor, 'r-', km2sdds_d['xpFactor'], 'b-')
            plt.subplot(212)
            plt.plot(xpFactor - km2sdds_d['xpFactor'], 'b-')

            np.testing.assert_almost_equal(xpFactor, km2sdds_d['xpFactor'], decimal=16)

            plt.figure()
            plt.subplot(211)
            plt.plot(ypFactor, 'r-', km2sdds_d['ypFactor'], 'b-')
            plt.subplot(212)
            plt.plot(ypFactor - km2sdds_d['ypFactor'], 'b-')

            np.testing.assert_almost_equal(ypFactor, km2sdds_d['ypFactor'], decimal=16)

            p = Popen(
                ["sddsdiff", sdds_filepath_gen_by_km2sdds, output_SDDS_filepath],
                stdout=PIPE, stderr=PIPE,
                encoding="utf-8",
            )
            out, err = p.communicate()
            print(out)
            if err:
                print("ERROR:")
                print(err)
                raise RuntimeError('Command "sddsdiff" failed.')

            Path(output_SDDS_filepath).unlink() # Delete test file

            plt.show()


    if delete_temp_Radia_file:
        Path(Radia_T2m2_filepath).unlink()


class KickmapFile:
    """"""

    def __init__(self, **kwargs):
        """
        If "output_unit" is different from input unit, then unit conversion will
        take place. In this case, "design_energy_GeV" is required.

        "SDDS_input_length" is required if "input_format" == 'sdds', whether or
        not length change takes place.

        If "output_length" is a positive real number, then length change will
        take place.

        "output_decimal" is relevant only when any type of conversion occurs.
        """

        self.d = {}

        for k in [
            "input_filepath",
            "input_format",
            "output_filepath",
            "output_format",
            "output_unit",
        ]:
            v = kwargs.get(k, "")

            if k in ("input_format", "output_format"):
                v = v.lower()
                if v not in ("radia", "sdds"):
                    raise ValueError(f'"{k}" must be either "radia" or "sdds".')
            elif k == "output_unit":
                if v not in ("", "T2m2", "urad"):
                    raise ValueError(f'"{k}" must be "T2m2" or "urad": "{v}"')
            elif k == "input_filepath":
                if not Path(v).exists():
                    raise ValueError(f"No such input file exists: {v}")

            self.d[k] = v

        for k in ["design_energy_GeV", "output_length", "SDDS_input_length"]:
            v = kwargs.get(k, None)

            if k == "output_length":
                if (v is not None) and (v <= 0.0):
                    raise ValueError(f'"{k}" must be None or a positive real number.')

            self.d[k] = v

        k = "zero_kick_plane_list"
        self.d[k] = kwargs.get(k, [])
        k = "output_decimal"
        self.d[k] = kwargs.get(k, 16)
        k = "use_km2sdds"
        self.d[k] = kwargs.get(k, False)

        d = self.d  # short-hand

        if (d["design_energy_GeV"] is not None) and (d["design_energy_GeV"] <= 0.0):
            raise ValueError(
                '"design_energy_GeV" must be None or a positive real number.'
            )
        if (d["SDDS_input_length"] is not None) and (d["SDDS_input_length"] <= 0.0):
            raise ValueError(
                '"SDDS_input_length" must be None or a positive real number.'
            )

        if (d["input_format"] == "sdds") and (d["SDDS_input_length"] is None):
            raise ValueError(
                'If "input_format" is SDDS, then "SDDS_input_length" must be provided.'
            )

        if (d["output_format"] == "sdds") and (d["output_unit"] == "urad"):
            raise ValueError(
                '"output_unit" cannot be "urad" when "output_format" is "sdds".'
            )

        if (
            (d["input_format"] == "sdds")
            and (d["output_unit"] == "urad")
            and (d["design_energy_GeV"] is None)
        ):
            raise ValueError(
                '"design_energy_GeV" must be provided when unit change takes place.'
            )

    # ----------------------------------------------------------------------
    def convert(self):
        """"""

        d = self.d

        if d["input_format"] == "radia":
            radia_dict = load_Radia_text_file(d["input_filepath"])
        else:
            assert d["input_format"] == "sdds"
            sdds_dict = load_SDDS_file(d["input_filepath"])
            nx, ny, radia_dict = convert_SDDS_vecs_to_Radia_format(sdds_dict)
            radia_dict["unit"] = "T2m2"
            radia_dict["undulator_length"] = d["SDDS_input_length"]

        if (d["output_unit"] != "") and (d["output_unit"] != radia_dict["unit"]):
            change_unit = True
        elif (
            (d["input_format"] == "radia")
            and (d["output_format"] == "sdds")
            and (radia_dict["unit"] == "urad")
            and (d["output_unit"] == "")
        ):
            change_unit = True
            d["output_unit"] = "T2m2"
        else:
            change_unit = False

        if (d["output_length"] is not None) and (
            d["output_length"] != radia_dict["undulator_length"]
        ):
            change_length = True
            d["input_length"] = radia_dict["undulator_length"]
        else:
            change_length = False

        if (d["zero_kick_plane_list"] is not None) and (
            d["zero_kick_plane_list"] != []
        ):
            zero_kick = True
        else:
            zero_kick = False

        if change_unit and (d["design_energy_GeV"] is None):
            raise ValueError(
                '"design_energy_GeV" must be provided when unit change takes place.'
            )

        temp_Radia_filepath = "temp.dat"
        temp2_Radia_filepath = "temp2.dat"

        decimal = d["output_decimal"]

        if (d["input_format"] == "radia") and (d["output_format"] == "radia"):

            if change_length:
                change_Radia_kickmap_length(
                    d["input_filepath"],
                    temp_Radia_filepath,
                    d["output_length"],
                    decimal=decimal,
                )
            else:
                copy(d["input_filepath"], temp_Radia_filepath)

            if change_unit:
                change_Radia_kickmap_unit(
                    temp_Radia_filepath,
                    d["output_filepath"],
                    d["output_unit"],
                    d["design_energy_GeV"],
                    decimal=decimal,
                )
            else:
                copy(temp_Radia_filepath, d["output_filepath"])

            if zero_kick:
                zero_Radia_kickmap_file(
                    d["output_filepath"],
                    d["output_filepath"],
                    d["zero_kick_plane_list"],
                    decimal=decimal,
                )

            Path(temp_Radia_filepath).unlink()

        elif (d["input_format"] == "radia") and (d["output_format"] == "sdds"):

            if change_length:
                change_Radia_kickmap_length(
                    d["input_filepath"],
                    temp_Radia_filepath,
                    d["output_length"],
                    decimal=decimal,
                )
            else:
                copy(d["input_filepath"], temp_Radia_filepath)

            if change_unit:
                change_Radia_kickmap_unit(
                    temp_Radia_filepath,
                    temp2_Radia_filepath,
                    d["output_unit"],
                    d["design_energy_GeV"],
                    decimal=decimal,
                )
            else:
                copy(temp_Radia_filepath, temp2_Radia_filepath)

            Path(temp_Radia_filepath).unlink()

            if zero_kick:
                zero_Radia_kickmap_file(
                    temp2_Radia_filepath,
                    temp2_Radia_filepath,
                    d["zero_kick_plane_list"],
                )

            generate_SDDS_kickmap_file_from_Radia_kickmap_file(
                temp2_Radia_filepath, d["output_filepath"],
                use_km2sdds=d['use_km2sdds']
            )

            Path(temp2_Radia_filepath).unlink()

        elif (d["input_format"] == "sdds") and (d["output_format"] == "radia"):
            generate_Radia_kickmap_file(
                radia_dict, temp_Radia_filepath, decimal=decimal
            )

            if change_length:
                change_Radia_kickmap_length(
                    temp_Radia_filepath,
                    temp2_Radia_filepath,
                    d["output_length"],
                    decimal=decimal,
                )
            else:
                copy(temp_Radia_filepath, temp2_Radia_filepath)

            Path(temp_Radia_filepath).unlink()

            if change_unit:
                change_Radia_kickmap_unit(
                    temp2_Radia_filepath,
                    d["output_filepath"],
                    d["output_unit"],
                    d["design_energy_GeV"],
                    decimal=decimal,
                )
            else:
                copy(temp2_Radia_filepath, d["output_filepath"])

            if zero_kick:
                zero_Radia_kickmap_file(
                    d["output_filepath"],
                    d["output_filepath"],
                    d["zero_kick_plane_list"],
                )

            Path(temp2_Radia_filepath).unlink()

        else:
            assert (d["input_format"] == "sdds") and (d["output_format"] == "sdds")

            # In this case, unit change is not allowed.

            if change_length:
                generate_Radia_kickmap_file(
                    radia_dict, temp_Radia_filepath, decimal=decimal
                )
                change_Radia_kickmap_length(
                    temp_Radia_filepath,
                    temp2_Radia_filepath,
                    d["output_length"],
                    decimal=decimal,
                )

                Path(temp_Radia_filepath).unlink()

                generate_SDDS_kickmap_file_from_Radia_kickmap_file(
                    temp2_Radia_filepath, d["output_filepath"],
                    use_km2sdds=d['use_km2sdds']
                )

                Path(temp2_Radia_filepath).unlink()
            else:
                copy(d["input_filepath"], d["output_filepath"])

            if zero_kick:
                zero_Radia_kickmap_file(
                    d["output_filepath"],
                    d["output_filepath"],
                    d["zero_kick_plane_list"],
                )

def test_use_km2sdds_False():

    global TEST_USE_km2sdds_FALSE
    TEST_USE_km2sdds_FALSE = True

    input_filepath = "U20_asbuilt_g52.txt"
    input_format = "radia"
    energy = 3.0
    decimal = 16
    output_length = 1.5

    common_kwargs =  dict(
            input_filepath=input_filepath,
            input_format=input_format,
            output_length=output_length,
            design_energy_GeV=energy,
            output_decimal=decimal,
        )

    kwargs = dict(
            output_filepath="test.sdds",
            output_format="sdds",
            output_unit="T2m2",
            use_km2sdds=False
        )
    kwargs.update(common_kwargs)

    km = KickmapFile(**kwargs)
    km.convert()

def test_conversion():

    # Reproduce conversion_history.py / generate_U20_asbuilt_g52_3o0m():

    common_kwargs =  dict(
            input_filepath="U20_asbuilt_g52.txt",
            input_format="radia",
            output_length=1.5,
            design_energy_GeV=3.0,
            output_decimal=16,
            use_km2sdds=True,
            #use_km2sdds=False,
        )

    kwargs_list = [
        dict(
            output_filepath="U20_asbuilt_g52_1o5m_urad.txt",
            output_format="radia",
            output_unit="urad"
        ),
        dict(
            output_filepath="U20_asbuilt_g52_1o5m_T2m2.sdds",
            output_format="sdds",
            output_unit="T2m2"
        )
    ]

    for kwargs in kwargs_list:
        kwargs.update(common_kwargs)
        km = KickmapFile(**kwargs)
        km.convert()

if __name__ == "__main__":

    if False:
        test_conversion()
    elif False:
        test_use_km2sdds_False()
