from setuptools import setup, find_packages
from setuptools.command.install import install
import sys
import os
import subprocess
from pathlib import Path
import shutil

MAJOR = 2
MINOR = 0
MICRO = 0
ISRELEASED = False
VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

def _minimal_ext_cmd(cmd):
    # construct minimal environment
    env = {}
    for k in ['SYSTEMROOT', 'PATH']:
        v = os.environ.get(k)
        if v is not None:
            env[k] = v
    # LANGUAGE is used on win32
    env['LANGUAGE'] = 'C'
    env['LANG'] = 'C'
    env['LC_ALL'] = 'C'
    out = subprocess.Popen(cmd, stdout = subprocess.PIPE, env=env).communicate()[0]
    return out

def git_revision():
    try:
        out = _minimal_ext_cmd(['git', "rev-parse", "HEAD"])
        GIT_REVISION = out.strip().decode('ascii')
    except OSError:
        GIT_REVISION = "Unknown"

    return GIT_REVISION

def write_version_py(filename='aphla/version.py'):
    cnt = """
# THIS FILE IS GENERATED FROM APHLA SETUP.PY
short_version = '%(version)s'
version = '%(version)s'
full_version = '%(full_version)s'
revision = '%(revision)s'
release = %(isrelease)s

if not release:
    version = full_version
"""
    # Adding the git rev number needs to be done inside write_version_py(),
    # otherwise the import of numpy.version messes up the build under Python 3.
    FULLVERSION = VERSION
    if os.path.exists(".git"):
        AP_REVISION = git_revision()
    elif os.path.exists('aphla/version.py'):
        # must be a source distribution, use existing version file
        from aphla.version import revision as AP_REVISION
    else:
        AP_REVISION = "Unknown"

    if not ISRELEASED:
        FULLVERSION += '.dev-' + AP_REVISION[:7]

    a = open(filename, 'w')
    try:
        a.write(cnt % {'version': VERSION,
                       'full_version' : FULLVERSION,
                       'revision' : AP_REVISION,
                       'isrelease': str(ISRELEASED)})
    finally:
        a.close()

write_version_py()

program_name = 'aphla'

facility_name_arg = 'facility-name'

com_req_pakcages = ['numpy', 'cothread', 'h5py', 'ruamel.yaml']

if ('install' in sys.argv) or ('sdist' in sys.argv):

    facility_name_opt = [v for v in sys.argv
                         if v.startswith(f'--{facility_name_arg}=')]
    if len(facility_name_opt) == 0:
        raise ValueError(f'Required arg "--{facility_name_arg}" is missing')
    elif len(facility_name_opt) > 1:
        raise ValueError(f'Multiple arg "--{facility_name_arg}" found')

    facility_name = facility_name_opt[0][len(f'--{facility_name_arg}='):]

    available_facility_names = ['generic', 'nsls2']
    if facility_name not in available_facility_names:
        print('* Only the following facility names are available:')
        print('      ' + ', '.join(available_facility_names))
        raise ValueError(
            f'Specified facility_name "{facility_name}" is not available.')

    this_folder = os.path.dirname(os.path.abspath(__file__))

    facility_yaml_filename = 'facility.yaml'
    shutil.copy(Path(this_folder).joinpath('facility_configs', f'{facility_name}.yaml'),
                Path(this_folder).joinpath('aphla', facility_yaml_filename))

    sys.argv.remove(facility_name_opt[0])

    if 'sdist' in sys.argv:
        # Modify the tarball name to be "aphla-{facility_name}-?.?.?.tar.gz"
        program_name += f'-{facility_name}'

    req_pakcages = []
    if facility_name == 'nsls2':
        req_pakcages += []

    other_setup_opts = dict(
        install_requires=req_pakcages,
        # ^ These requirements are actually NOT being checked (as of 04/01/2020)
        #   due to the known bug with the custom install:
        #       (https://github.com/pypa/setuptools/issues/456)
        )
elif 'egg_info' in sys.argv:
    other_setup_opts = dict(install_requires=com_req_pakcages)
else:
    raise RuntimeError()

class InstallCommand(install):
    """"""

    user_options = install.user_options + [
        (f'{facility_name_arg}=', None, 'Facility name for "aphla" installation')
    ]

    def initialize_options(self):
        """"""
        install.initialize_options(self)
        self.facility_name = facility_name

    def finalize_options(self):
        """"""
        print((f'Specified facility name for "aphla" installation is '
               f'"{self.facility_name}"'))
        install.finalize_options(self)

    def run(self):
        """"""
        print(self.facility_name)
        install.run(self)

setup(
    name = program_name,
    version = VERSION,
    packages = find_packages(
        exclude=['aphla.tests', 'aphla.gui', 'aphla.gui.*', 'aphla.contrib',
                 'aphla.contrib.*', 'aphla.mpfit', 'aphla.dms',
                 'aphla.machines.*']),
    #include_package_data = True,
    package_data = {'aphla': [facility_yaml_filename]},
    #package_data = {'aphla.gui.TinkerUtils': ['tinker_columns.sqlite']},
    #package_data = {
    #    # any these files
    #    'aphla.gui': ['data/*'],
    #    'aphla.machines': ['*']},
    #py_modules = [
    #    # GUI
    #    'aphla.gui.gui_resources',
    #    'aphla.gui.aplauncher',
    #    'aphla.gui.orbit', 'aphla.gui.orbitconfdlg',
    #    'aphla.gui.apbba'],
    #    'aphla.gui.channelexplorer',
    #install_requires = ['distribute', 'matplotlib', 'cothread',
    #                    'numpy', 'scipy'],
    entry_points = {
        #'gui_scripts': [
            #'mleap = aphla.gui.mleap:main',
            #'apbba = aphla.gui.apbba:main',
            #'aplauncher = aphla.gui.aplauncher:main',
            #'apcurrentmonitor = aphla.gui.apcurrentmonitor:main',
            #'apchx = aphla.gui.channelexplorer:main',
            #'aptinker = aphla.gui.aptinker:main'
            #]
        },
    description = "Accelerator control and experiment toolkit",
    author = "Lingyun Yang, Yoshiteru Hidaka",
    maintainer = "Yoshiteru Hidaka",
    maintainer_email = "yhidaka@bnl.gov",
    url = 'https://github.com/NSLS-II/aphla',
    cmdclass={'install': InstallCommand},
    **other_setup_opts
    )

