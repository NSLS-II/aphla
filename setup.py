from setuptools import setup, find_packages
import os
import subprocess

MAJOR = 0
MINOR = 8
MICRO = 22
ISRELEASED = True
VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

def hg_version():
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

    try:
        out = _minimal_ext_cmd(['hg', 'id', '-n', '-i'])
        HG_REVISION = out.strip().decode('ascii')
    except OSError:
        HG_REVISION = "Unknown"

    return HG_REVISION

def write_version_py(filename='aphla/version.py'):
    cnt = """
# THIS FILE IS GENERATED FROM APHLA SETUP.PY
short_version = '%(version)s'
version = '%(version)s'
full_version = '%(full_version)s'
hg_revision = '%(hg_revision)s'
release = %(isrelease)s

if not release:
    version = full_version
"""
    # Adding the git rev number needs to be done inside write_version_py(),
    # otherwise the import of numpy.version messes up the build under Python 3.
    FULLVERSION = VERSION
    if os.path.exists('.hg'):
        HG_REVISION = hg_version()
    elif os.path.exists('aphla/version.py'):
        # must be a source distribution, use existing version file
        from aphla.version import hg_revision as HG_REVISION
    else:
        HG_REVISION = "Unknown"

    if not ISRELEASED:
        FULLVERSION += '.dev-' + HG_REVISION[:7]

    a = open(filename, 'w')
    try:
        a.write(cnt % {'version': VERSION,
                       'full_version' : FULLVERSION,
                       'hg_revision' : HG_REVISION,
                       'isrelease': str(ISRELEASED)})
    finally:
        a.close()

write_version_py()

setup(
    name = "aphla",
    version = VERSION,
    packages = find_packages(exclude=['tests']),
    include_package_data = True,
    package_data = {'aphla.gui.TinkerUtils': ['tinker_columns.sqlite']},
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
        'gui_scripts': [
            'mleap = aphla.gui.mleap:main',
            'apbba = aphla.gui.apbba:main',
            'aplauncher = aphla.gui.aplauncher:main',
            'apcurrentmonitor = aphla.gui.apcurrentmonitor:main',
            'apchx = aphla.gui.channelexplorer:main',
            'aptinker = aphla.gui.aptinker:main'
            ]
        },
    description = "Accelerator control and experiment toolkit",
    author = "Lingyun Yang, Yoshiteru Hidaka, Jinhyuk Choi",
    maintainer = "Lingyun Yang",
    maintainer_email = "lyyang@bnl.gov",
    url = 'http://code.nsls2.bnl.gov/hg/ap/hla',
    )

