import sys
from copy import deepcopy

from conv_kickmap import KickmapFile


def _gen_radia_sdds_with_without_km2sdds(radia_file_base_name, common_kwargs):

    kwargs_list = []
    for output_format in ["radia", "sdds"]:
        if output_format == "radia":
            unit = "urad"
            ext = "txt"
        elif output_format == "sdds":
            unit = "T2m2"
            ext = "sdds"
        else:
            raise ValueError

        len_str = f'{common_kwargs["output_length"]:.3f}'
        for i, c in enumerate(len_str[::-1]):
            if c != "0":
                if i == 0:
                    stop = None
                else:
                    stop = -i
                break
        len_str = len_str[:stop] + "m"
        len_str = len_str.replace(".", "o")

        output_file_base_name = f"{radia_file_base_name}_{len_str}_{unit}"

        kwargs = dict(
            output_filepath=f"{output_file_base_name}.{ext}",
            output_format=output_format,
            output_unit=unit,
        )

        if output_format == "sdds":
            kwargs["use_km2sdds"] = True
            kwargs["output_filepath"] = f"{output_file_base_name}_wKm2sdds.{ext}"
            kwargs_list.append(deepcopy(kwargs))
            kwargs["use_km2sdds"] = False
            kwargs["output_filepath"] = f"{output_file_base_name}_woKm2sdds.{ext}"
            kwargs_list.append(kwargs)
        else:
            kwargs_list.append(kwargs)

    for kwargs in kwargs_list:
        kwargs.update(common_kwargs)
        km = KickmapFile(**kwargs)
        print(kwargs)
        try:
            km.convert()
            print("\nSuccess!")
        except:
            print("\n*** ERROR during KickmapFile.convert() ***")
        print("")


def gen_C27_HEX():

    radia_file_base_name = "SCW_HEX70_4_3_T_1_2m"

    common_kwargs = dict(
        input_filepath=f"../orig_Radia/{radia_file_base_name}.txt",
        input_format="radia",
        output_length=1.19,
        design_energy_GeV=3.0,
        output_decimal=16,
    )

    _gen_radia_sdds_with_without_km2sdds(radia_file_base_name, common_kwargs)


def gen_C03_1o5m():

    radia_file_base_name = "U20_asbuilt_g52"

    common_kwargs = dict(
        input_filepath=f"../orig_Radia/{radia_file_base_name}.txt",
        input_format="radia",
        output_length=1.5,
        design_energy_GeV=3.0,
        output_decimal=16,
    )

    _gen_radia_sdds_with_without_km2sdds(radia_file_base_name, common_kwargs)


def gen_C16_1o4m():

    radia_file_base_name = "U23L_asbuilt_g57"

    common_kwargs = dict(
        input_filepath=f"../orig_Radia/{radia_file_base_name}.txt",
        input_format="radia",
        output_length=1.4,
        design_energy_GeV=3.0,
        output_decimal=16,
    )

    _gen_radia_sdds_with_without_km2sdds(radia_file_base_name, common_kwargs)


def gen_C17_0o75m():

    radia_file_base_name = "U21_asbuilt_g64"

    common_kwargs = dict(
        input_filepath=f"../orig_Radia/{radia_file_base_name}.txt",
        input_format="radia",
        output_length=0.75,
        design_energy_GeV=3.0,
        output_decimal=16,
    )

    _gen_radia_sdds_with_without_km2sdds(radia_file_base_name, common_kwargs)


if __name__ == "__main__":

    if sys.argv[1] == "C27":
        gen_C27_HEX()
    elif sys.argv[1] == "C03":
        gen_C03_1o5m()
    elif sys.argv[1] == "C16":
        gen_C16_1o4m()
    elif sys.argv[1] == "C17":
        gen_C17_0o75m()
