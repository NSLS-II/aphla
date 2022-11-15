import os, sys
import os.path as osp

from pyeletra import kickmap_folderpath
from pyeletra import convkm

temp_json_filepath = 'test.json'

########################################################################
class convkm_options:
    """"""

    #----------------------------------------------------------------------
    def __init__(self, **kwargs):
        """Constructor"""

        self.kwargs = dict(input_filepath='', input_format='',
                           output_filepath='', output_format='',
                           output_unit='', design_energy_GeV='null',
                           output_length='null', SDDS_input_length='null',
                           output_decimal=16, zero_kick_plane_list='null')

        for k, v in kwargs.iteritems():

            if k == 'zero_kick_plane_list':
                if v != 'null':
                    v = '"{0}"'.format(v)

            self.kwargs[k] = v

        self.json_text_template = '''
{{
    "input_filepath": "{input_filepath}",
    "input_format"  : "{input_format}",

    "output_filepath": "{output_filepath}",
    "output_format"  : "{output_format}",

    "output_unit"      : "{output_unit}",
    "design_energy_GeV": {design_energy_GeV},

    "output_length"    : {output_length},
    "SDDS_input_length": {SDDS_input_length},

    "output_decimal": {output_decimal},

    "zero_kick_plane_list": {zero_kick_plane_list}
}}
'''

    #----------------------------------------------------------------------
    def convert(self, json_filepath):
        """"""

        with open(json_filepath,'w') as fobj:
            fobj.write(self.json_text_template.format(**self.kwargs))

        sys.argv = ['', json_filepath]
        convkm.main()

#----------------------------------------------------------------------
def generate_W100_DF_asbuilt_3o4m_zeroed_longit_table():
    """"""

    input_filepath = 'W100_DF_asbuilt.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 3.4

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='W100_DF_asbuilt_3o4m_zeroed_longit_table_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           zero_kick_plane_list='z',
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='W100_DF_asbuilt_3o4m_zeroed_longit_table.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           zero_kick_plane_list='z',
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_W100_DF_asbuilt_3o4m():
    """"""

    input_filepath = 'W100_DF_asbuilt.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 3.4

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='W100_DF_asbuilt_3o4m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='W100_DF_asbuilt_3o4m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_W100_DF_asbuilt_3o4m_2o5GeV():
    """"""

    input_filepath = 'W100_DF_asbuilt.txt'
    input_format   = 'radia'
    energy         = 2.5
    decimal        = 16
    output_length  = 3.4

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='W100_DF_asbuilt_3o4m_2o5GeV_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='W100_DF_asbuilt_3o4m_2o5GeV_.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_W100_DF_asbuilt_3o4m_2o0GeV():
    """"""

    input_filepath = 'W100_DF_asbuilt.txt'
    input_format   = 'radia'
    energy         = 2.0
    decimal        = 16
    output_length  = 3.4

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='W100_DF_asbuilt_3o4m_2o0GeV_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='W100_DF_asbuilt_3o4m_2o0GeV_.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_W100_DF_asbuilt_1o7m():
    """"""

    input_filepath = 'W100_DF_asbuilt.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 1.7

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='W100_DF_asbuilt_1o7m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='W100_DF_asbuilt_1o7m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_W100_DF_asbuilt_intermediate_gap_3o4m(gap):
    """"""

    input_filepath = 'W100_DF_asbuilt_g{0:d}.txt'.format(gap)
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 3.4

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='W100_DF_asbuilt_g{0:d}_3o4m_urad.txt'.format(gap),
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='W100_DF_asbuilt_g{0:d}_3o4m.sdds'.format(gap),
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_W100_DF_asbuilt_3o5m():
    """"""

    input_filepath = 'W100_DF_asbuilt.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 3.5

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='W100_DF_asbuilt_3o5m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='W100_DF_asbuilt_3o5m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_U20_asbuilt_g52_1o5m():
    """"""

    input_filepath = 'U20_asbuilt_g52.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 1.5

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U20_asbuilt_g52_1o5m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U20_asbuilt_g52_1o5m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_U20_asbuilt_g52_3o0m():
    """"""

    input_filepath = 'U20_asbuilt_g52.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 3.0

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U20_asbuilt_g52_3o0m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U20_asbuilt_g52_3o0m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_U21NX_boostmag():
    """
    OBSOLETE: DO NOT USE
    """

    input_filepath = 'U21NX_boostmag.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U21NX_boostmag.sdds',
           output_format='sdds', output_unit='T2m2',
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_U22_asbuilt_6m_g75mm_2o97m():
    """"""

    input_filepath = 'U22_asbuilt_6m_g75mm.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 2.97

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U22_asbuilt_6m_g75mm_2o97m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U22_asbuilt_6m_g75mm_2o97m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_EPU49v2LVG11KickMap2Pure_1o96m():
    """"""

    input_filepath = 'EPU49v2LVG11KickMap2Pure.dat'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 1.96

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU49v2LVG11KickMap2Pure_1o96m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU49v2LVG11KickMap2Pure_1o96m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_EPU49v2LVG11KickMapRes_1o96m():
    """"""

    input_filepath = 'EPU49v2LVG11KickMapRes.dat'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 1.96

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU49v2LVG11KickMapRes_1o96m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU49v2LVG11KickMapRes_1o96m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_U21NX_boostmag_1o5m():
    """
    OBSOLETE: DO NOT USE
    """

    input_filepath = 'U21NX_boostmag.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 1.5

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U21NX_boostmag_1o5m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U21NX_boostmag_1o5m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_U21NX_boostmag_0o75m_AMX_FMX():
    """
    OBSOLETE: DO NOT USE
    """

    input_filepath = 'U21NX_boostmag.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 0.75

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U21NX_boostmag_0o75m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U21NX_boostmag_0o75m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_U21_asbuilt_g64_1o5m():
    """"""

    input_filepath = 'U21_asbuilt_g64.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 1.5

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U21_asbuilt_g64_1o5m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U21_asbuilt_g64_1o5m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_U21_asbuilt_g64_0o75m():
    """"""

    input_filepath = 'U21_asbuilt_g64.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 0.75

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U21_asbuilt_g64_0o75m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U21_asbuilt_g64_0o75m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)


#----------------------------------------------------------------------
def generate_U22_asbuilt_6m_g75mm_1o5m():
    """"""

    input_filepath = 'U22_asbuilt_6m_g75mm.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 1.5

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U22_asbuilt_6m_g75mm_1o5m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U22_asbuilt_6m_g75mm_1o5m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_U22_asbuilt_6m_g75mm_3o0m():
    """"""

    input_filepath = 'U22_asbuilt_6m_g75mm.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 3.0

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U22_asbuilt_6m_g75mm_3o0m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U22_asbuilt_6m_g75mm_3o0m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_U23L_asbuilt_g61_2o8m():
    """"""

    input_filepath = 'U23L_asbuilt_g61.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 2.8

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U23L_asbuilt_g61_2o8m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U23L_asbuilt_g61_2o8m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_U23L_asbuilt_g57_2o8m():
    """"""

    input_filepath = 'U23L_asbuilt_g57.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 2.8

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U23L_asbuilt_g57_2o8m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U23L_asbuilt_g57_2o8m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_U23L_asbuilt_g57_1o4m():
    """"""

    input_filepath = 'U23L_asbuilt_g57.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 1.4

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U23L_asbuilt_g57_1o4m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    #opts_list.append(convkm_options(
        #**dict(input_filepath=input_filepath, input_format=input_format,
           #output_filepath='U23L_asbuilt_g57_1o4m.sdds',
           #output_format='sdds', output_unit='T2m2', output_length=output_length,
           #design_energy_GeV=energy, output_decimal=decimal,
           #)))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_EPU49v2LVG11KickMap2Pure_2o0m():
    """"""

    input_filepath = 'EPU49v2LVG11KickMap2Pure.dat'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 2.0

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU49v2LVG11KickMap2Pure_2o0m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU49v2LVG11KickMap2Pure_2o0m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_EPU49v2LVG11KickMapRes_2o0m():
    """"""

    input_filepath = 'EPU49v2LVG11KickMapRes.dat'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 2.0

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU49v2LVG11KickMapRes_2o0m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU49v2LVG11KickMapRes_2o0m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_EPU105ESMv2LVG19L2800mmKickMap2Pure_2o8m():
    """"""

    input_filepath = 'EPU105ESMv2LVG19L2800mmKickMap2Pure.dat'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 2.8

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU105ESMv2LVG19L2800mmKickMap2Pure_2o8m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU105ESMv2LVG19L2800mmKickMap2Pure_2o8m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_EPU105ESMv2LVG19L2800mmKickMapRes_2o8m():
    """"""

    input_filepath = 'EPU105ESMv2LVG19L2800mmKickMapRes.dat'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 2.8

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU105ESMv2LVG19L2800mmKickMapRes_2o8m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU105ESMv2LVG19L2800mmKickMapRes_2o8m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_EPU105ESMv2LVG19PS14L2800mmKickMapRes_2o8m():
    """"""

    input_filepath = 'EPU105ESMv2LVG19PS14L2800mmKickMapRes.dat'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 2.8

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath=input_filepath.replace('.dat', '_2o8m_urad.txt'),
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath=input_filepath.replace('.dat', '_2o8m.sdds'),
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_EPU49ESMv2LVG16KickMap2Pure_sdds():
    """"""

    input_filepath = 'EPU49ESMv2LVG16KickMap2Pure.dat'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU49ESMv2LVG16KickMap2Pure.sdds',
           output_format='sdds', output_unit='T2m2',
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_EPU49ESMv2LVG16KickMapRes_sdds():
    """"""

    input_filepath = 'EPU49ESMv2LVG16KickMapRes.dat'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU49ESMv2LVG16KickMapRes.sdds',
           output_format='sdds', output_unit='T2m2',
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_EPU57v2LVG16KickMap2Pure_1o75m():
    """"""

    input_filepath = 'EPU57v2LVG16KickMap2Pure.dat'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 1.75

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU57v2LVG16KickMap2Pure_1o75m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU57v2LVG16KickMap2Pure_1o75m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_EPU57v2LVG16KickMapRes_1o75m():
    """"""

    input_filepath = 'EPU57v2LVG16KickMapRes.dat'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 1.75

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU57v2LVG16KickMapRes_1o75m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU57v2LVG16KickMapRes_1o75m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_EPU57v2LVG16KickMap2Pure_3o5m():
    """"""

    input_filepath = 'EPU57v2LVG16KickMap2Pure.dat'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 3.5

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU57v2LVG16KickMap2Pure_3o5m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU57v2LVG16KickMap2Pure_3o5m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_EPU57v2LVG16KickMapRes_3o5m():
    """
    SIX EPU with all 27 current strip power supplies.
    """

    input_filepath = 'EPU57v2LVG16KickMapRes.dat'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 3.5

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU57v2LVG16KickMapRes_3o5m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU57v2LVG16KickMapRes_3o5m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_EPU57v2LVG16KickMap2Pure_3o3m():
    """"""

    input_filepath = 'EPU57v2LVG16KickMap2Pure.dat'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 3.3

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU57v2LVG16KickMap2Pure_3o3m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU57v2LVG16KickMap2Pure_3o3m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_EPU57v2LVG16KickMapRes_3o3m():
    """"""

    input_filepath = 'EPU57v2LVG16KickMapRes.dat'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 3.3

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU57v2LVG16KickMapRes_3o3m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU57v2LVG16KickMapRes_3o3m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_EPU57v2ModeParaP28_6G16v2KickMap2Pure_3o5m():
    """
    """

    input_filepath = 'EPU57v2ModeParaP28_6G16v2KickMap2Pure.dat'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 3.5

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU57v2ModeParaP28_6G16v2KickMap2Pure_3o5m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU57v2ModeParaP28_6G16v2KickMap2Pure_3o5m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_EPU57v2ModeParaP28_6G16v2KickMapRes_3o5m():
    """
    SIX EPU with only 14 current strip (CS) power supplies,
    instead of all 27 CS power supplies.
    """

    input_filepath = 'EPU57v2ModeParaP28_6G16v2KickMapRes.dat'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 3.5

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU57v2ModeParaP28_6G16v2KickMapRes_3o5m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EPU57v2ModeParaP28_6G16v2KickMapRes_3o5m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_ESM_EPU57v2LVG16KickMap2Pure_1o4m():
    """"""

    input_filepath = 'EPU57v2LVG16KickMap2Pure.dat'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 1.4

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='ESM_EPU57v2LVG16KickMap2Pure_1o4m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='ESM_EPU57v2LVG16KickMap2Pure_1o4m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_ESM_EPU57v2LVG16KickMapRes_1o4m():
    """"""

    input_filepath = 'EPU57v2LVG16KickMapRes.dat'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 1.4

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='ESM_EPU57v2LVG16KickMapRes_1o4m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='ESM_EPU57v2LVG16KickMapRes_1o4m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_SCW_HEX_4_2T_1o0m():
    """"""

    input_filepath = 'SCW_HEX_4_2T.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 1.0

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='SCW_HEX_4_2T_1o0m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='SCW_HEX_4_2T_1o0m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_SCW80_HEX_4_5T_1o0m():
    """"""
    input_filepath = 'SCW80_HEX_4_5T.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 1.0

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='SCW80_HEX_4_5T_1o0m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='SCW80_HEX_4_5T_1o0m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)


#----------------------------------------------------------------------
def generate_SST_U42_1o6m():
    """"""

    input_filepath = 'U42.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 1.6

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U42_1o6m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='U42_1o6m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_SST_EPU60_vert_0o96m():
    """"""

    input_filepath = 'EU60_g15_vert.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 0.96

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EU60_g15_vert_0o96m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EU60_g15_vert_0o96m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_SST_EPU60_vert_0o89m():
    """"""

    input_filepath = 'EU60_g15_vert.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 0.89

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EU60_g15_vert_0o89m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EU60_g15_vert_0o89m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_SST_EPU60_heli_0o96m():
    """"""

    input_filepath = 'EU60_g15_heli.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 0.96

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EU60_g15_heli_0o96m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EU60_g15_heli_0o96m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_SST_EPU60_heli_0o89m():
    """"""

    input_filepath = 'EU60_g15_heli.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 0.89

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EU60_g15_heli_0o89m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EU60_g15_heli_0o89m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_SST_EPU60_45d_0o96m():
    """"""

    input_filepath = 'EU60_g15_45d.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 0.96

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EU60_g15_45d_0o96m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EU60_g15_45d_0o96m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_SST_EPU60_45d_0o89m():
    """"""

    input_filepath = 'EU60_g15_45d.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 0.89

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EU60_g15_45d_0o89m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='EU60_g15_45d_0o89m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_NYX_U18_1o0m():
    """"""

    input_filepath = 'X25MGU.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 1.0

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='X25MGU_1o0m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='X25MGU_1o0m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    for opts in opts_list:
        opts.convert(temp_json_filepath)
    os.remove(temp_json_filepath)

#----------------------------------------------------------------------
def generate_3PW_unscaled_0o2m():
    """"""

    input_filepath = '3PW_28mm_kickmap110711.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 0.6 # Note that this needs to be 0.6, NOT 0.2, as
    # the most kicks for 3PW is contained within 0.2 m, and you don't want
    # to scale the kick down. Toshi integrated the whole 0.6 m so that the
    # tail fields are included, but the actual device length is 0.2 m.

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='3PW_28mm_kickmap110711_unscaled_0o2m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath='3PW_28mm_kickmap110711_unscaled_0o2m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    try:
        for opts in opts_list:
            opts.convert(temp_json_filepath)
    except:
        pass
    os.remove(temp_json_filepath)

    with open('3PW_28mm_kickmap110711_unscaled_0o2m_urad.txt', 'r') as f:
        all_text = f.read()
    all_text = all_text.replace(
        '# Undulator Length [m]\n0.6', '# Undulator Length [m]\n0.2')
    with open('3PW_28mm_kickmap110711_unscaled_0o2m_urad.txt', 'w') as f:
        f.write(all_text)

#----------------------------------------------------------------------
def generate_2T_3PW_unscaled_0o2m(with_gradient):
    """"""

    if not with_gradient:
        prefix = 'C3PW_10mm_kickmap'
    else:
        prefix = 'C3PW_10mm_grad_kickmap'

    input_filepath = prefix + '.txt'
    input_format   = 'radia'
    energy         = 3.0
    decimal        = 16
    output_length  = 0.6 # Note that this needs to be 0.6, NOT 0.2, as
    # the most kicks for 3PW is contained within 0.2 m, and you don't want
    # to scale the kick down. Toshi integrated the whole 0.6 m so that the
    # tail fields are included, but the actual device length is 0.2 m.

    opts_list = []

    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath=prefix+'_unscaled_0o2m_urad.txt',
           output_format='radia', output_unit='urad', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))
    opts_list.append(convkm_options(
        **dict(input_filepath=input_filepath, input_format=input_format,
           output_filepath=prefix+'_unscaled_0o2m.sdds',
           output_format='sdds', output_unit='T2m2', output_length=output_length,
           design_energy_GeV=energy, output_decimal=decimal,
           )))

    try:
        for opts in opts_list:
            opts.convert(temp_json_filepath)
    except:
        pass
    os.remove(temp_json_filepath)

    with open(prefix+'_unscaled_0o2m_urad.txt', 'r') as f:
        all_text = f.read()
    all_text = all_text.replace(
        '# Undulator Length [m]\n0.6', '# Undulator Length [m]\n0.2')
    with open(prefix+'_unscaled_0o2m_urad.txt', 'w') as f:
        f.write(all_text)


if __name__ == '__main__':

    #generate_W100_DF_asbuilt_3o4m()
    #generate_W100_DF_asbuilt_3o4m_zeroed_longit_table()
    #generate_W100_DF_asbuilt_3o4m_2o5GeV()
    #generate_W100_DF_asbuilt_3o4m_2o0GeV()
    #generate_W100_DF_asbuilt_3o5m()
    #generate_U20_asbuilt_g52_1o5m()
    #generate_U21NX_boostmag() # OBSOLETE: DO NOT USE
    #generate_U22_asbuilt_6m_g75mm_2o97m()
    #generate_EPU49v2LVG11KickMap2Pure_1o96m()
    #generate_EPU49v2LVG11KickMapRes_1o96m()
    #generate_U21NX_boostmag_1o5m() OBSOLETE: DO NOT USE
    #generate_U22_asbuilt_6m_g75mm_1o5m()
    #generate_EPU49v2LVG11KickMap2Pure_2o0m()
    #generate_EPU49v2LVG11KickMapRes_2o0m()
    #generate_EPU105ESMv2LVG19L2800mmKickMap2Pure_2o8m()
    #generate_EPU105ESMv2LVG19L2800mmKickMapRes_2o8m()
    #generate_EPU49ESMv2LVG16KickMap2Pure_sdds()
    #generate_EPU49ESMv2LVG16KickMapRes_sdds()
    #generate_EPU57v2LVG16KickMap2Pure_1o75m()
    #generate_EPU57v2LVG16KickMapRes_1o75m()
    #generate_ESM_EPU57v2LVG16KickMap2Pure_1o4m()
    #generate_ESM_EPU57v2LVG16KickMapRes_1o4m()
    #generate_EPU57v2LVG16KickMap2Pure_3o5m()
    #generate_EPU57v2LVG16KickMapRes_3o5m()
    #generate_EPU57v2LVG16KickMap2Pure_3o3m()
    #generate_EPU57v2LVG16KickMapRes_3o3m()
    #generate_W100_DF_asbuilt_intermediate_gap_3o4m(20)
    #generate_W100_DF_asbuilt_intermediate_gap_3o4m(30)
    #generate_W100_DF_asbuilt_intermediate_gap_3o4m(40)
    #generate_W100_DF_asbuilt_intermediate_gap_3o4m(50)
    #generate_EPU105ESMv2LVG19PS14L2800mmKickMapRes_2o8m()
    #generate_EPU57v2ModeParaP28_6G16v2KickMap2Pure_3o5m()
    #generate_EPU57v2ModeParaP28_6G16v2KickMapRes_3o5m()
    #generate_U23L_asbuilt_g61_2o8m()
    #generate_U23L_asbuilt_g57_2o8m()
    #generate_SCW_HEX_4_2T_1o0m()
    #generate_SCW80_HEX_4_5T_1o0m()
    #generate_SST_U42_1o6m()
    #generate_SST_EPU60_vert_0o96m()
    #generate_SST_EPU60_heli_0o96m()
    #generate_SST_EPU60_45d_0o96m()
    #generate_NYX_U18_1o0m()
    #generate_W100_DF_asbuilt_1o7m()
    #generate_U23L_asbuilt_g57_1o4m()
    #generate_3PW_unscaled_0o2m()
    #generate_U21_asbuilt_g64_1o5m()
    #generate_U21_asbuilt_g64_0o75m()
    #generate_U21NX_boostmag_0o75m_AMX_FMX() # OBSOLETE: DO NOT USE

    #generate_U20_asbuilt_g52_3o0m()
    #generate_U22_asbuilt_6m_g75mm_3o0m()
    #generate_SST_EPU60_vert_0o89m()
    #generate_SST_EPU60_heli_0o89m()
    #generate_SST_EPU60_45d_0o89m()


    #generate_2T_3PW_unscaled_0o2m(with_gradient=False)
    generate_2T_3PW_unscaled_0o2m(with_gradient=True)
