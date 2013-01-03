from setuptools import setup, find_packages
import os


setup(
    name = "aphla",
    version = "0.7.3",
    #packages = ['aphla', 'aphla.lib.mpfit', 'aphla.gui', 'aphla.gui.Qt4Designer_files', 
    #            'aphla.gui.TunerUtils', 'aphla.gui.PlotterUtils', 'aphla.machines'],
    #package_dir = {'aphla': 'lib', 'aphla.mpfit': 'lib/mpfit',
    #%               'aphla.gui': 'gui', 'aphla.machines': 'machines'},
    packages = find_packages(exclude=['tests']),
    include_package_data = True,
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
            'aporbit = aphla.gui.orbit:main',
            'apbba = aphla.gui.apbba:main',
            'aplauncher = aphla.gui.aplauncher:main',
            'apcurrentmonitor = aphla.gui.apcurrentmonitor:main',
            'apchx = aphla.gui.channelexplorer:main'
            ]
        },
    description = "Accelerator control and experiment toolkit",
    author = "Lingyun Yang, Yoshiteru Hidaka, Jinhyuk Choi",
    maintainer = "Lingyun Yang",
    maintainer_email = "lyyang@bnl.gov",
    url = 'http://code.nsls2.bnl.gov/hg/ap/hla',
    )

